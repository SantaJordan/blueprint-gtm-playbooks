"""
Blitz API Evaluator

Tests the Blitz waterfall-icp endpoint against ground truth contacts.
Compares Blitz results against other contact discovery methods.
"""

import asyncio
import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import logging
import sys

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "contact-finder"))

from .cache import EvaluationCache
from .metrics import MetricsResult

logger = logging.getLogger(__name__)


# Target title patterns per persona
PERSONA_TITLES = {
    "owner_operator": [
        "Owner", "Founder", "CEO", "Chief Executive Officer",
        "President", "Principal", "Managing Partner", "Proprietor",
        "Co-Founder", "Co-Owner"
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


@dataclass
class BlitzEvalResult:
    """Result of evaluating Blitz for a single company"""
    company_name: str
    linkedin_company_url: str
    target_persona: str

    # What we found
    contacts_returned: int = 0
    contacts: list[dict] = field(default_factory=list)
    credits_consumed: float = 0

    # Accuracy metrics
    persona_found: bool = False  # Found at least 1 person with matching title
    person_matched: bool = False  # Found the exact ground truth person
    email_matched: bool = False  # Email matches ground truth

    # Ground truth comparison
    ground_truth_contact: dict = field(default_factory=dict)

    # Timing
    latency_ms: int = 0

    # Errors
    error: str | None = None


@dataclass
class BlitzEvalSummary:
    """Summary metrics for Blitz evaluation"""
    total_companies: int = 0
    total_contacts_found: int = 0
    total_credits: float = 0

    # Per-persona metrics
    persona_hit_rate: float = 0.0  # % of companies where we found target persona
    person_match_rate: float = 0.0  # % where we found exact person
    email_match_rate: float = 0.0  # % where email matched

    # Cost metrics
    cost_per_company: float = 0.0
    cost_per_hit: float = 0.0

    # Breakdown by persona
    by_persona: dict = field(default_factory=dict)

    # Breakdown by company size
    by_size: dict = field(default_factory=dict)

    # Detailed results
    results: list[BlitzEvalResult] = field(default_factory=list)


class BlitzEvaluator:
    """
    Evaluates Blitz waterfall-icp endpoint against ground truth.

    Usage:
        evaluator = BlitzEvaluator(
            api_key="blitz_VQkRdq6HiJMk5xqkz9anTW3S",
            cache_path="./evaluation/data/cache.db"
        )

        # Load ground truth
        evaluator.load_ground_truth("contacts_truth.parquet")

        # Run evaluation
        summary = await evaluator.evaluate_waterfall_icp(
            persona_types=["owner_operator", "vp_sales"]
        )

        # Generate report
        evaluator.generate_report(summary, "blitz_eval_report.md")
    """

    def __init__(
        self,
        api_key: str,
        cache_path: str | Path = "./evaluation/data/cache.db"
    ):
        self.api_key = api_key
        self.cache = EvaluationCache(cache_path)
        self._client = None

        # Ground truth data
        self.companies_df: pd.DataFrame | None = None
        self.contacts_df: pd.DataFrame | None = None

    async def _get_client(self):
        """Get or create Blitz client"""
        if self._client is None:
            from modules.enrichment.blitz import BlitzClient
            self._client = BlitzClient(self.api_key)
        return self._client

    async def close(self):
        """Close the client"""
        if self._client:
            await self._client.close()

    def load_ground_truth(
        self,
        companies_path: str | Path,
        contacts_path: str | Path | None = None
    ):
        """
        Load ground truth data.

        Companies must have: name, linkedin_company_url
        Contacts must have: company_name, name, title, persona_type, email, linkedin_url
        """
        # Load companies
        if str(companies_path).endswith(".parquet"):
            self.companies_df = pd.read_parquet(companies_path)
        else:
            self.companies_df = pd.read_csv(companies_path)

        logger.info(f"Loaded {len(self.companies_df)} companies from ground truth")

        # Load contacts if provided
        if contacts_path:
            if str(contacts_path).endswith(".parquet"):
                self.contacts_df = pd.read_parquet(contacts_path)
            else:
                self.contacts_df = pd.read_csv(contacts_path)

            logger.info(f"Loaded {len(self.contacts_df)} contacts from ground truth")

    async def evaluate_waterfall_icp(
        self,
        persona_types: list[str] | None = None,
        max_results_per_call: int = 5,
        use_realtime: bool = False,
        max_concurrent: int = 3,
        skip_cache: bool = False
    ) -> BlitzEvalSummary:
        """
        Evaluate Blitz waterfall-icp against ground truth.

        Args:
            persona_types: Which personas to test (default: all)
            max_results_per_call: Max results to request from Blitz
            use_realtime: Use real-time (3 credits) vs regular (1 credit)
            max_concurrent: Max concurrent API calls
            skip_cache: Skip cache and always call API

        Returns:
            BlitzEvalSummary with metrics and detailed results
        """
        if self.companies_df is None:
            raise ValueError("Load ground truth first with load_ground_truth()")

        persona_types = persona_types or list(PERSONA_TITLES.keys())

        # Filter to companies with LinkedIn URLs
        companies = self.companies_df[
            self.companies_df["linkedin_company_url"].notna()
        ].to_dict("records")

        logger.info(f"Evaluating {len(companies)} companies for {len(persona_types)} personas")

        semaphore = asyncio.Semaphore(max_concurrent)
        results: list[BlitzEvalResult] = []

        async def evaluate_company(company: dict, persona: str):
            async with semaphore:
                result = await self._evaluate_single(
                    company, persona, max_results_per_call, use_realtime, skip_cache
                )
                results.append(result)

        # Create tasks for all company-persona combinations
        tasks = []
        for company in companies:
            for persona in persona_types:
                # Check if we have ground truth contacts for this persona
                if self.contacts_df is not None:
                    gt_contacts = self.contacts_df[
                        (self.contacts_df["company_name"] == company["name"]) &
                        (self.contacts_df["persona_type"] == persona)
                    ]
                    if len(gt_contacts) == 0:
                        continue  # Skip if no ground truth for this persona

                tasks.append(evaluate_company(company, persona))

        await asyncio.gather(*tasks)

        # Compute summary
        summary = self._compute_summary(results)

        return summary

    async def _evaluate_single(
        self,
        company: dict,
        persona: str,
        max_results: int,
        use_realtime: bool,
        skip_cache: bool
    ) -> BlitzEvalResult:
        """Evaluate Blitz for a single company-persona combination"""
        import time

        linkedin_url = company["linkedin_company_url"]
        titles = PERSONA_TITLES.get(persona, [])

        result = BlitzEvalResult(
            company_name=company["name"],
            linkedin_company_url=linkedin_url,
            target_persona=persona
        )

        # Check cache first
        cache_key = f"{linkedin_url}:{persona}:{use_realtime}"
        if not skip_cache:
            cached = self.cache.get("blitz_waterfall", cache_key)
            if cached:
                return self._parse_cached_result(cached, result)

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

            result.contacts_returned = len(contacts)
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

            # Estimate credits (3 per result if realtime, 1 otherwise)
            credits_per = 3 if use_realtime else 1
            result.credits_consumed = len(contacts) * credits_per

            # Compare against ground truth
            if self.contacts_df is not None:
                gt = self.contacts_df[
                    (self.contacts_df["company_name"] == company["name"]) &
                    (self.contacts_df["persona_type"] == persona)
                ]

                if len(gt) > 0:
                    gt_contact = gt.iloc[0].to_dict()
                    result.ground_truth_contact = gt_contact

                    # Check persona match (title contains persona pattern)
                    result.persona_found = any(
                        self._title_matches_persona(c.get("title"), persona)
                        for c in result.contacts
                    )

                    # Check person match (LinkedIn URL or name match)
                    result.person_matched = any(
                        self._person_matches(c, gt_contact)
                        for c in result.contacts
                    )

                    # Check email match
                    if gt_contact.get("email"):
                        gt_email = gt_contact["email"].lower()
                        result.email_matched = any(
                            c.get("email", "").lower() == gt_email
                            for c in result.contacts
                        )

            # Cache the result
            self.cache.set("blitz_waterfall", cache_key, response={
                "contacts": result.contacts,
                "credits": result.credits_consumed,
                "latency_ms": result.latency_ms,
                "persona_found": result.persona_found,
                "person_matched": result.person_matched,
                "email_matched": result.email_matched
            })

        except Exception as e:
            result.error = str(e)
            logger.error(f"Blitz error for {company['name']}: {e}")

        return result

    def _parse_cached_result(self, cached: dict, result: BlitzEvalResult) -> BlitzEvalResult:
        """Parse cached Blitz result"""
        result.contacts = cached.get("contacts", [])
        result.contacts_returned = len(result.contacts)
        result.credits_consumed = cached.get("credits", 0)
        result.latency_ms = cached.get("latency_ms", 0)
        result.persona_found = cached.get("persona_found", False)
        result.person_matched = cached.get("person_matched", False)
        result.email_matched = cached.get("email_matched", False)
        return result

    def _title_matches_persona(self, title: str | None, persona: str) -> bool:
        """Check if a title matches a persona type"""
        if not title:
            return False

        title_lower = title.lower()
        patterns = {
            "owner_operator": ["owner", "founder", "ceo", "president", "principal", "managing partner"],
            "vp_marketing": ["vp marketing", "head of marketing", "cmo", "director marketing"],
            "vp_sales": ["vp sales", "head of sales", "cro", "director sales"]
        }

        return any(p in title_lower for p in patterns.get(persona, []))

    def _person_matches(self, contact: dict, ground_truth: dict) -> bool:
        """Check if a contact matches ground truth person"""
        # Match by LinkedIn URL (most reliable)
        c_li = (contact.get("linkedin_url") or "").lower().rstrip("/")
        gt_li = (ground_truth.get("linkedin_url") or "").lower().rstrip("/")
        if c_li and gt_li and c_li == gt_li:
            return True

        # Match by name (fuzzy)
        c_name = (contact.get("name") or "").lower()
        gt_name = (ground_truth.get("name") or "").lower()
        if c_name and gt_name:
            # Simple containment check
            if c_name in gt_name or gt_name in c_name:
                return True

        return False

    def _compute_summary(self, results: list[BlitzEvalResult]) -> BlitzEvalSummary:
        """Compute summary metrics from results"""
        summary = BlitzEvalSummary()
        summary.results = results

        if not results:
            return summary

        summary.total_companies = len(results)
        summary.total_contacts_found = sum(r.contacts_returned for r in results)
        summary.total_credits = sum(r.credits_consumed for r in results)

        # Core metrics
        persona_hits = sum(1 for r in results if r.persona_found)
        person_matches = sum(1 for r in results if r.person_matched)
        email_matches = sum(1 for r in results if r.email_matched and r.person_matched)

        n = len(results)
        summary.persona_hit_rate = persona_hits / n if n > 0 else 0
        summary.person_match_rate = person_matches / n if n > 0 else 0
        summary.email_match_rate = email_matches / person_matches if person_matches > 0 else 0

        # Cost metrics
        summary.cost_per_company = summary.total_credits / n if n > 0 else 0
        summary.cost_per_hit = summary.total_credits / persona_hits if persona_hits > 0 else float("inf")

        # Breakdown by persona
        personas = set(r.target_persona for r in results)
        for persona in personas:
            p_results = [r for r in results if r.target_persona == persona]
            p_n = len(p_results)
            summary.by_persona[persona] = {
                "count": p_n,
                "persona_hit_rate": sum(1 for r in p_results if r.persona_found) / p_n if p_n > 0 else 0,
                "person_match_rate": sum(1 for r in p_results if r.person_matched) / p_n if p_n > 0 else 0,
                "avg_contacts": sum(r.contacts_returned for r in p_results) / p_n if p_n > 0 else 0,
            }

        return summary

    def generate_report(self, summary: BlitzEvalSummary, output_path: str | Path):
        """Generate markdown evaluation report"""
        report = f"""# Blitz Waterfall-ICP Evaluation Report

## Summary

| Metric | Value |
|--------|-------|
| Total Companies Tested | {summary.total_companies} |
| Total Contacts Found | {summary.total_contacts_found} |
| Total Credits Used | {summary.total_credits:.1f} |
| **Persona Hit Rate** | **{summary.persona_hit_rate*100:.1f}%** |
| **Person Match Rate** | **{summary.person_match_rate*100:.1f}%** |
| **Email Match Rate** | **{summary.email_match_rate*100:.1f}%** |
| Cost per Company | {summary.cost_per_company:.2f} credits |
| Cost per Hit | {summary.cost_per_hit:.2f} credits |

## Breakdown by Persona

| Persona | Count | Persona Hit Rate | Person Match Rate | Avg Contacts |
|---------|-------|-----------------|-------------------|--------------|
"""
        for persona, stats in summary.by_persona.items():
            report += f"| {persona} | {stats['count']} | {stats['persona_hit_rate']*100:.1f}% | {stats['person_match_rate']*100:.1f}% | {stats['avg_contacts']:.1f} |\n"

        report += """
## Detailed Results

### Sample Failures (Persona Not Found)

"""
        failures = [r for r in summary.results if not r.persona_found][:10]
        for r in failures:
            report += f"- **{r.company_name}** ({r.target_persona}): {r.contacts_returned} contacts returned, "
            if r.contacts:
                titles = [c.get("title", "N/A") for c in r.contacts[:3]]
                report += f"titles: {titles}\n"
            else:
                report += "no contacts\n"

        report += """
### Sample Successes (Exact Match)

"""
        successes = [r for r in summary.results if r.person_matched][:10]
        for r in successes:
            report += f"- **{r.company_name}** ({r.target_persona}): Found {r.ground_truth_contact.get('name', 'N/A')}\n"

        # Write report
        with open(output_path, "w") as f:
            f.write(report)

        logger.info(f"Wrote evaluation report to {output_path}")


async def run_blitz_evaluation(
    api_key: str,
    companies_path: str,
    contacts_path: str | None = None,
    output_path: str = "blitz_eval_report.md",
    personas: list[str] | None = None
):
    """
    Convenience function to run Blitz evaluation.

    Args:
        api_key: Blitz API key
        companies_path: Path to companies ground truth CSV/parquet
        contacts_path: Path to contacts ground truth CSV/parquet
        output_path: Path for output report
        personas: List of personas to test
    """
    evaluator = BlitzEvaluator(api_key)

    try:
        evaluator.load_ground_truth(companies_path, contacts_path)
        summary = await evaluator.evaluate_waterfall_icp(persona_types=personas)
        evaluator.generate_report(summary, output_path)

        print(f"\nBlitz Evaluation Complete:")
        print(f"  Persona Hit Rate: {summary.persona_hit_rate*100:.1f}%")
        print(f"  Person Match Rate: {summary.person_match_rate*100:.1f}%")
        print(f"  Total Credits: {summary.total_credits:.1f}")
        print(f"\nReport saved to: {output_path}")

        return summary

    finally:
        await evaluator.close()
