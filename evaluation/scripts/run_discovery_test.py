#!/usr/bin/env python3
"""
Discovery Test for Recent Job Changers

Tests the FULL discovery → enrichment → verification pipeline using people_all_dedup.csv:

1. DISCOVER LinkedIn URL using multiple methods:
   - Serper OSINT (Google search "{name} {company} site:linkedin.com")
   - Scrapin match_person (API-based matching)

2. ENRICH found URLs with all 3 providers:
   - RapidAPI
   - Scrapin
   - LeadMagic

3. VERIFY enriched data matches CSV ground truth:
   - Does enriched company match expected company?
   - Does name match?
   - Is person currently employed there?

The CSV contains recent job changers (decision-makers with role_duration <= 11 months),
which provides a good stress test since these are NEW positions that may not be
indexed yet in all databases.

Usage:
    python -m evaluation.scripts.run_discovery_test \
        --csv people_all_dedup.csv \
        --sample 100
"""

import argparse
import asyncio
import csv
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evaluation.harness.pipeline_tester import (
    PipelineTester,
    EnrichmentResult,
    VerificationResult,
    LinkedInConnection,
)

# Import Serper OSINT
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "contact-finder"))
from modules.discovery.serper_osint import SerperOsint, OsintResult


@dataclass
class JobChanger:
    """Ground truth from people_all_dedup.csv"""
    name: str
    title: str
    company: str
    location: str | None = None
    role_duration_months: int | None = None
    connection_degree: str | None = None


@dataclass
class DiscoveryMethodResult:
    """Result from a single discovery method"""
    method: str  # "serper" or "scrapin"
    success: bool = False
    linkedin_url: str | None = None
    confidence: float = 0.0
    error: str | None = None
    latency_ms: int = 0


@dataclass
class DiscoveryResult:
    """Result of testing one job changer"""
    ground_truth: JobChanger

    # Discovery from each method
    serper_discovery: DiscoveryMethodResult | None = None
    scrapin_discovery: DiscoveryMethodResult | None = None

    # Best discovered URL (from either method)
    discovered_url: str | None = None
    discovery_method: str | None = None  # Which method found the URL

    # Enrichment results from each source
    enrichments: dict[str, EnrichmentResult] = field(default_factory=dict)

    # Verification
    verification: VerificationResult | None = None

    # Summary metrics
    name_match: bool = False
    company_match: bool = False
    title_match: bool = False

    # Timing
    total_latency_ms: int = 0


def load_job_changers(csv_path: str, sample_size: int | None = None) -> list[JobChanger]:
    """Load job changers from CSV"""
    changers = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row.get('name', '').strip()
            if not name:
                continue

            role_duration = row.get('role_duration_months', '')
            try:
                role_months = int(role_duration) if role_duration else None
            except ValueError:
                role_months = None

            changers.append(JobChanger(
                name=name,
                title=row.get('title', '').strip(),
                company=row.get('company', '').strip(),
                location=row.get('location_full', '').strip() or None,
                role_duration_months=role_months,
                connection_degree=row.get('connection_degree', '').strip() or None,
            ))

    # Sample if requested
    if sample_size and sample_size < len(changers):
        import random
        changers = random.sample(changers, sample_size)

    return changers


def split_name(full_name: str) -> tuple[str, str | None]:
    """Split full name into first and last name"""
    parts = full_name.strip().split()
    if len(parts) == 0:
        return "", None
    elif len(parts) == 1:
        return parts[0], None
    else:
        return parts[0], " ".join(parts[1:])


def fuzzy_match(str1: str | None, str2: str | None) -> bool:
    """Simple fuzzy string matching"""
    if not str1 or not str2:
        return False

    s1 = str1.lower().strip()
    s2 = str2.lower().strip()

    if s1 == s2:
        return True

    # Check substring
    if s1 in s2 or s2 in s1:
        return True

    # Word overlap
    words1 = set(s1.split())
    words2 = set(s2.split())
    if words1 and words2:
        overlap = len(words1 & words2) / max(len(words1), len(words2))
        if overlap >= 0.6:
            return True

    return False


async def discover_with_serper(
    serper: SerperOsint,
    name: str,
    company: str,
) -> DiscoveryMethodResult:
    """Try to find LinkedIn URL using Serper OSINT"""
    import time
    start = time.time()
    result = DiscoveryMethodResult(method="serper")

    try:
        osint_result = await serper.find_person_linkedin(name=name, company=company)

        if osint_result.linkedin_url:
            result.success = True
            result.linkedin_url = osint_result.linkedin_url
            result.confidence = osint_result.confidence
        else:
            result.error = "No LinkedIn URL found"

    except Exception as e:
        result.error = str(e)

    result.latency_ms = int((time.time() - start) * 1000)
    return result


async def discover_with_scrapin(
    tester: PipelineTester,
    first_name: str,
    last_name: str | None,
    company: str,
) -> DiscoveryMethodResult:
    """Try to find LinkedIn URL using Scrapin match_person"""
    import time
    start = time.time()
    result = DiscoveryMethodResult(method="scrapin")

    try:
        scrapin = await tester._get_scrapin()
        match_result = await scrapin.match_person(
            first_name=first_name,
            last_name=last_name,
            company_name=company,
        )

        if match_result and match_result.linkedin_url:
            result.success = True
            result.linkedin_url = match_result.linkedin_url
            result.confidence = 0.85  # Scrapin match has good confidence
        else:
            result.error = "No match found"

    except Exception as e:
        result.error = str(e)

    result.latency_ms = int((time.time() - start) * 1000)
    return result


async def test_job_changer(
    changer: JobChanger,
    tester: PipelineTester,
    serper: SerperOsint,
    sources: list[str],
    discovery_methods: list[str],
) -> DiscoveryResult:
    """Test discovery and enrichment for one job changer"""
    import time
    start_time = time.time()
    result = DiscoveryResult(ground_truth=changer)

    first_name, last_name = split_name(changer.name)

    # Step 1: Discovery - Find LinkedIn URL using multiple methods
    discovery_tasks = []

    if "serper" in discovery_methods:
        discovery_tasks.append(
            ("serper", discover_with_serper(serper, changer.name, changer.company))
        )

    if "scrapin" in discovery_methods:
        discovery_tasks.append(
            ("scrapin", discover_with_scrapin(tester, first_name, last_name, changer.company))
        )

    # Run discovery in parallel
    discovery_results = await asyncio.gather(*[t[1] for t in discovery_tasks], return_exceptions=True)

    for i, (method, _) in enumerate(discovery_tasks):
        res = discovery_results[i]
        if isinstance(res, Exception):
            res = DiscoveryMethodResult(method=method, error=str(res))

        if method == "serper":
            result.serper_discovery = res
        elif method == "scrapin":
            result.scrapin_discovery = res

        # Track best discovered URL
        if res.success and not result.discovered_url:
            result.discovered_url = res.linkedin_url
            result.discovery_method = method

    # Step 2: Enrichment (if discovered)
    if result.discovered_url:
        # Create a fake LinkedInConnection for the tester
        connection = LinkedInConnection(
            first_name=first_name,
            last_name=last_name or '',
            full_name=changer.name,
            company=changer.company,
            title=changer.title,
            linkedin_url=result.discovered_url,
        )

        # Test with all sources
        test_result = await tester.test_connection(connection, sources=sources, verify=True)

        result.enrichments = test_result.enrichments
        result.verification = test_result.verification

        # Check if enriched data matches ground truth
        for source, enrichment in result.enrichments.items():
            if enrichment.success:
                if fuzzy_match(enrichment.name, changer.name):
                    result.name_match = True
                if fuzzy_match(enrichment.company, changer.company):
                    result.company_match = True
                if fuzzy_match(enrichment.title, changer.title):
                    result.title_match = True

    result.total_latency_ms = int((time.time() - start_time) * 1000)
    return result


async def run_discovery_test(
    changers: list[JobChanger],
    sources: list[str],
    discovery_methods: list[str],
    concurrency: int = 2,
    delay: float = 1.5,
    progress_callback=None,
) -> list[DiscoveryResult]:
    """Run discovery test on all job changers"""
    tester = PipelineTester()
    serper = SerperOsint()
    results = []
    semaphore = asyncio.Semaphore(concurrency)

    async def process_one(idx: int, changer: JobChanger) -> DiscoveryResult:
        async with semaphore:
            result = await test_job_changer(changer, tester, serper, sources, discovery_methods)

            if progress_callback:
                progress_callback(idx + 1, len(changers), result)

            await asyncio.sleep(delay)
            return result

    try:
        tasks = [process_one(i, c) for i, c in enumerate(changers)]
        results = await asyncio.gather(*tasks)
    finally:
        await tester.close()

    return results


def generate_discovery_report(results: list[DiscoveryResult]) -> str:
    """Generate markdown report from discovery test results"""
    total = len(results)
    if total == 0:
        return "# Discovery Test Report\n\nNo results to report."

    # Discovery metrics by method
    serper_tried = sum(1 for r in results if r.serper_discovery)
    serper_found = sum(1 for r in results if r.serper_discovery and r.serper_discovery.success)
    scrapin_tried = sum(1 for r in results if r.scrapin_discovery)
    scrapin_found = sum(1 for r in results if r.scrapin_discovery and r.scrapin_discovery.success)

    # Combined discovery
    any_discovered = sum(1 for r in results if r.discovered_url)
    discovered_by_serper = sum(1 for r in results if r.discovery_method == "serper")
    discovered_by_scrapin = sum(1 for r in results if r.discovery_method == "scrapin")

    # Both found same URL
    both_found = sum(1 for r in results
                    if r.serper_discovery and r.scrapin_discovery
                    and r.serper_discovery.success and r.scrapin_discovery.success)

    # Enrichment metrics (only for discovered)
    discovered_results = [r for r in results if r.discovered_url]

    rapidapi_success = sum(1 for r in discovered_results
                          if r.enrichments.get('rapidapi', EnrichmentResult(source='', success=False)).success)
    scrapin_success = sum(1 for r in discovered_results
                         if r.enrichments.get('scrapin', EnrichmentResult(source='', success=False)).success)
    leadmagic_success = sum(1 for r in discovered_results
                           if r.enrichments.get('leadmagic', EnrichmentResult(source='', success=False)).success)

    # Match metrics
    name_match = sum(1 for r in discovered_results if r.name_match)
    company_match = sum(1 for r in discovered_results if r.company_match)
    title_match = sum(1 for r in discovered_results if r.title_match)

    # Verification
    verified = [r for r in discovered_results if r.verification]
    same_person = sum(1 for r in verified if r.verification.is_same_person)
    currently_employed = sum(1 for r in verified if r.verification.currently_employed)

    # Average latencies
    serper_latencies = [r.serper_discovery.latency_ms for r in results if r.serper_discovery]
    scrapin_latencies = [r.scrapin_discovery.latency_ms for r in results if r.scrapin_discovery]
    avg_serper = sum(serper_latencies) / len(serper_latencies) if serper_latencies else 0
    avg_scrapin = sum(scrapin_latencies) / len(scrapin_latencies) if scrapin_latencies else 0
    avg_total = sum(r.total_latency_ms for r in results) / total if total > 0 else 0

    n_disc = len(discovered_results) if discovered_results else 1  # Avoid division by zero

    report = f"""# Discovery Test Report - Recent Job Changers

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Discovery Summary

| Metric | Value | Percentage |
|--------|-------|------------|
| Total Tested | {total} | - |
| Any LinkedIn URL Found | {any_discovered} | {any_discovered/total*100:.1f}% |

## Discovery Method Comparison

| Method | Tried | Found | Success Rate | Avg Latency |
|--------|-------|-------|--------------|-------------|
| Serper OSINT | {serper_tried} | {serper_found} | {serper_found/serper_tried*100:.1f}% | {avg_serper:.0f}ms |
| Scrapin Match | {scrapin_tried} | {scrapin_found} | {scrapin_found/scrapin_tried*100:.1f}% | {avg_scrapin:.0f}ms |
| Both Found | - | {both_found} | {both_found/total*100:.1f}% | - |

**First Discovery Method Used:**
- Serper found first: {discovered_by_serper} ({discovered_by_serper/any_discovered*100:.1f}% of discovered)
- Scrapin found first: {discovered_by_scrapin} ({discovered_by_scrapin/any_discovered*100:.1f}% of discovered)

## Enrichment Results (of {any_discovered} discovered)

| Provider | Success | Percentage |
|----------|---------|------------|
| RapidAPI | {rapidapi_success} | {rapidapi_success/n_disc*100:.1f}% |
| Scrapin | {scrapin_success} | {scrapin_success/n_disc*100:.1f}% |
| LeadMagic | {leadmagic_success} | {leadmagic_success/n_disc*100:.1f}% |

## Ground Truth Matching (of {any_discovered} discovered)

| Metric | Value | Percentage |
|--------|-------|------------|
| Name Matches | {name_match} | {name_match/n_disc*100:.1f}% |
| Company Matches | {company_match} | {company_match/n_disc*100:.1f}% |
| Title Matches | {title_match} | {title_match/n_disc*100:.1f}% |

## Verification Results

| Metric | Value | Percentage |
|--------|-------|------------|
| Same Person | {same_person} | {same_person/n_disc*100:.1f}% |
| Currently Employed | {currently_employed} | {currently_employed/n_disc*100:.1f}% |

## Performance

- Average Total Latency: {avg_total:.0f}ms
- Average Serper Latency: {avg_serper:.0f}ms
- Average Scrapin Latency: {avg_scrapin:.0f}ms

## Sample Results (first 15)

"""

    # Add sample results
    for i, r in enumerate(results[:15]):
        gt = r.ground_truth
        report += f"""
### {i+1}. {gt.name}
- **Expected**: {gt.title} at {gt.company}
- **Role Duration**: {gt.role_duration_months} months
"""
        # Discovery results
        if r.serper_discovery:
            d = r.serper_discovery
            status = "FOUND" if d.success else f"NOT FOUND ({d.error})"
            report += f"- **Serper**: {status}"
            if d.success:
                report += f" (confidence: {d.confidence:.0%})"
            report += "\n"

        if r.scrapin_discovery:
            d = r.scrapin_discovery
            status = "FOUND" if d.success else f"NOT FOUND ({d.error})"
            report += f"- **Scrapin Match**: {status}\n"

        if r.discovered_url:
            report += f"- **Discovered URL**: {r.discovered_url} (via {r.discovery_method})\n"

            for source, enrichment in r.enrichments.items():
                if enrichment.success:
                    report += f"- **{source}**: {enrichment.name} | {enrichment.title} | {enrichment.company}\n"
                else:
                    report += f"- **{source}**: FAILED - {enrichment.error}\n"

            if r.verification:
                v = r.verification
                report += f"- **Verification**: Same person: {v.is_same_person}, Currently employed: {v.currently_employed}\n"
        else:
            report += "- **Discovery Failed**: No LinkedIn URL found\n"

    return report


def progress_callback(current: int, total: int, result: DiscoveryResult):
    """Print progress during test run"""
    gt = result.ground_truth

    status_parts = []

    # Discovery status
    if result.serper_discovery:
        status_parts.append(f"Serper: {'OK' if result.serper_discovery.success else 'MISS'}")
    if result.scrapin_discovery:
        status_parts.append(f"Scrapin: {'OK' if result.scrapin_discovery.success else 'MISS'}")

    if result.discovered_url:
        # Enrichment status
        for source, enrichment in result.enrichments.items():
            if enrichment.success:
                status_parts.append(f"{source}: OK")
            else:
                status_parts.append(f"{source}: FAIL")

        if result.verification:
            v = result.verification
            if v.is_same_person and v.currently_employed:
                status_parts.append("VERIFIED")
            elif v.is_same_person:
                status_parts.append("NOT EMPLOYED")
            else:
                status_parts.append("MISMATCH")
    else:
        status_parts.append("NOT FOUND")

    status = " | ".join(status_parts)
    print(f"[{current}/{total}] {gt.name[:30]:<30} | {status}")


async def main():
    parser = argparse.ArgumentParser(description="Run Discovery Test on Job Changers CSV")
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to job changers CSV (e.g., people_all_dedup.csv)"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=50,
        help="Number of records to test (default: 50)"
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        default=["rapidapi", "scrapin", "leadmagic"],
        help="Enrichment sources to test (default: rapidapi scrapin leadmagic)"
    )
    parser.add_argument(
        "--discovery-methods",
        nargs="+",
        default=["serper", "scrapin"],
        help="Discovery methods to use (default: serper scrapin)"
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
        help="Delay between requests (default: 1.5s)"
    )
    parser.add_argument(
        "--output-dir",
        default="evaluation/data/pipeline_results",
        help="Output directory for reports"
    )

    args = parser.parse_args()

    # Check API keys
    missing_keys = []
    if "serper" in args.discovery_methods and not os.environ.get("SERPER_API_KEY"):
        missing_keys.append("SERPER_API_KEY (required for Serper discovery)")
    if "scrapin" in args.discovery_methods and not os.environ.get("SCRAPIN_API_KEY"):
        missing_keys.append("SCRAPIN_API_KEY (required for Scrapin discovery)")
    if "rapidapi" in args.sources and not os.environ.get("RAPIDAPI_KEY"):
        missing_keys.append("RAPIDAPI_KEY")
    if "leadmagic" in args.sources and not os.environ.get("LEADMAGIC_API_KEY"):
        missing_keys.append("LEADMAGIC_API_KEY")

    if missing_keys:
        print(f"Error: Missing environment variables: {', '.join(missing_keys)}")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load job changers
    print(f"\nLoading job changers from: {args.csv}")
    changers = load_job_changers(args.csv, sample_size=args.sample)
    print(f"Loaded {len(changers)} job changers (sample: {args.sample})")

    # Show sample
    print("\nSample records:")
    for changer in changers[:3]:
        print(f"  - {changer.name} | {changer.title} at {changer.company} ({changer.role_duration_months}mo)")

    print(f"\nDiscovery Methods: {', '.join(args.discovery_methods)}")
    print(f"Enrichment Sources: {', '.join(args.sources)}")
    print(f"Concurrency: {args.concurrency}")
    print(f"Delay: {args.delay}s")

    print("\n" + "=" * 70)
    print("STARTING DISCOVERY TEST")
    print("=" * 70 + "\n")

    # Run tests
    start_time = datetime.now()

    results = await run_discovery_test(
        changers,
        sources=args.sources,
        discovery_methods=args.discovery_methods,
        concurrency=args.concurrency,
        delay=args.delay,
        progress_callback=progress_callback,
    )

    elapsed = (datetime.now() - start_time).total_seconds()

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print(f"\nTotal time: {elapsed:.1f}s ({elapsed/len(results):.1f}s per record)")

    # Generate report
    report = generate_discovery_report(results)
    print("\n" + report)

    # Save outputs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_path = output_dir / f"discovery_test_{timestamp}.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved: {report_path}")

    # Save JSON
    json_path = output_dir / f"discovery_test_{timestamp}.json"
    json_results = []
    for r in results:
        json_results.append({
            "ground_truth": {
                "name": r.ground_truth.name,
                "title": r.ground_truth.title,
                "company": r.ground_truth.company,
                "role_duration_months": r.ground_truth.role_duration_months,
            },
            "discovery": {
                "serper": {
                    "success": r.serper_discovery.success if r.serper_discovery else None,
                    "url": r.serper_discovery.linkedin_url if r.serper_discovery else None,
                    "confidence": r.serper_discovery.confidence if r.serper_discovery else None,
                    "error": r.serper_discovery.error if r.serper_discovery else None,
                    "latency_ms": r.serper_discovery.latency_ms if r.serper_discovery else None,
                } if r.serper_discovery else None,
                "scrapin": {
                    "success": r.scrapin_discovery.success if r.scrapin_discovery else None,
                    "url": r.scrapin_discovery.linkedin_url if r.scrapin_discovery else None,
                    "error": r.scrapin_discovery.error if r.scrapin_discovery else None,
                    "latency_ms": r.scrapin_discovery.latency_ms if r.scrapin_discovery else None,
                } if r.scrapin_discovery else None,
                "best_url": r.discovered_url,
                "best_method": r.discovery_method,
            },
            "enrichments": {
                source: {
                    "success": e.success,
                    "name": e.name,
                    "title": e.title,
                    "company": e.company,
                    "error": e.error,
                }
                for source, e in r.enrichments.items()
            },
            "matches": {
                "name": r.name_match,
                "company": r.company_match,
                "title": r.title_match,
            },
            "verification": {
                "is_same_person": r.verification.is_same_person,
                "currently_employed": r.verification.currently_employed,
                "confidence": r.verification.confidence,
            } if r.verification else None,
            "total_latency_ms": r.total_latency_ms,
        })

    with open(json_path, 'w') as f:
        json.dump(json_results, f, indent=2)
    print(f"JSON results saved: {json_path}")


if __name__ == "__main__":
    asyncio.run(main())
