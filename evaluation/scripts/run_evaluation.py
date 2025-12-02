#!/usr/bin/env python3
"""
Phase 3: Run Evaluation Pipeline

This script evaluates the domain resolver and contact finder against ground truth.
Generates metrics and reports comparing predictions to verified data.

Usage:
    python evaluation/scripts/run_evaluation.py [--domain-only] [--contact-only] [--split cal_dev]
"""

import asyncio
import argparse
import pandas as pd
import yaml
import logging
import sys
import time
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "domain-resolver"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "contact-finder"))

from evaluation.harness.cache import EvaluationCache
from evaluation.harness.metrics import calculate_domain_metrics, MetricsResult

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================
# Domain Resolver Evaluator
# ============================================================

@dataclass
class DomainEvalResult:
    """Result for a single domain resolution"""
    company_name: str
    expected_domain: str
    resolved_domain: str | None = None
    confidence: float = 0
    source: str | None = None
    correct: bool = False
    latency_ms: int = 0
    error: str | None = None


class DomainResolverEvaluator:
    """Evaluates domain resolution against ground truth"""

    def __init__(self, cache_path: str = "./evaluation/data/cache.db"):
        self.cache = EvaluationCache(cache_path)
        self._resolver = None
        self._config = None

    async def _get_resolver(self):
        """Get or create domain resolver"""
        if self._resolver is None:
            # Load domain resolver config
            config_path = Path(__file__).parent.parent.parent / "domain-resolver" / "config.yaml"
            with open(config_path) as f:
                self._config = yaml.safe_load(f)

            from domain_resolver import DomainResolver
            self._resolver = DomainResolver(self._config)
        return self._resolver

    async def evaluate(
        self,
        companies_df: pd.DataFrame,
        max_concurrent: int = 5,
        skip_cache: bool = False
    ) -> tuple[list[DomainEvalResult], pd.DataFrame]:
        """
        Run domain resolution against ground truth companies

        Args:
            companies_df: DataFrame with name, city, expected_domain columns
            max_concurrent: Max concurrent API calls
            skip_cache: Skip cache and always call API

        Returns:
            List of DomainEvalResult and DataFrame with results
        """
        results: list[DomainEvalResult] = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def resolve_company(row):
            async with semaphore:
                return await self._resolve_single(row, skip_cache)

        companies = companies_df.to_dict('records')
        logger.info(f"Evaluating domain resolution for {len(companies)} companies")

        tasks = [resolve_company(c) for c in companies]
        results = await asyncio.gather(*tasks)

        # Convert to DataFrame
        results_df = pd.DataFrame([
            {
                "company_name": r.company_name,
                "domain": r.resolved_domain,
                "confidence": r.confidence,
                "source": r.source,
                "correct": r.correct,
                "latency_ms": r.latency_ms,
                "error": r.error
            }
            for r in results
        ])

        return results, results_df

    async def _resolve_single(self, company: dict, skip_cache: bool) -> DomainEvalResult:
        """Resolve domain for a single company"""
        name = company["name"]
        city = company.get("city", "")
        expected = company.get("expected_domain", "")

        result = DomainEvalResult(
            company_name=name,
            expected_domain=expected
        )

        # Check cache
        cache_key = f"{name}:{city}"
        if not skip_cache:
            cached = self.cache.get("domain_resolver", cache_key)
            if cached:
                result.resolved_domain = cached.get("domain")
                result.confidence = cached.get("confidence", 0)
                result.source = cached.get("source")
                result.correct = self._domains_match(result.resolved_domain, expected)
                return result

        # Call domain resolver
        try:
            resolver = await self._get_resolver()

            start = time.time()
            resolution = await resolver.resolve(name, city=city)
            result.latency_ms = int((time.time() - start) * 1000)

            if resolution:
                result.resolved_domain = resolution.get("domain")
                result.confidence = resolution.get("confidence", 0)
                result.source = resolution.get("source")
                result.correct = self._domains_match(result.resolved_domain, expected)

                # Cache result
                self.cache.set("domain_resolver", cache_key, response={
                    "domain": result.resolved_domain,
                    "confidence": result.confidence,
                    "source": result.source
                })

        except Exception as e:
            result.error = str(e)
            logger.debug(f"Domain resolution error for {name}: {e}")

        return result

    def _domains_match(self, d1: str | None, d2: str | None) -> bool:
        """Check if two domains match"""
        if not d1 or not d2:
            return False
        d1 = str(d1).lower().replace("www.", "").rstrip("/").strip()
        d2 = str(d2).lower().replace("www.", "").rstrip("/").strip()
        return d1 == d2


# ============================================================
# Blitz Contact Finder Evaluator
# ============================================================

@dataclass
class ContactEvalResult:
    """Result for a single contact finding attempt"""
    company_name: str
    linkedin_url: str
    target_persona: str
    contacts_found: int = 0
    contacts: list = field(default_factory=list)
    persona_found: bool = False
    credits_consumed: float = 0
    latency_ms: int = 0
    error: str | None = None


class BlitzContactEvaluator:
    """Evaluates Blitz contact finding against companies"""

    PERSONA_TITLES = {
        "owner_operator": ["owner", "founder", "ceo", "president", "principal", "managing partner", "co-founder"],
        "vp_marketing": ["vp marketing", "vp of marketing", "head of marketing", "cmo", "director marketing", "marketing director"],
        "vp_sales": ["vp sales", "vp of sales", "head of sales", "cro", "director sales", "sales director"]
    }

    def __init__(
        self,
        api_key: str,
        cache_path: str = "./evaluation/data/cache.db"
    ):
        self.api_key = api_key
        self.cache = EvaluationCache(cache_path)
        self._client = None

    async def _get_client(self):
        """Get or create Blitz client"""
        if self._client is None:
            from modules.enrichment.blitz import BlitzClient
            self._client = BlitzClient(self.api_key)
        return self._client

    async def close(self):
        if self._client:
            await self._client.close()

    async def evaluate(
        self,
        companies_df: pd.DataFrame,
        personas: list[str] = None,
        max_results_per_call: int = 5,
        use_realtime: bool = False,
        max_concurrent: int = 3,
        skip_cache: bool = False
    ) -> tuple[list[ContactEvalResult], pd.DataFrame]:
        """
        Run contact finding against companies

        Args:
            companies_df: DataFrame with name, linkedin_company_url columns
            personas: List of persona types to search for
            max_results_per_call: Max results per API call
            use_realtime: Use real-time mode (3x credits)
            max_concurrent: Max concurrent API calls
            skip_cache: Skip cache

        Returns:
            List of ContactEvalResult and DataFrame with results
        """
        personas = personas or ["owner_operator"]

        # Filter to companies with LinkedIn URLs
        has_linkedin = companies_df[companies_df["linkedin_company_url"].notna()]
        logger.info(f"Evaluating contact finding for {len(has_linkedin)} companies with LinkedIn URLs")

        results: list[ContactEvalResult] = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def find_contacts(company, persona):
            async with semaphore:
                return await self._find_single(
                    company, persona, max_results_per_call, use_realtime, skip_cache
                )

        # Create tasks for all company-persona combinations
        tasks = []
        for _, row in has_linkedin.iterrows():
            company = row.to_dict()
            for persona in personas:
                tasks.append(find_contacts(company, persona))

        results = await asyncio.gather(*tasks)

        # Convert to DataFrame
        results_df = pd.DataFrame([
            {
                "company_name": r.company_name,
                "linkedin_url": r.linkedin_url,
                "persona": r.target_persona,
                "contacts_found": r.contacts_found,
                "persona_found": r.persona_found,
                "credits": r.credits_consumed,
                "latency_ms": r.latency_ms,
                "error": r.error
            }
            for r in results
        ])

        return results, results_df

    async def _find_single(
        self,
        company: dict,
        persona: str,
        max_results: int,
        use_realtime: bool,
        skip_cache: bool
    ) -> ContactEvalResult:
        """Find contacts for a single company"""
        linkedin_url = company["linkedin_company_url"]
        name = company["name"]

        result = ContactEvalResult(
            company_name=name,
            linkedin_url=linkedin_url,
            target_persona=persona
        )

        # Get title patterns for persona
        titles = self._get_titles_for_persona(persona)

        # Check cache
        cache_key = f"{linkedin_url}:{persona}:{use_realtime}"
        if not skip_cache:
            cached = self.cache.get("blitz_waterfall", cache_key)
            if cached:
                result.contacts = cached.get("contacts", [])
                result.contacts_found = len(result.contacts)
                result.persona_found = cached.get("persona_found", False)
                result.credits_consumed = cached.get("credits", 0)
                return result

        # Call Blitz API
        try:
            client = await self._get_client()

            start = time.time()
            contacts = await client.waterfall_icp(
                linkedin_company_url=linkedin_url,
                titles=titles,
                max_results=max_results,
                real_time=use_realtime
            )
            result.latency_ms = int((time.time() - start) * 1000)

            result.contacts_found = len(contacts)
            result.contacts = [
                {
                    "name": c.name,
                    "title": c.title,
                    "linkedin_url": c.linkedin_url,
                    "email": c.email,
                    "confidence": c.confidence
                }
                for c in contacts
            ]

            # Check if persona was found
            result.persona_found = any(
                self._title_matches_persona(c.get("title"), persona)
                for c in result.contacts
            )

            # Calculate credits
            credits_per = 3 if use_realtime else 1
            result.credits_consumed = len(contacts) * credits_per

            # Cache result
            self.cache.set("blitz_waterfall", cache_key, response={
                "contacts": result.contacts,
                "persona_found": result.persona_found,
                "credits": result.credits_consumed,
                "latency_ms": result.latency_ms
            })

        except Exception as e:
            result.error = str(e)
            logger.debug(f"Blitz error for {name}: {e}")

        return result

    def _get_titles_for_persona(self, persona: str) -> list[str]:
        """Get title patterns for a persona type"""
        patterns = {
            "owner_operator": [
                "Owner", "Founder", "CEO", "Chief Executive Officer",
                "President", "Principal", "Managing Partner", "Co-Founder"
            ],
            "vp_marketing": [
                "VP Marketing", "VP of Marketing", "Vice President Marketing",
                "Head of Marketing", "CMO", "Chief Marketing Officer",
                "Director of Marketing", "Marketing Director"
            ],
            "vp_sales": [
                "VP Sales", "VP of Sales", "Vice President Sales",
                "Head of Sales", "CRO", "Chief Revenue Officer",
                "Director of Sales", "Sales Director"
            ]
        }
        return patterns.get(persona, [])

    def _title_matches_persona(self, title: str | None, persona: str) -> bool:
        """Check if a title matches a persona type"""
        if not title:
            return False
        title_lower = title.lower()
        patterns = self.PERSONA_TITLES.get(persona, [])
        return any(p in title_lower for p in patterns)


# ============================================================
# Report Generator
# ============================================================

def generate_evaluation_report(
    domain_results_df: pd.DataFrame | None,
    contact_results_df: pd.DataFrame | None,
    ground_truth_df: pd.DataFrame,
    output_path: str,
    config: dict
) -> str:
    """Generate comprehensive evaluation report"""

    report = f"""# Evaluation Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Ground Truth Summary

| Metric | Value |
|--------|-------|
| Total Companies | {len(ground_truth_df)} |
| Gold Tier | {(ground_truth_df['domain_tier'] == 'gold').sum()} |
| With LinkedIn URLs | {ground_truth_df['linkedin_company_url'].notna().sum()} |

### Industry Distribution
| Industry | Count | % |
|----------|-------|---|
"""

    for industry, count in ground_truth_df['industry'].value_counts().items():
        pct = count / len(ground_truth_df) * 100
        report += f"| {industry} | {count} | {pct:.1f}% |\n"

    report += """
### Size Distribution
| Size | Count | % |
|------|-------|---|
"""

    for size, count in ground_truth_df['size_bucket'].value_counts().items():
        pct = count / len(ground_truth_df) * 100
        report += f"| {size} | {count} | {pct:.1f}% |\n"

    # Domain Resolution Metrics
    if domain_results_df is not None and len(domain_results_df) > 0:
        # Calculate metrics
        domain_metrics = calculate_domain_metrics(
            domain_results_df,
            ground_truth_df,
            join_on=("company_name", "name")
        )

        report += f"""
## Domain Resolution Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Accuracy | {domain_metrics.accuracy*100:.1f}% | {config['targets']['domain']['accuracy']*100:.0f}% | {'PASS' if domain_metrics.accuracy >= config['targets']['domain']['accuracy'] else 'FAIL'} |
| Precision | {domain_metrics.precision*100:.1f}% | - | - |
| Recall | {domain_metrics.recall*100:.1f}% | - | - |
| F1 Score | {domain_metrics.f1_score*100:.1f}% | - | - |
| Coverage | {domain_metrics.coverage*100:.1f}% | {config['targets']['domain']['coverage']*100:.0f}% | {'PASS' if domain_metrics.coverage >= config['targets']['domain']['coverage'] else 'FAIL'} |

### Confidence Calibration

| Confidence Band | Count | Accuracy |
|-----------------|-------|----------|
| High (85-100) | {domain_metrics.high_conf_count} | {domain_metrics.high_conf_accuracy*100:.1f}% |
| Medium (70-85) | {domain_metrics.medium_conf_count} | {domain_metrics.medium_conf_accuracy*100:.1f}% |
| Low (0-70) | {domain_metrics.low_conf_count} | {domain_metrics.low_conf_accuracy*100:.1f}% |

**Expected Calibration Error (ECE):** {domain_metrics.calibration_ece:.3f} (Target: <{config['targets']['domain']['calibration_ece']})

### Accuracy by Industry
| Industry | Count | Accuracy |
|----------|-------|----------|
"""
        for industry, stats in domain_metrics.by_industry.items():
            report += f"| {industry} | {stats['count']} | {stats['accuracy']*100:.1f}% |\n"

        report += """
### Accuracy by Size
| Size | Count | Accuracy |
|------|-------|----------|
"""
        for size, stats in domain_metrics.by_size_bucket.items():
            report += f"| {size} | {stats['count']} | {stats['accuracy']*100:.1f}% |\n"

        report += """
### Accuracy by Tier
| Tier | Count | Accuracy |
|------|-------|----------|
"""
        for tier, stats in domain_metrics.by_tier.items():
            report += f"| {tier} | {stats['count']} | {stats['accuracy']*100:.1f}% |\n"

    # Contact Finding Metrics
    if contact_results_df is not None and len(contact_results_df) > 0:
        total_queries = len(contact_results_df)
        persona_hits = contact_results_df['persona_found'].sum()
        total_contacts = contact_results_df['contacts_found'].sum()
        total_credits = contact_results_df['credits'].sum()
        errors = (contact_results_df['error'].notna()).sum()

        persona_hit_rate = persona_hits / total_queries if total_queries > 0 else 0
        avg_contacts = total_contacts / total_queries if total_queries > 0 else 0
        cost_per_hit = total_credits / persona_hits if persona_hits > 0 else float('inf')

        report += f"""
## Contact Finding Metrics (Blitz)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Queries | {total_queries} | - | - |
| Persona Hit Rate | {persona_hit_rate*100:.1f}% | {config['targets']['contact']['persona_recall']*100:.0f}% | {'PASS' if persona_hit_rate >= config['targets']['contact']['persona_recall'] else 'FAIL'} |
| Total Contacts Found | {total_contacts} | - | - |
| Avg Contacts/Query | {avg_contacts:.1f} | - | - |
| Total Credits Used | {total_credits:.1f} | - | - |
| Cost per Hit | {cost_per_hit:.2f} credits | <{config['targets']['e2e']['cost_per_contact']} | {'PASS' if cost_per_hit <= config['targets']['e2e']['cost_per_contact'] else 'FAIL'} |
| Errors | {errors} | - | - |

### By Persona
| Persona | Queries | Hits | Hit Rate | Avg Contacts |
|---------|---------|------|----------|--------------|
"""
        for persona in contact_results_df['persona'].unique():
            p_df = contact_results_df[contact_results_df['persona'] == persona]
            p_queries = len(p_df)
            p_hits = p_df['persona_found'].sum()
            p_hit_rate = p_hits / p_queries if p_queries > 0 else 0
            p_avg_contacts = p_df['contacts_found'].mean()
            report += f"| {persona} | {p_queries} | {p_hits} | {p_hit_rate*100:.1f}% | {p_avg_contacts:.1f} |\n"

    # Summary
    report += """
## Summary

"""

    passed = 0
    failed = 0

    if domain_results_df is not None:
        if domain_metrics.accuracy >= config['targets']['domain']['accuracy']:
            report += "- Domain Accuracy: PASS\n"
            passed += 1
        else:
            report += f"- Domain Accuracy: FAIL ({domain_metrics.accuracy*100:.1f}% < {config['targets']['domain']['accuracy']*100:.0f}%)\n"
            failed += 1

        if domain_metrics.coverage >= config['targets']['domain']['coverage']:
            report += "- Domain Coverage: PASS\n"
            passed += 1
        else:
            report += f"- Domain Coverage: FAIL ({domain_metrics.coverage*100:.1f}% < {config['targets']['domain']['coverage']*100:.0f}%)\n"
            failed += 1

    if contact_results_df is not None:
        if persona_hit_rate >= config['targets']['contact']['persona_recall']:
            report += "- Contact Persona Recall: PASS\n"
            passed += 1
        else:
            report += f"- Contact Persona Recall: FAIL ({persona_hit_rate*100:.1f}% < {config['targets']['contact']['persona_recall']*100:.0f}%)\n"
            failed += 1

        if cost_per_hit <= config['targets']['e2e']['cost_per_contact']:
            report += "- Cost per Contact: PASS\n"
            passed += 1
        else:
            report += f"- Cost per Contact: FAIL ({cost_per_hit:.2f} > {config['targets']['e2e']['cost_per_contact']})\n"
            failed += 1

    report += f"""
**Overall: {passed} passed, {failed} failed**
"""

    # Write report
    with open(output_path, 'w') as f:
        f.write(report)

    logger.info(f"Report saved to {output_path}")
    return report


# ============================================================
# Main Entry Point
# ============================================================

async def main():
    parser = argparse.ArgumentParser(description="Run evaluation pipeline")
    parser.add_argument("--domain-only", action="store_true", help="Only run domain evaluation")
    parser.add_argument("--contact-only", action="store_true", help="Only run contact evaluation")
    parser.add_argument("--split", default="cal_dev", choices=["cal_dev", "validation", "blind", "all"],
                       help="Which data split to evaluate")
    parser.add_argument("--skip-cache", action="store_true", help="Skip cache, call APIs fresh")
    parser.add_argument("--max-concurrent", type=int, default=5, help="Max concurrent API calls")
    parser.add_argument("--personas", nargs="+", default=["owner_operator"],
                       help="Personas to search for")
    args = parser.parse_args()

    print("=" * 60)
    print("PHASE 3: EVALUATION PIPELINE")
    print("=" * 60)

    # Load config
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Load ground truth
    data_dir = Path(__file__).parent.parent / "data"

    if args.split == "all":
        gt_path = data_dir / "companies_truth.parquet"
    else:
        gt_path = data_dir / f"companies_{args.split}.parquet"

    if not gt_path.exists():
        print(f"Ground truth not found at {gt_path}")
        print("Run Phase 2 first: python evaluation/scripts/build_full_ground_truth.py")
        return 1

    ground_truth_df = pd.read_parquet(gt_path)
    print(f"\nLoaded {len(ground_truth_df)} companies from {gt_path.name}")

    domain_results_df = None
    contact_results_df = None

    # Run domain evaluation
    if not args.contact_only:
        print("\n" + "-" * 40)
        print("Step 1: Domain Resolution Evaluation")
        print("-" * 40)

        domain_evaluator = DomainResolverEvaluator(
            cache_path=str(data_dir / "cache.db")
        )

        try:
            _, domain_results_df = await domain_evaluator.evaluate(
                ground_truth_df,
                max_concurrent=args.max_concurrent,
                skip_cache=args.skip_cache
            )

            correct = domain_results_df['correct'].sum()
            total = len(domain_results_df)
            print(f"  Domain accuracy: {correct}/{total} = {correct/total*100:.1f}%")

            # Save raw results
            domain_results_df.to_parquet(data_dir / f"domain_results_{args.split}.parquet")
            print(f"  Saved results to domain_results_{args.split}.parquet")

        except Exception as e:
            logger.error(f"Domain evaluation failed: {e}")
            print(f"  Domain evaluation skipped: {e}")

    # Run contact evaluation
    if not args.domain_only:
        print("\n" + "-" * 40)
        print("Step 2: Contact Finding Evaluation (Blitz)")
        print("-" * 40)

        blitz_key = config['api_keys'].get('blitz')
        if not blitz_key:
            print("  Skipped: No Blitz API key configured")
        else:
            contact_evaluator = BlitzContactEvaluator(
                api_key=blitz_key,
                cache_path=str(data_dir / "cache.db")
            )

            try:
                _, contact_results_df = await contact_evaluator.evaluate(
                    ground_truth_df,
                    personas=args.personas,
                    max_concurrent=args.max_concurrent,
                    skip_cache=args.skip_cache
                )

                hits = contact_results_df['persona_found'].sum()
                total = len(contact_results_df)
                print(f"  Persona hit rate: {hits}/{total} = {hits/total*100:.1f}%")

                # Save raw results
                contact_results_df.to_parquet(data_dir / f"contact_results_{args.split}.parquet")
                print(f"  Saved results to contact_results_{args.split}.parquet")

            except Exception as e:
                logger.error(f"Contact evaluation failed: {e}")
                print(f"  Contact evaluation failed: {e}")
            finally:
                await contact_evaluator.close()

    # Generate report
    print("\n" + "-" * 40)
    print("Step 3: Generate Report")
    print("-" * 40)

    report_path = data_dir / f"evaluation_report_{args.split}.md"
    report = generate_evaluation_report(
        domain_results_df,
        contact_results_df,
        ground_truth_df,
        str(report_path),
        config
    )

    print(f"\nReport saved to: {report_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
