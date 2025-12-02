#!/usr/bin/env python3
"""
Contact QA Test Runner

Compare enrichment APIs against LinkedIn connections export as ground truth.

Usage:
    # Full comparison on 100 contacts
    python -m evaluation.scripts.run_contact_qa \
        --linkedin-export ~/Downloads/Complete_LinkedInDataExport_11-28-2025.zip.zip \
        --scenarios person_lookup email_lookup \
        --apis rapidapi scrapin \
        --sample 100

    # Quick test with RapidAPI only
    python -m evaluation.scripts.run_contact_qa --sample 20 --apis rapidapi

    # Email lookup test (uses all contacts with email)
    python -m evaluation.scripts.run_contact_qa --scenarios email_lookup --apis rapidapi

Environment Variables:
    RAPIDAPI_KEY - RapidAPI key for realtime-linkedin-fresh-data
    SCRAPIN_API_KEY - Scrapin API key
    BLITZ_API_KEY - Blitz API key
    LEADMAGIC_API_KEY - LeadMagic API key
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "contact-finder"))

from harness.contact_qa_tester import ContactQATester

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def check_api_keys(apis: list[str]) -> list[str]:
    """Check which API keys are available"""
    key_map = {
        "rapidapi": "RAPIDAPI_KEY",
        "blitz": "BLITZ_API_KEY",
        "scrapin": "SCRAPIN_API_KEY",
        "leadmagic": "LEADMAGIC_API_KEY"
    }

    available = []
    missing = []

    for api in apis:
        env_var = key_map.get(api)
        if env_var and os.environ.get(env_var):
            available.append(api)
        else:
            missing.append(f"{api} ({env_var})")

    if missing:
        logger.warning(f"Missing API keys: {', '.join(missing)}")

    return available


async def main():
    parser = argparse.ArgumentParser(
        description="Contact QA Tester - Compare enrichment APIs against LinkedIn ground truth",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--linkedin-export",
        default=os.path.expanduser("~/Downloads/Complete_LinkedInDataExport_11-28-2025.zip.zip"),
        help="Path to LinkedIn data export zip file"
    )

    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=["person_lookup"],
        choices=["person_lookup", "email_lookup", "email_enrichment"],
        help="Test scenarios to run (email_enrichment: LinkedIn URL -> email verification)"
    )

    parser.add_argument(
        "--apis",
        nargs="+",
        default=["rapidapi"],
        choices=["rapidapi", "scrapin", "blitz", "leadmagic"],
        help="APIs to test"
    )

    parser.add_argument(
        "--sample", "-n",
        type=int,
        default=50,
        help="Number of contacts to test (per scenario)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling"
    )

    parser.add_argument(
        "--output", "-o",
        help="Output path for markdown report"
    )

    parser.add_argument(
        "--cache-path",
        default="./evaluation/data/cache.db",
        help="Path to cache database"
    )

    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable inline progress output"
    )

    args = parser.parse_args()

    # Check API keys
    available_apis = check_api_keys(args.apis)
    if not available_apis:
        logger.error("No API keys available. Set environment variables.")
        return 1

    # Initialize tester
    tester = ContactQATester(cache_path=args.cache_path)

    try:
        # Load ground truth
        logger.info(f"Loading LinkedIn export from {args.linkedin_export}")
        try:
            count = tester.load_linkedin_export(args.linkedin_export)
        except FileNotFoundError:
            logger.error(f"LinkedIn export not found: {args.linkedin_export}")
            return 1

        logger.info(f"Loaded {count} contacts ({len(tester.get_contacts_with_email())} with email)")
        logger.info("")

        # Progress callback
        progress_fn = None if args.no_progress else tester.print_progress

        # Store all results for report
        all_results = {}

        # Run each scenario
        for scenario in args.scenarios:
            logger.info(f"Running {scenario} scenario...")
            logger.info("")

            if scenario == "person_lookup":
                # Filter to APIs that support person lookup
                person_apis = [a for a in available_apis if a in ["rapidapi", "scrapin"]]
                if not person_apis:
                    logger.warning(f"No APIs available for person_lookup")
                    continue

                results = await tester.run_person_lookup_test(
                    apis=person_apis,
                    sample_size=args.sample,
                    seed=args.seed,
                    progress_callback=progress_fn
                )
                all_results["person_lookup"] = results
                tester.print_summary(results)

            elif scenario == "email_lookup":
                # Filter to APIs that support email lookup (email -> LinkedIn)
                email_apis = [a for a in available_apis if a in ["rapidapi"]]
                if not email_apis:
                    logger.warning(f"No APIs available for email_lookup")
                    continue

                results = await tester.run_email_lookup_test(
                    apis=email_apis,
                    sample_size=args.sample,
                    seed=args.seed,
                    progress_callback=progress_fn
                )
                all_results["email_lookup"] = results
                tester.print_summary(results)

            elif scenario == "email_enrichment":
                # Filter to APIs that support email enrichment (LinkedIn URL -> email)
                enrich_apis = [a for a in available_apis if a in ["blitz", "scrapin"]]
                if not enrich_apis:
                    logger.warning(f"No APIs available for email_enrichment (need blitz or scrapin)")
                    continue

                results = await tester.run_email_enrichment_test(
                    apis=enrich_apis,
                    sample_size=args.sample,
                    seed=args.seed,
                    progress_callback=progress_fn
                )
                all_results["email_enrichment"] = results
                tester.print_summary(results)

            logger.info("")

        # Generate report if requested
        if args.output:
            output_path = Path(args.output)
        else:
            # Default output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"./evaluation/data/qa_results/report_{timestamp}.md")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        tester.generate_report(all_results, output_path)
        logger.info(f"Report saved to {output_path}")

        return 0

    finally:
        await tester.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
