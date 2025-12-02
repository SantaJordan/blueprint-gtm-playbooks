#!/usr/bin/env python3
"""
Evaluation Framework CLI

Unified command-line interface for building ground truth,
running evaluations, and generating reports.

Usage:
    python -m evaluation.cli build-truth --companies companies.csv
    python -m evaluation.cli eval-blitz --companies truth.parquet --contacts contacts.parquet
    python -m evaluation.cli eval-domain --companies truth.parquet
    python -m evaluation.cli cache-stats
"""

import argparse
import asyncio
import sys
import yaml
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str | None = None) -> dict:
    """Load configuration from YAML file or environment"""
    import os

    config = {
        "ocean_key": os.environ.get("OCEAN_API_KEY"),
        "scrapin_key": os.environ.get("SCRAPIN_API_KEY"),
        "blitz_key": os.environ.get("BLITZ_API_KEY"),
        "cache_path": "./evaluation/data/cache.db",
    }

    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            yaml_config = yaml.safe_load(f)

        # Merge with defaults
        if yaml_config.get("api_keys"):
            config["ocean_key"] = yaml_config["api_keys"].get("ocean") or config["ocean_key"]
            config["scrapin_key"] = yaml_config["api_keys"].get("scrapin") or config["scrapin_key"]
            config["blitz_key"] = yaml_config["api_keys"].get("blitz") or config["blitz_key"]

        if yaml_config.get("cache_path"):
            config["cache_path"] = yaml_config["cache_path"]

    return config


async def cmd_build_truth(args, config):
    """Build ground truth dataset from multiple sources"""
    from evaluation.harness.ground_truth_builder import GroundTruthBuilder

    builder = GroundTruthBuilder(
        ocean_key=config.get("ocean_key"),
        scrapin_key=config.get("scrapin_key"),
        blitz_key=config.get("blitz_key"),
        cache_path=config.get("cache_path")
    )

    # Load companies
    if not Path(args.companies).exists():
        logger.error(f"Companies file not found: {args.companies}")
        return 1

    builder.load_companies(args.companies)

    # Build truth
    logger.info("Building Tier 2 (Silver) ground truth...")
    await builder.build_tier2_truth(
        use_ocean=not args.no_ocean,
        use_scrapin=not args.no_scrapin
    )

    # Export conflicts for review
    conflicts = builder.get_conflicts()
    if conflicts:
        review_path = args.output.replace(".parquet", "_review.csv")
        builder.export_for_review(review_path)
        logger.info(f"Exported {len(conflicts)} conflicts for manual review")

    # Save truth
    builder.save_truth(args.output)

    # Assign splits if requested
    if args.assign_splits:
        splits = builder.assign_splits()
        splits_path = args.output.replace(".parquet", "_splits.yaml")
        builder.save_splits(splits, splits_path)
        logger.info(f"Split assignments: {splits['counts']}")

    return 0


async def cmd_eval_blitz(args, config):
    """Evaluate Blitz waterfall-icp against ground truth"""
    from evaluation.harness.blitz_evaluator import BlitzEvaluator

    blitz_key = args.api_key or config.get("blitz_key")
    if not blitz_key:
        logger.error("Blitz API key required. Set BLITZ_API_KEY or use --api-key")
        return 1

    evaluator = BlitzEvaluator(
        api_key=blitz_key,
        cache_path=config.get("cache_path")
    )

    try:
        # Load ground truth
        evaluator.load_ground_truth(
            args.companies,
            args.contacts
        )

        # Parse personas
        personas = args.personas.split(",") if args.personas else None

        # Run evaluation
        summary = await evaluator.evaluate_waterfall_icp(
            persona_types=personas,
            use_realtime=args.realtime,
            skip_cache=args.skip_cache
        )

        # Generate report
        evaluator.generate_report(summary, args.output)

        # Print summary
        print("\n" + "=" * 50)
        print("BLITZ EVALUATION SUMMARY")
        print("=" * 50)
        print(f"Companies tested: {summary.total_companies}")
        print(f"Persona Hit Rate: {summary.persona_hit_rate*100:.1f}%")
        print(f"Person Match Rate: {summary.person_match_rate*100:.1f}%")
        print(f"Email Match Rate: {summary.email_match_rate*100:.1f}%")
        print(f"Total Credits Used: {summary.total_credits:.1f}")
        print(f"\nReport saved to: {args.output}")

    finally:
        await evaluator.close()

    return 0


async def cmd_eval_domain(args, config):
    """Evaluate domain resolver against ground truth"""
    from evaluation.harness.metrics import calculate_domain_metrics
    import pandas as pd

    # Load ground truth
    if args.truth.endswith(".parquet"):
        df_truth = pd.read_parquet(args.truth)
    else:
        df_truth = pd.read_csv(args.truth)

    # Load results (if provided) or run domain resolver
    if args.results:
        if args.results.endswith(".parquet"):
            df_results = pd.read_parquet(args.results)
        else:
            df_results = pd.read_csv(args.results)
    else:
        # TODO: Run domain resolver on truth companies
        logger.error("Results file required. Use --results or implement live evaluation.")
        return 1

    # Calculate metrics
    metrics = calculate_domain_metrics(df_results, df_truth)

    # Print results
    print("\n" + "=" * 50)
    print("DOMAIN RESOLVER EVALUATION")
    print("=" * 50)
    print(f"Total Companies: {metrics.total}")
    print(f"Accuracy: {metrics.accuracy*100:.1f}%")
    print(f"Precision: {metrics.precision*100:.1f}%")
    print(f"Recall: {metrics.recall*100:.1f}%")
    print(f"F1 Score: {metrics.f1_score*100:.1f}%")
    print(f"Coverage: {metrics.coverage*100:.1f}%")
    print(f"\nHigh Confidence (≥85): {metrics.high_conf_accuracy*100:.1f}% ({metrics.high_conf_count} companies)")
    print(f"Calibration ECE: {metrics.calibration_ece:.3f}")

    if metrics.by_source:
        print("\nBy Source:")
        for source, stats in metrics.by_source.items():
            print(f"  {source}: {stats['accuracy']*100:.1f}% ({stats['correct']}/{stats['count']})")

    # Save detailed metrics if requested
    if args.output:
        import json
        with open(args.output, "w") as f:
            json.dump(metrics.to_dict(), f, indent=2)
        logger.info(f"Saved detailed metrics to: {args.output}")

    return 0


def cmd_cache_stats(args, config):
    """Show cache statistics"""
    from evaluation.harness.cache import EvaluationCache

    cache = EvaluationCache(config.get("cache_path"))
    stats = cache.stats()

    print("\n" + "=" * 50)
    print("CACHE STATISTICS")
    print("=" * 50)
    print(f"Total Entries: {stats['total_entries']}")
    print(f"Expired Entries: {stats['expired_entries']}")
    print(f"Database Size: {stats['db_size_mb']:.2f} MB")

    if stats['by_api']:
        print("\nBy API:")
        for api, api_stats in stats['by_api'].items():
            print(f"  {api}: {api_stats['count']} entries, {api_stats['total_hits']} total hits")

    if args.clear_expired:
        deleted = cache.clear_expired()
        print(f"\nCleared {deleted} expired entries")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Evaluation Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--config", "-c",
        default="./evaluation/config.yaml",
        help="Path to configuration file"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # build-truth command
    build_parser = subparsers.add_parser(
        "build-truth",
        help="Build ground truth dataset from multiple sources"
    )
    build_parser.add_argument(
        "--companies", "-i",
        required=True,
        help="Path to input companies CSV"
    )
    build_parser.add_argument(
        "--output", "-o",
        default="./evaluation/data/companies_truth.parquet",
        help="Output path for ground truth"
    )
    build_parser.add_argument(
        "--no-ocean",
        action="store_true",
        help="Skip Ocean.io enrichment"
    )
    build_parser.add_argument(
        "--no-scrapin",
        action="store_true",
        help="Skip Scrapin enrichment"
    )
    build_parser.add_argument(
        "--assign-splits",
        action="store_true",
        help="Assign cal/val/blind splits"
    )

    # eval-blitz command
    blitz_parser = subparsers.add_parser(
        "eval-blitz",
        help="Evaluate Blitz waterfall-icp"
    )
    blitz_parser.add_argument(
        "--companies", "-i",
        required=True,
        help="Path to companies ground truth"
    )
    blitz_parser.add_argument(
        "--contacts",
        help="Path to contacts ground truth"
    )
    blitz_parser.add_argument(
        "--output", "-o",
        default="./evaluation/runs/blitz_eval_report.md",
        help="Output path for report"
    )
    blitz_parser.add_argument(
        "--api-key",
        help="Blitz API key (overrides env/config)"
    )
    blitz_parser.add_argument(
        "--personas",
        help="Comma-separated list of personas to test"
    )
    blitz_parser.add_argument(
        "--realtime",
        action="store_true",
        help="Use real-time mode (3 credits/result)"
    )
    blitz_parser.add_argument(
        "--skip-cache",
        action="store_true",
        help="Skip cache and always call API"
    )

    # eval-domain command
    domain_parser = subparsers.add_parser(
        "eval-domain",
        help="Evaluate domain resolver"
    )
    domain_parser.add_argument(
        "--truth", "-t",
        required=True,
        help="Path to ground truth file"
    )
    domain_parser.add_argument(
        "--results", "-r",
        help="Path to domain resolver results"
    )
    domain_parser.add_argument(
        "--output", "-o",
        help="Path to save detailed metrics JSON"
    )

    # cache-stats command
    cache_parser = subparsers.add_parser(
        "cache-stats",
        help="Show cache statistics"
    )
    cache_parser.add_argument(
        "--clear-expired",
        action="store_true",
        help="Clear expired entries"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Load config
    config = load_config(args.config)

    # Run command
    if args.command == "build-truth":
        return asyncio.run(cmd_build_truth(args, config))
    elif args.command == "eval-blitz":
        return asyncio.run(cmd_eval_blitz(args, config))
    elif args.command == "eval-domain":
        return asyncio.run(cmd_eval_domain(args, config))
    elif args.command == "cache-stats":
        return cmd_cache_stats(args, config)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
