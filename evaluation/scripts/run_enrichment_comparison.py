#!/usr/bin/env python3
"""
Run Enrichment Provider Comparison

Compares LinkedIn profile enrichment from multiple sources:
- RapidAPI LinkedIn Fresh Data
- Scrapin LinkedIn API

Usage:
    python -m evaluation.scripts.run_enrichment_comparison \
        --linkedin-export Basic_LinkedInDataExport_11-29-2025.zip.zip \
        --all

    # Quick test with sample
    python -m evaluation.scripts.run_enrichment_comparison \
        --linkedin-export Basic_LinkedInDataExport_11-29-2025.zip.zip \
        --sample 20
"""

import asyncio
import argparse
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from evaluation.harness.company_people_qa import CompanyPeopleQATester


def main():
    parser = argparse.ArgumentParser(
        description="Compare LinkedIn enrichment providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Test all connections
    python -m evaluation.scripts.run_enrichment_comparison \\
        --linkedin-export Basic_LinkedInDataExport_11-29-2025.zip.zip \\
        --all

    # Quick sample test
    python -m evaluation.scripts.run_enrichment_comparison \\
        --linkedin-export Basic_LinkedInDataExport_11-29-2025.zip.zip \\
        --sample 50

Environment Variables:
    RAPIDAPI_KEY      - RapidAPI key for LinkedIn Fresh Data
    SCRAPIN_API_KEY   - Scrapin API key
        """
    )

    parser.add_argument(
        "--linkedin-export",
        required=True,
        help="Path to LinkedIn export ZIP file"
    )
    parser.add_argument(
        "--sample",
        type=int,
        help="Number of connections to sample (default: 100)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test ALL connections (overrides --sample)"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="Max concurrent API requests (default: 2)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Delay between requests in seconds (default: 1.5)"
    )
    parser.add_argument(
        "--output-dir",
        default="evaluation/data/qa_results",
        help="Output directory for reports"
    )
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Skip confirmation prompt (for automated runs)"
    )

    args = parser.parse_args()

    # Get API keys
    rapidapi_key = os.environ.get("RAPIDAPI_KEY")
    scrapin_key = os.environ.get("SCRAPIN_API_KEY")

    if not rapidapi_key and not scrapin_key:
        print("ERROR: Set at least one of RAPIDAPI_KEY or SCRAPIN_API_KEY")
        print("\nExample:")
        print('  export RAPIDAPI_KEY="your-key"')
        print('  export SCRAPIN_API_KEY="your-key"')
        sys.exit(1)

    print("=" * 70)
    print("ENRICHMENT PROVIDER COMPARISON")
    print("=" * 70)
    print(f"LinkedIn Export: {args.linkedin_export}")
    print(f"RapidAPI: {'configured' if rapidapi_key else 'NOT configured'}")
    print(f"Scrapin: {'configured' if scrapin_key else 'NOT configured'}")
    print("=" * 70)

    asyncio.run(run_comparison(args, rapidapi_key, scrapin_key))


async def run_comparison(args, rapidapi_key, scrapin_key):
    tester = CompanyPeopleQATester(
        rapidapi_key=rapidapi_key,
        scrapin_key=scrapin_key,
        output_dir=args.output_dir
    )

    try:
        # Load connections
        print(f"\nLoading LinkedIn export...")
        connections = tester.load_linkedin_export(args.linkedin_export)
        print(f"Loaded {len(connections)} total connections")

        # Filter to those with LinkedIn URLs
        connections_with_url = [c for c in connections if c.linkedin_url]
        print(f"{len(connections_with_url)} have LinkedIn URLs")

        # Sample or use all
        if args.all:
            test_connections = connections_with_url
            print(f"Testing ALL {len(test_connections)} connections")
        else:
            sample_size = args.sample or 100
            if sample_size < len(connections_with_url):
                import random
                test_connections = random.sample(connections_with_url, sample_size)
                print(f"Sampled {len(test_connections)} connections")
            else:
                test_connections = connections_with_url

        if not test_connections:
            print("ERROR: No connections with LinkedIn URLs found")
            return

        # Estimate time and cost
        est_time_min = len(test_connections) * args.delay / 60
        print(f"\nEstimated time: ~{est_time_min:.1f} minutes")
        print(f"Concurrency: {args.concurrency}")
        print(f"Delay between requests: {args.delay}s")

        # Confirm
        if not args.no_confirm:
            input("\nPress Enter to start (Ctrl+C to cancel)...")

        # Progress tracking
        start_time = datetime.now()
        success_count = 0
        diff_count = 0

        def progress(current, total, result):
            nonlocal success_count, diff_count

            if result.enriched and result.enriched.sources_succeeded > 0:
                success_count += 1

            if result.has_differences():
                diff_count += 1

            # Build status line
            sources = result.enriched.get_sources_summary() if result.enriched else {}
            source_str = " ".join([
                f"R:{'ok' if sources.get('rapidapi') else 'x'}",
                f"S:{'ok' if sources.get('scrapin') else 'x'}"
            ])

            diff_marker = " [DIFF]" if result.has_differences() else ""

            elapsed = (datetime.now() - start_time).total_seconds()
            rate = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / rate if rate > 0 else 0

            print(f"[{current:4d}/{total}] {result.connection.name[:30]:30s} | {source_str}{diff_marker} | ETA: {eta/60:.1f}m")

        # Run test
        print("\n" + "-" * 70)
        print("Starting enrichment comparison...")
        print("-" * 70 + "\n")

        results = await tester.run_test(
            test_connections,
            concurrency=args.concurrency,
            delay_between=args.delay,
            progress_callback=progress
        )

        # Summary
        elapsed = (datetime.now() - start_time).total_seconds()

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total tested: {len(results)}")
        print(f"Successfully enriched: {success_count} ({success_count/len(results)*100:.1f}%)")
        print(f"With differences: {diff_count}")
        print(f"Time elapsed: {elapsed/60:.1f} minutes")

        # Per-source breakdown
        rapidapi_ok = sum(1 for r in results if r.enriched and r.enriched.rapidapi and r.enriched.rapidapi.success)
        scrapin_ok = sum(1 for r in results if r.enriched and r.enriched.scrapin and r.enriched.scrapin.success)

        print(f"\nPer-source success:")
        print(f"  RapidAPI: {rapidapi_ok}/{len(results)} ({rapidapi_ok/len(results)*100:.1f}%)")
        print(f"  Scrapin:  {scrapin_ok}/{len(results)} ({scrapin_ok/len(results)*100:.1f}%)")

        # Generate report
        report_path = tester.generate_report(results)
        print(f"\nReport saved to: {report_path}")

        # Show first few differences
        diffs = [r for r in results if r.has_differences()]
        if diffs:
            print(f"\nFirst 5 differences:")
            for r in diffs[:5]:
                print(f"\n  {r.connection.name}:")
                print(f"    Ground truth: {r.connection.title} @ {r.connection.company}")
                for source, data in r.sources_data.items():
                    print(f"    {source}: {data.get('title')} @ {data.get('company')}")

    finally:
        await tester.close()


if __name__ == "__main__":
    main()
