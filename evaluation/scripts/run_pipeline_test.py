#!/usr/bin/env python3
"""
Run Contact Discovery Pipeline Test

Tests the full contact discovery flow against LinkedIn connections as ground truth:
1. Multi-source enrichment (RapidAPI, Scrapin)
2. LLM verification (is this the right person? do they work there?)

Usage:
    # Quick test with 10 connections
    python -m evaluation.scripts.run_pipeline_test \
        --linkedin-export Basic_LinkedInDataExport_11-29-2025.zip \
        --sample 10

    # Full test with 1000 connections
    python -m evaluation.scripts.run_pipeline_test \
        --linkedin-export Basic_LinkedInDataExport_11-29-2025.zip \
        --sample 1000 \
        --verify

    # Specific sources only
    python -m evaluation.scripts.run_pipeline_test \
        --linkedin-export Basic_LinkedInDataExport_11-29-2025.zip \
        --sources rapidapi scrapin \
        --sample 100
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evaluation.harness.pipeline_tester import (
    PipelineTester,
    PipelineTestResult,
    generate_report,
)


def progress_callback(current: int, total: int, result: PipelineTestResult):
    """Print progress during test run"""
    gt = result.ground_truth
    status_parts = []

    for source, enrichment in result.enrichments.items():
        if enrichment.success:
            status_parts.append(f"{source}: OK")
        else:
            status_parts.append(f"{source}: FAIL")

    if result.verification:
        v = result.verification
        if v.is_same_person and v.currently_employed:
            status_parts.append("LLM: VERIFIED")
        elif v.is_same_person:
            status_parts.append("LLM: PERSON OK, NOT EMPLOYED")
        else:
            status_parts.append("LLM: MISMATCH")

    status = " | ".join(status_parts)
    print(f"[{current}/{total}] {gt.full_name[:30]:<30} | {status}")


async def main():
    parser = argparse.ArgumentParser(
        description="Run Contact Discovery Pipeline Test"
    )
    parser.add_argument(
        "--linkedin-export",
        required=True,
        help="Path to LinkedIn export ZIP file"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=10,
        help="Number of connections to test (default: 10)"
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        default=["rapidapi", "scrapin"],
        help="Enrichment sources to test (default: rapidapi scrapin)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        default=True,
        help="Run LLM verification (default: True)"
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip LLM verification"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="Max parallel requests (default: 2)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Delay between requests in seconds (default: 1.5)"
    )
    parser.add_argument(
        "--output-dir",
        default="evaluation/data/pipeline_results",
        help="Output directory for reports"
    )

    args = parser.parse_args()

    # Check API keys
    missing_keys = []
    if "rapidapi" in args.sources and not os.environ.get("RAPIDAPI_KEY"):
        missing_keys.append("RAPIDAPI_KEY")
    if "scrapin" in args.sources and not os.environ.get("SCRAPIN_API_KEY"):
        missing_keys.append("SCRAPIN_API_KEY")
    if "leadmagic" in args.sources and not os.environ.get("LEADMAGIC_API_KEY"):
        missing_keys.append("LEADMAGIC_API_KEY")
    if args.verify and not args.no_verify and not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set, using rule-based verification")

    if missing_keys:
        print(f"Error: Missing environment variables: {', '.join(missing_keys)}")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load connections
    print(f"\nLoading LinkedIn export: {args.linkedin_export}")
    tester = PipelineTester()

    try:
        connections = tester.load_linkedin_export(args.linkedin_export, sample_size=args.sample)
        print(f"Loaded {len(connections)} connections (sample: {args.sample})")

        # Show sample
        print("\nSample connections:")
        for conn in connections[:3]:
            print(f"  - {conn.full_name} | {conn.title} at {conn.company}")

        print(f"\nSources: {', '.join(args.sources)}")
        print(f"LLM Verification: {'Enabled' if args.verify and not args.no_verify else 'Disabled'}")
        print(f"Concurrency: {args.concurrency}")
        print(f"Delay: {args.delay}s")

        print("\n" + "=" * 70)
        print("STARTING PIPELINE TEST")
        print("=" * 70 + "\n")

        # Run tests
        start_time = datetime.now()

        results = await tester.run_batch(
            connections,
            sources=args.sources,
            verify=args.verify and not args.no_verify,
            concurrency=args.concurrency,
            delay=args.delay,
            progress_callback=progress_callback,
        )

        elapsed = (datetime.now() - start_time).total_seconds()

        print("\n" + "=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)
        print(f"\nTotal time: {elapsed:.1f}s ({elapsed/len(results):.1f}s per connection)")

        # Generate report
        report = generate_report(results)
        print("\n" + report)

        # Save outputs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save markdown report
        report_path = output_dir / f"pipeline_test_{timestamp}.md"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"\nReport saved: {report_path}")

        # Save JSON results
        json_path = output_dir / f"pipeline_test_{timestamp}.json"
        json_results = []
        for r in results:
            json_results.append({
                "ground_truth": {
                    "name": r.ground_truth.full_name,
                    "company": r.ground_truth.company,
                    "title": r.ground_truth.title,
                    "linkedin_url": r.ground_truth.linkedin_url,
                },
                "enrichments": {
                    source: {
                        "success": e.success,
                        "name": e.name,
                        "title": e.title,
                        "company": e.company,
                        "experiences": e.experiences[:3],
                        "error": e.error,
                    }
                    for source, e in r.enrichments.items()
                },
                "verification": {
                    "is_same_person": r.verification.is_same_person,
                    "currently_employed": r.verification.currently_employed,
                    "confidence": r.verification.confidence,
                    "reasoning": r.verification.reasoning,
                    "red_flags": r.verification.red_flags,
                } if r.verification else None,
                "sources_agree_on_name": r.sources_agree_on_name,
                "sources_agree_on_company": r.sources_agree_on_company,
                "any_source_found_data": r.any_source_found_data,
                "total_latency_ms": r.total_latency_ms,
            })

        with open(json_path, 'w') as f:
            json.dump(json_results, f, indent=2)
        print(f"JSON results saved: {json_path}")

    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
