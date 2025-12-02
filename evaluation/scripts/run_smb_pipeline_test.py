#!/usr/bin/env python3
"""
SMB Pipeline Test - Full Contact Finder Evaluation

Runs the complete ContactFinder pipeline on SMB companies to evaluate:
- Discovery success rates (LinkedIn company, contact candidates)
- Enrichment success rates (Scrapin, Blitz, LeadMagic)
- LLM validation rates
- Cost per successful contact
- Per-vertical performance

Usage:
    python -m evaluation.scripts.run_smb_pipeline_test \
        --input evaluation/data/smb_sample_1400.json \
        --output evaluation/results/smb_pipeline_results.json \
        --concurrency 5 \
        --delay 0.5
"""

import argparse
import asyncio
import json
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "contact-finder"))

from contact_finder import ContactFinder, CompanyContactResult


@dataclass
class SMBTestResult:
    """Result for one SMB company test"""
    company_name: str
    domain: str
    vertical: str

    # Pipeline result
    success: bool = False
    stage_reached: str = "input"
    linkedin_company_url: str | None = None

    # Contact found
    contact_name: str | None = None
    contact_title: str | None = None
    contact_email: str | None = None
    contact_linkedin: str | None = None
    contact_confidence: float = 0.0
    contact_reasoning: str = ""
    contact_red_flags: list[str] = field(default_factory=list)

    # Sources that contributed
    contact_sources: list[str] = field(default_factory=list)

    # Metrics
    candidates_found: int = 0
    candidates_enriched: int = 0
    candidates_validated: int = 0
    processing_time_ms: float = 0.0
    cost_credits: float = 0.0

    # Errors
    errors: list[str] = field(default_factory=list)


@dataclass
class BatchMetrics:
    """Aggregated metrics for the batch"""
    total: int = 0
    successful: int = 0
    failed: int = 0

    # Stage success rates
    linkedin_company_found: int = 0
    candidates_found: int = 0
    candidates_enriched: int = 0
    candidates_validated: int = 0

    # By vertical
    by_vertical: dict = field(default_factory=dict)

    # Cost
    total_cost_credits: float = 0.0
    total_time_seconds: float = 0.0


def load_smb_sample(input_path: str) -> list[dict]:
    """Load SMB sample from JSON"""
    with open(input_path, 'r') as f:
        return json.load(f)


def convert_to_test_result(
    company: dict,
    result: CompanyContactResult
) -> SMBTestResult:
    """Convert ContactFinder result to test result"""
    test_result = SMBTestResult(
        company_name=company.get('company_name', ''),
        domain=company.get('domain', ''),
        vertical=company.get('vertical', 'unknown'),
        success=result.success,
        stage_reached=result.stage_reached,
        linkedin_company_url=result.linkedin_company_url,
        candidates_found=result.candidates_found,
        candidates_enriched=result.candidates_enriched,
        candidates_validated=result.candidates_validated,
        processing_time_ms=result.processing_time_ms,
        cost_credits=result.total_cost_credits,
        errors=result.errors,
    )

    # Add best contact info
    if result.best_contact:
        bc = result.best_contact
        test_result.contact_name = bc.name
        test_result.contact_title = bc.title
        test_result.contact_email = bc.email
        test_result.contact_linkedin = bc.linkedin_url
        test_result.contact_confidence = bc.confidence
        test_result.contact_reasoning = bc.reasoning
        test_result.contact_red_flags = bc.red_flags
        test_result.contact_sources = bc.sources

    return test_result


def print_progress(
    idx: int,
    total: int,
    result: SMBTestResult
):
    """Print progress for one company"""
    status = "OK" if result.success else "FAIL"
    stage = result.stage_reached

    parts = [
        f"[{idx}/{total}]",
        f"{result.company_name[:30]:<30}",
        f"| {result.vertical[:15]:<15}",
        f"| {status:<4}",
        f"| stage={stage:<8}",
    ]

    if result.success:
        parts.append(f"| {result.contact_name or 'N/A'}")
        parts.append(f"| conf={result.contact_confidence:.0f}")
    else:
        parts.append(f"| {', '.join(result.errors[:2])[:40]}")

    print(" ".join(parts))


def calculate_metrics(results: list[SMBTestResult]) -> BatchMetrics:
    """Calculate aggregate metrics"""
    metrics = BatchMetrics()
    metrics.total = len(results)
    metrics.successful = sum(1 for r in results if r.success)
    metrics.failed = metrics.total - metrics.successful

    metrics.linkedin_company_found = sum(1 for r in results if r.linkedin_company_url)
    metrics.candidates_found = sum(1 for r in results if r.candidates_found > 0)
    metrics.candidates_enriched = sum(1 for r in results if r.candidates_enriched > 0)
    metrics.candidates_validated = sum(1 for r in results if r.candidates_validated > 0)

    metrics.total_cost_credits = sum(r.cost_credits for r in results)
    metrics.total_time_seconds = sum(r.processing_time_ms for r in results) / 1000

    # By vertical
    by_vertical = defaultdict(lambda: {
        'total': 0, 'success': 0, 'cost': 0.0,
        'linkedin_found': 0, 'candidates_found': 0
    })

    for r in results:
        v = by_vertical[r.vertical]
        v['total'] += 1
        if r.success:
            v['success'] += 1
        if r.linkedin_company_url:
            v['linkedin_found'] += 1
        if r.candidates_found > 0:
            v['candidates_found'] += 1
        v['cost'] += r.cost_credits

    metrics.by_vertical = dict(by_vertical)

    return metrics


def generate_report(results: list[SMBTestResult], metrics: BatchMetrics) -> str:
    """Generate markdown report"""
    report = f"""# SMB Pipeline Test Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value | Rate |
|--------|-------|------|
| Total Companies | {metrics.total} | - |
| Successful | {metrics.successful} | {metrics.successful/metrics.total*100:.1f}% |
| Failed | {metrics.failed} | {metrics.failed/metrics.total*100:.1f}% |

## Pipeline Stage Success

| Stage | Count | Rate |
|-------|-------|------|
| LinkedIn Company Found | {metrics.linkedin_company_found} | {metrics.linkedin_company_found/metrics.total*100:.1f}% |
| Candidates Found | {metrics.candidates_found} | {metrics.candidates_found/metrics.total*100:.1f}% |
| Candidates Enriched | {metrics.candidates_enriched} | {metrics.candidates_enriched/metrics.total*100:.1f}% |
| Candidates Validated | {metrics.candidates_validated} | {metrics.candidates_validated/metrics.total*100:.1f}% |

## Cost

| Metric | Value |
|--------|-------|
| Total Credits | {metrics.total_cost_credits:.2f} |
| Credits per Company | {metrics.total_cost_credits/metrics.total:.3f} |
| Credits per Success | {metrics.total_cost_credits/max(1,metrics.successful):.3f} |

## Performance by Vertical

| Vertical | Total | Success | Rate | LinkedIn | Candidates | Cost |
|----------|-------|---------|------|----------|------------|------|
"""

    for vertical, stats in sorted(metrics.by_vertical.items()):
        rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
        report += f"| {vertical} | {stats['total']} | {stats['success']} | {rate:.1f}% | {stats['linkedin_found']} | {stats['candidates_found']} | {stats['cost']:.2f} |\n"

    # Contact sources distribution
    source_counts = defaultdict(int)
    for r in results:
        if r.success:
            for src in r.contact_sources:
                source_counts[src] += 1

    report += f"""

## Contact Source Distribution (of {metrics.successful} successful)

| Source | Count | Rate |
|--------|-------|------|
"""
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        report += f"| {source} | {count} | {count/max(1,metrics.successful)*100:.1f}% |\n"

    # Confidence distribution
    conf_buckets = {'0-50': 0, '50-70': 0, '70-85': 0, '85-100': 0}
    for r in results:
        if r.success:
            conf = r.contact_confidence
            if conf < 50:
                conf_buckets['0-50'] += 1
            elif conf < 70:
                conf_buckets['50-70'] += 1
            elif conf < 85:
                conf_buckets['70-85'] += 1
            else:
                conf_buckets['85-100'] += 1

    report += f"""

## Confidence Distribution (of {metrics.successful} successful)

| Range | Count | Rate |
|-------|-------|------|
"""
    for bucket, count in conf_buckets.items():
        report += f"| {bucket} | {count} | {count/max(1,metrics.successful)*100:.1f}% |\n"

    # Error distribution
    error_counts = defaultdict(int)
    for r in results:
        if not r.success:
            for err in r.errors[:1]:  # First error
                # Truncate long errors
                err_key = err[:50] if len(err) > 50 else err
                error_counts[err_key] += 1

    if error_counts:
        report += f"""

## Top Failure Reasons

| Error | Count |
|-------|-------|
"""
        for error, count in sorted(error_counts.items(), key=lambda x: -x[1])[:10]:
            report += f"| {error} | {count} |\n"

    # Sample results
    report += """

## Sample Successful Results (first 15)

"""
    success_results = [r for r in results if r.success][:15]
    for i, r in enumerate(success_results):
        report += f"""
### {i+1}. {r.company_name} ({r.vertical})
- **Domain**: {r.domain}
- **Contact**: {r.contact_name} - {r.contact_title}
- **Email**: {r.contact_email}
- **LinkedIn**: {r.contact_linkedin}
- **Confidence**: {r.contact_confidence:.0f}%
- **Reasoning**: {r.contact_reasoning}
- **Sources**: {', '.join(r.contact_sources)}
"""

    # Sample failures
    report += """

## Sample Failed Results (first 10)

"""
    failed_results = [r for r in results if not r.success][:10]
    for i, r in enumerate(failed_results):
        report += f"""
### {i+1}. {r.company_name} ({r.vertical})
- **Domain**: {r.domain}
- **Stage Reached**: {r.stage_reached}
- **Errors**: {'; '.join(r.errors)}
"""

    return report


async def run_pipeline_test(
    companies: list[dict],
    finder: ContactFinder,
    concurrency: int = 5,
    delay: float = 0.5,
    checkpoint_every: int = 50,
    checkpoint_dir: str = "evaluation/results/checkpoints",
    resume_from: str | None = None,
) -> list[SMBTestResult]:
    """Run pipeline test on all companies"""
    results = []
    semaphore = asyncio.Semaphore(concurrency)
    processed_indices = set()

    # Resume from checkpoint if specified
    if resume_from and os.path.exists(resume_from):
        print(f"Resuming from checkpoint: {resume_from}")
        with open(resume_from, 'r') as f:
            checkpoint_data = json.load(f)
            results = [SMBTestResult(**r) for r in checkpoint_data.get('results', [])]
            processed_indices = set(checkpoint_data.get('processed_indices', []))
            print(f"Loaded {len(results)} previous results")

    # Create checkpoint directory
    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

    async def process_one(idx: int, company: dict) -> SMBTestResult | None:
        if idx in processed_indices:
            return None

        async with semaphore:
            try:
                result = await finder.find_contacts(
                    company_name=company.get('company_name', ''),
                    domain=company.get('domain'),
                )
                test_result = convert_to_test_result(company, result)
            except Exception as e:
                test_result = SMBTestResult(
                    company_name=company.get('company_name', ''),
                    domain=company.get('domain', ''),
                    vertical=company.get('vertical', 'unknown'),
                    success=False,
                    errors=[str(e)],
                )

            print_progress(idx + 1, len(companies), test_result)
            await asyncio.sleep(delay)
            return test_result

    # Process in batches for checkpointing
    checkpoint_file = None
    for batch_start in range(0, len(companies), checkpoint_every):
        batch_end = min(batch_start + checkpoint_every, len(companies))
        batch = companies[batch_start:batch_end]

        # Create tasks
        tasks = [
            process_one(batch_start + i, company)
            for i, company in enumerate(batch)
        ]

        # Run batch
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect results
        for i, result in enumerate(batch_results):
            idx = batch_start + i
            if result is None:
                continue  # Already processed

            if isinstance(result, Exception):
                result = SMBTestResult(
                    company_name=companies[idx].get('company_name', ''),
                    domain=companies[idx].get('domain', ''),
                    vertical=companies[idx].get('vertical', 'unknown'),
                    success=False,
                    errors=[str(result)],
                )

            results.append(result)
            processed_indices.add(idx)

        # Save checkpoint
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = f"{checkpoint_dir}/checkpoint_{timestamp}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'processed_indices': list(processed_indices),
                'results': [asdict(r) for r in results],
            }, f, default=str)

        print(f"\n--- Checkpoint saved: {checkpoint_file} ({len(results)} results) ---\n")

    return results


async def main():
    parser = argparse.ArgumentParser(description="Run SMB Pipeline Test")
    parser.add_argument(
        "--input",
        default="evaluation/data/smb_sample_1400.json",
        help="Input JSON file with SMB sample"
    )
    parser.add_argument(
        "--output",
        default="evaluation/results/smb_pipeline_results.json",
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--config",
        default="contact-finder/config.yaml",
        help="ContactFinder config file"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Max parallel requests (default: 5)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between requests in seconds (default: 0.5)"
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=50,
        help="Save checkpoint every N companies (default: 50)"
    )
    parser.add_argument(
        "--resume",
        help="Resume from checkpoint file"
    )
    parser.add_argument(
        "--sample",
        type=int,
        help="Only process first N companies (for testing)"
    )

    args = parser.parse_args()

    # Load sample
    print(f"Loading SMB sample from: {args.input}")
    companies = load_smb_sample(args.input)

    if args.sample:
        companies = companies[:args.sample]

    print(f"Loaded {len(companies)} companies")

    # Show vertical distribution
    verticals = defaultdict(int)
    for c in companies:
        verticals[c.get('vertical', 'unknown')] += 1

    print("\nVertical distribution:")
    for v, count in sorted(verticals.items()):
        print(f"  {v}: {count}")

    # Initialize ContactFinder
    print(f"\nInitializing ContactFinder from: {args.config}")
    finder = ContactFinder.from_config(args.config)

    print(f"\nSettings:")
    print(f"  Concurrency: {args.concurrency}")
    print(f"  Delay: {args.delay}s")
    print(f"  Checkpoint every: {args.checkpoint_every}")
    if args.resume:
        print(f"  Resuming from: {args.resume}")

    print("\n" + "=" * 80)
    print("STARTING SMB PIPELINE TEST")
    print("=" * 80 + "\n")

    start_time = time.time()

    try:
        results = await run_pipeline_test(
            companies,
            finder,
            concurrency=args.concurrency,
            delay=args.delay,
            checkpoint_every=args.checkpoint_every,
            resume_from=args.resume,
        )
    finally:
        await finder.close()

    elapsed = time.time() - start_time

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print(f"\nTotal time: {elapsed:.1f}s ({elapsed/len(results):.2f}s per company)")

    # Calculate metrics
    metrics = calculate_metrics(results)

    # Generate report
    report = generate_report(results, metrics)
    print("\n" + report)

    # Save outputs
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save JSON results
    with open(output_path, 'w') as f:
        json.dump({
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'input_file': args.input,
                'total_companies': len(companies),
                'elapsed_seconds': elapsed,
            },
            'metrics': asdict(metrics),
            'results': [asdict(r) for r in results],
        }, f, indent=2, default=str)

    print(f"\nResults saved: {output_path}")

    # Save markdown report
    report_path = output_path.with_suffix('.md')
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"Report saved: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
