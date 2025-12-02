#!/usr/bin/env python3
"""
Contact Finder Pipeline Evaluation

Evaluates the full contact_finder.py pipeline against verified ground truth:
1. Runs the real pipeline (Serper + ZenRows + multi-source + LLM judgment)
2. Compares output against hidden ground truth
3. Measures discovery rate, person accuracy, LLM calibration

Metrics:
- Discovery Rate: % of companies where pipeline found any contact
- Person Accuracy: % where pipeline found the exact ground truth person
- Email Accuracy: % where email matches ground truth
- LLM Calibration (ECE): Expected Calibration Error
- Cost per Correct: Credits / correct contacts
"""

import asyncio
import os
import sys
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
import pandas as pd
import numpy as np

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "contact-finder"))

from harness.cache import EvaluationCache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Persona title patterns for filtering
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
class EvaluationRecord:
    """Single evaluation record"""
    company_name: str
    company_domain: str | None
    linkedin_company_url: str
    persona_type: str

    # Ground truth
    gt_name: str
    gt_title: str | None
    gt_email: str | None
    gt_linkedin_url: str | None
    gt_tier: str

    # Pipeline output
    pipeline_ran: bool = False
    found_any: bool = False
    found_correct_person: bool = False
    found_correct_email: bool = False

    # LLM outputs
    llm_confidence: float = 0.0
    llm_accepted: bool = False
    llm_reasoning: str = ""
    llm_red_flags: list[str] = field(default_factory=list)

    # Details
    best_contact_name: str | None = None
    best_contact_title: str | None = None
    best_contact_email: str | None = None
    best_contact_linkedin: str | None = None

    # Failure attribution
    failure_stage: str = ""  # search_failed, scrape_failed, wrong_person, wrong_title, etc.

    # Cost and performance
    cost_credits: float = 0.0
    latency_ms: float = 0.0
    stage_reached: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class EvaluationSummary:
    """Summary of evaluation results"""
    total_evaluated: int = 0
    pipeline_ran: int = 0

    # Core metrics
    discovery_rate: float = 0.0  # Found any contact
    person_accuracy: float = 0.0  # Found exact person
    email_accuracy: float = 0.0  # Email matches

    # LLM calibration
    expected_calibration_error: float = 0.0
    calibration_bins: dict = field(default_factory=dict)

    # By persona
    by_persona: dict = field(default_factory=dict)

    # By ground truth tier
    by_tier: dict = field(default_factory=dict)

    # Failure attribution
    failure_reasons: dict = field(default_factory=dict)

    # Cost
    total_credits: float = 0.0
    cost_per_correct: float = 0.0
    avg_latency_ms: float = 0.0

    # Targets
    targets_met: dict = field(default_factory=dict)


class ContactFinderEvaluator:
    """
    Evaluates the contact finder pipeline against ground truth.
    """

    def __init__(
        self,
        config_path: str = "contact-finder/config.yaml",
        cache_path: str = "./evaluation/data/cache.db"
    ):
        self.config_path = config_path
        self.cache = EvaluationCache(cache_path)
        self._finder = None

        # Ground truth data
        self.contacts_df: pd.DataFrame | None = None
        self.companies_df: pd.DataFrame | None = None

        # Evaluation targets
        self.targets = {
            "discovery_rate": 0.60,
            "person_accuracy": 0.40,
            "email_accuracy": 0.80,
            "ece": 0.15,
            "cost_per_correct": 0.20
        }

    async def _get_finder(self):
        """Get or create ContactFinder"""
        if self._finder is None:
            from contact_finder import ContactFinder
            self._finder = ContactFinder.from_config(self.config_path)
        return self._finder

    def load_ground_truth(
        self,
        contacts_path: str | Path,
        companies_path: str | Path | None = None
    ):
        """
        Load ground truth data.

        Args:
            contacts_path: Path to verified contacts parquet
            companies_path: Optional path to companies parquet
        """
        # Load contacts
        if str(contacts_path).endswith(".parquet"):
            self.contacts_df = pd.read_parquet(contacts_path)
        else:
            self.contacts_df = pd.read_csv(contacts_path)

        # Filter to verified contacts (include bronze for initial testing)
        if "tier" in self.contacts_df.columns:
            self.contacts_df = self.contacts_df[
                self.contacts_df["tier"].isin(["gold", "silver", "bronze"])
            ]

        logger.info(f"Loaded {len(self.contacts_df)} verified contacts")

        # Load companies if provided
        if companies_path:
            if str(companies_path).endswith(".parquet"):
                self.companies_df = pd.read_parquet(companies_path)
            else:
                self.companies_df = pd.read_csv(companies_path)

            logger.info(f"Loaded {len(self.companies_df)} companies")

    def _names_match(self, name1: str | None, name2: str | None) -> bool:
        """Check if two names match (fuzzy)"""
        if not name1 or not name2:
            return False

        n1 = name1.lower().strip()
        n2 = name2.lower().strip()

        # Exact match
        if n1 == n2:
            return True

        # One contains the other
        if n1 in n2 or n2 in n1:
            return True

        # Sequence matcher similarity
        ratio = SequenceMatcher(None, n1, n2).ratio()
        return ratio > 0.85

    def _linkedin_urls_match(self, url1: str | None, url2: str | None) -> bool:
        """Check if two LinkedIn URLs match"""
        if not url1 or not url2:
            return False

        def normalize(url):
            import re
            url = url.lower().rstrip("/")
            url = url.replace("http://", "https://")
            url = re.sub(r'\?.*$', '', url)
            return url

        return normalize(url1) == normalize(url2)

    def _emails_match(self, email1: str | None, email2: str | None) -> bool:
        """Check if two emails match"""
        if not email1 or not email2:
            return False
        return email1.lower().strip() == email2.lower().strip()

    def _title_matches_persona(self, title: str | None, persona: str) -> bool:
        """Check if a title matches a persona type"""
        if not title:
            return False

        title_lower = title.lower()
        patterns = PERSONA_TITLES.get(persona, [])

        return any(p.lower() in title_lower for p in patterns)

    def _attribute_failure(
        self,
        pipeline_result,
        gt_contact: dict,
        persona: str
    ) -> str:
        """Attribute why the pipeline failed"""
        if not pipeline_result:
            return "pipeline_error"

        if not pipeline_result.success:
            stage = getattr(pipeline_result, 'stage_reached', 'unknown')
            if stage == "linkedin":
                return "linkedin_failed"
            elif stage == "search":
                return "search_failed"
            elif stage == "enrich":
                return "enrich_failed"
            elif stage == "validate":
                return "validate_failed"
            else:
                return f"stage_{stage}_failed"

        if not pipeline_result.contacts:
            return "no_contacts"

        best = pipeline_result.best_contact
        if not best:
            return "no_best_contact"

        # Check what went wrong
        gt_name = gt_contact.get("contact_name", "")
        gt_linkedin = gt_contact.get("contact_linkedin_url", "")
        gt_email = gt_contact.get("contact_email", "")

        # Check person match
        if not self._names_match(best.name, gt_name):
            if not self._linkedin_urls_match(best.linkedin_url, gt_linkedin):
                # Check if found someone with right title
                if self._title_matches_persona(best.title, persona):
                    return "wrong_person_right_title"
                else:
                    return "wrong_person_wrong_title"

        # Person matches - check email
        if gt_email and best.email:
            if not self._emails_match(best.email, gt_email):
                return "email_mismatch"

        # Everything matched but was rejected
        if not getattr(pipeline_result, 'success', True):
            return "llm_rejected"

        return "success"

    async def evaluate_single(
        self,
        company: dict,
        gt_contact: dict,
        persona: str
    ) -> EvaluationRecord:
        """Evaluate pipeline for a single company-persona"""
        record = EvaluationRecord(
            company_name=company.get("company_name") or company.get("name", ""),
            company_domain=company.get("company_domain") or company.get("expected_domain"),
            linkedin_company_url=company.get("linkedin_company_url", ""),
            persona_type=persona,
            gt_name=gt_contact.get("contact_name", ""),
            gt_title=gt_contact.get("contact_title"),
            gt_email=gt_contact.get("contact_email"),
            gt_linkedin_url=gt_contact.get("contact_linkedin_url"),
            gt_tier=gt_contact.get("tier", "unknown")
        )

        # Get persona-specific titles
        target_titles = PERSONA_TITLES.get(persona, [])

        try:
            finder = await self._get_finder()
            start = datetime.now()

            result = await finder.find_contacts(
                company_name=record.company_name,
                domain=record.company_domain,
                target_titles=target_titles
            )

            record.latency_ms = (datetime.now() - start).total_seconds() * 1000
            record.pipeline_ran = True
            record.stage_reached = result.stage_reached
            record.cost_credits = result.total_cost_credits
            record.errors = result.errors

            # Check results
            record.found_any = result.success and len(result.contacts) > 0

            if record.found_any and result.best_contact:
                best = result.best_contact
                record.best_contact_name = best.name
                record.best_contact_title = best.title
                record.best_contact_email = best.email
                record.best_contact_linkedin = best.linkedin_url
                record.llm_confidence = best.confidence
                record.llm_reasoning = best.reasoning
                record.llm_red_flags = best.red_flags
                record.llm_accepted = best.confidence >= 50  # Assuming 50 is threshold

                # Check person match (by LinkedIn URL or name)
                record.found_correct_person = (
                    self._linkedin_urls_match(best.linkedin_url, record.gt_linkedin_url) or
                    self._names_match(best.name, record.gt_name)
                )

                # Check email match
                if record.gt_email:
                    record.found_correct_email = self._emails_match(best.email, record.gt_email)

            # Attribute failure
            record.failure_stage = self._attribute_failure(result, gt_contact, persona)

        except Exception as e:
            record.errors = [str(e)]
            record.failure_stage = "pipeline_exception"
            logger.error(f"Evaluation error for {record.company_name}: {e}")

        return record

    def _calculate_ece(self, records: list[EvaluationRecord]) -> tuple[float, dict]:
        """
        Calculate Expected Calibration Error.

        ECE measures how well the LLM's confidence predicts actual accuracy.
        Lower is better (0 = perfectly calibrated).
        """
        # Filter to records with predictions
        predictions = [
            (r.llm_confidence / 100, 1 if r.found_correct_person else 0)
            for r in records if r.pipeline_ran and r.found_any
        ]

        if not predictions:
            return 0.0, {}

        # Bin predictions by confidence
        bins = {}
        n_bins = 10

        for conf, correct in predictions:
            bin_idx = min(int(conf * n_bins), n_bins - 1)
            if bin_idx not in bins:
                bins[bin_idx] = {"count": 0, "correct": 0, "conf_sum": 0}
            bins[bin_idx]["count"] += 1
            bins[bin_idx]["correct"] += correct
            bins[bin_idx]["conf_sum"] += conf

        # Calculate ECE
        ece = 0.0
        n_total = len(predictions)
        bin_details = {}

        for bin_idx, data in bins.items():
            n = data["count"]
            accuracy = data["correct"] / n
            avg_conf = data["conf_sum"] / n

            ece += (n / n_total) * abs(accuracy - avg_conf)

            bin_details[f"{bin_idx * 10}-{(bin_idx + 1) * 10}%"] = {
                "count": n,
                "accuracy": accuracy,
                "avg_confidence": avg_conf,
                "gap": abs(accuracy - avg_conf)
            }

        return ece, bin_details

    def compute_summary(self, records: list[EvaluationRecord]) -> EvaluationSummary:
        """Compute summary metrics from evaluation records"""
        summary = EvaluationSummary()

        if not records:
            return summary

        summary.total_evaluated = len(records)
        summary.pipeline_ran = sum(1 for r in records if r.pipeline_ran)

        ran_records = [r for r in records if r.pipeline_ran]
        if not ran_records:
            return summary

        # Core metrics
        summary.discovery_rate = sum(1 for r in ran_records if r.found_any) / len(ran_records)
        summary.person_accuracy = sum(1 for r in ran_records if r.found_correct_person) / len(ran_records)

        # Email accuracy (only for records with GT email)
        email_records = [r for r in ran_records if r.gt_email]
        if email_records:
            summary.email_accuracy = sum(1 for r in email_records if r.found_correct_email) / len(email_records)

        # LLM calibration
        summary.expected_calibration_error, summary.calibration_bins = self._calculate_ece(ran_records)

        # By persona
        for persona in PERSONA_TITLES.keys():
            p_records = [r for r in ran_records if r.persona_type == persona]
            if p_records:
                summary.by_persona[persona] = {
                    "count": len(p_records),
                    "discovery_rate": sum(1 for r in p_records if r.found_any) / len(p_records),
                    "person_accuracy": sum(1 for r in p_records if r.found_correct_person) / len(p_records),
                }

        # By tier
        for tier in ["gold", "silver", "bronze"]:
            t_records = [r for r in ran_records if r.gt_tier == tier]
            if t_records:
                summary.by_tier[tier] = {
                    "count": len(t_records),
                    "discovery_rate": sum(1 for r in t_records if r.found_any) / len(t_records),
                    "person_accuracy": sum(1 for r in t_records if r.found_correct_person) / len(t_records),
                }

        # Failure attribution
        for r in ran_records:
            if r.failure_stage:
                summary.failure_reasons[r.failure_stage] = summary.failure_reasons.get(r.failure_stage, 0) + 1

        # Cost metrics
        summary.total_credits = sum(r.cost_credits for r in ran_records)
        correct_count = sum(1 for r in ran_records if r.found_correct_person)
        summary.cost_per_correct = summary.total_credits / correct_count if correct_count > 0 else float('inf')
        summary.avg_latency_ms = sum(r.latency_ms for r in ran_records) / len(ran_records)

        # Check targets
        summary.targets_met = {
            "discovery_rate": summary.discovery_rate >= self.targets["discovery_rate"],
            "person_accuracy": summary.person_accuracy >= self.targets["person_accuracy"],
            "email_accuracy": summary.email_accuracy >= self.targets["email_accuracy"],
            "ece": summary.expected_calibration_error <= self.targets["ece"],
            "cost_per_correct": summary.cost_per_correct <= self.targets["cost_per_correct"],
        }

        return summary

    async def evaluate(
        self,
        personas: list[str] | None = None,
        max_companies: int | None = None,
        max_concurrent: int = 3
    ) -> tuple[EvaluationSummary, list[EvaluationRecord]]:
        """
        Run full evaluation.

        Args:
            personas: List of personas to evaluate (default: all)
            max_companies: Limit number of companies
            max_concurrent: Max concurrent evaluations

        Returns:
            Tuple of (summary, detailed_records)
        """
        if self.contacts_df is None:
            raise ValueError("Load ground truth first with load_ground_truth()")

        personas = personas or list(PERSONA_TITLES.keys())

        # Get unique companies from contacts
        companies = self.contacts_df.groupby(
            ["company_name", "linkedin_company_url"]
        ).first().reset_index()

        if max_companies:
            companies = companies.head(max_companies)

        logger.info(f"Evaluating {len(companies)} companies for {len(personas)} personas")

        semaphore = asyncio.Semaphore(max_concurrent)
        records: list[EvaluationRecord] = []

        async def eval_company_persona(company_row, persona: str):
            async with semaphore:
                # Get ground truth contact for this persona
                gt_contacts = self.contacts_df[
                    (self.contacts_df["company_name"] == company_row["company_name"]) &
                    (self.contacts_df["persona_type"] == persona)
                ]

                if len(gt_contacts) == 0:
                    return None

                gt_contact = gt_contacts.iloc[0].to_dict()

                record = await self.evaluate_single(
                    company=company_row.to_dict(),
                    gt_contact=gt_contact,
                    persona=persona
                )

                return record

        # Create tasks
        tasks = []
        for _, company in companies.iterrows():
            for persona in personas:
                # Check if we have ground truth for this persona
                gt_exists = len(self.contacts_df[
                    (self.contacts_df["company_name"] == company["company_name"]) &
                    (self.contacts_df["persona_type"] == persona)
                ]) > 0

                if gt_exists:
                    tasks.append(eval_company_persona(company, persona))

        # Run evaluations
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Evaluation error: {r}")
            elif r is not None:
                records.append(r)

        # Compute summary
        summary = self.compute_summary(records)

        return summary, records

    def generate_report(
        self,
        summary: EvaluationSummary,
        records: list[EvaluationRecord],
        output_path: str | Path
    ):
        """Generate markdown evaluation report"""
        report = f"""# Contact Finder Pipeline Evaluation Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Actual | Target | Status |
|--------|--------|--------|--------|
| Discovery Rate | {summary.discovery_rate*100:.1f}% | {self.targets['discovery_rate']*100:.0f}% | {'PASS' if summary.targets_met['discovery_rate'] else 'FAIL'} |
| Person Accuracy | {summary.person_accuracy*100:.1f}% | {self.targets['person_accuracy']*100:.0f}% | {'PASS' if summary.targets_met['person_accuracy'] else 'FAIL'} |
| Email Accuracy | {summary.email_accuracy*100:.1f}% | {self.targets['email_accuracy']*100:.0f}% | {'PASS' if summary.targets_met['email_accuracy'] else 'FAIL'} |
| LLM Calibration (ECE) | {summary.expected_calibration_error:.3f} | <{self.targets['ece']} | {'PASS' if summary.targets_met['ece'] else 'FAIL'} |
| Cost per Correct | ${summary.cost_per_correct:.2f} | <${self.targets['cost_per_correct']:.2f} | {'PASS' if summary.targets_met['cost_per_correct'] else 'FAIL'} |

### Overall Stats

- Total Evaluated: {summary.total_evaluated}
- Pipeline Ran: {summary.pipeline_ran}
- Total Credits: {summary.total_credits:.1f}
- Avg Latency: {summary.avg_latency_ms:.0f}ms

## By Persona

| Persona | Count | Discovery Rate | Person Accuracy |
|---------|-------|----------------|-----------------|
"""
        for persona, stats in summary.by_persona.items():
            report += f"| {persona} | {stats['count']} | {stats['discovery_rate']*100:.1f}% | {stats['person_accuracy']*100:.1f}% |\n"

        report += """
## By Ground Truth Tier

| Tier | Count | Discovery Rate | Person Accuracy |
|------|-------|----------------|-----------------|
"""
        for tier, stats in summary.by_tier.items():
            report += f"| {tier} | {stats['count']} | {stats['discovery_rate']*100:.1f}% | {stats['person_accuracy']*100:.1f}% |\n"

        report += """
## Failure Attribution

| Reason | Count | % |
|--------|-------|---|
"""
        total_failures = sum(summary.failure_reasons.values())
        for reason, count in sorted(summary.failure_reasons.items(), key=lambda x: -x[1]):
            pct = count / total_failures * 100 if total_failures > 0 else 0
            report += f"| {reason} | {count} | {pct:.1f}% |\n"

        report += """
## LLM Calibration Analysis

| Confidence Bin | Count | Actual Accuracy | Expected | Gap |
|----------------|-------|-----------------|----------|-----|
"""
        for bin_name, data in sorted(summary.calibration_bins.items()):
            report += f"| {bin_name} | {data['count']} | {data['accuracy']*100:.1f}% | {data['avg_confidence']*100:.1f}% | {data['gap']*100:.1f}% |\n"

        report += f"""
ECE = {summary.expected_calibration_error:.3f} ({'Good' if summary.expected_calibration_error < 0.1 else 'Needs improvement'})

## Sample Failures

"""
        failures = [r for r in records if not r.found_correct_person][:10]
        for r in failures:
            report += f"- **{r.company_name}** ({r.persona_type})\n"
            report += f"  - Ground truth: {r.gt_name} ({r.gt_title})\n"
            report += f"  - Pipeline found: {r.best_contact_name} ({r.best_contact_title})\n"
            report += f"  - Failure: {r.failure_stage}\n\n"

        report += """
## Sample Successes

"""
        successes = [r for r in records if r.found_correct_person][:10]
        for r in successes:
            report += f"- **{r.company_name}** ({r.persona_type})\n"
            report += f"  - Found: {r.best_contact_name} ({r.best_contact_title})\n"
            report += f"  - Confidence: {r.llm_confidence:.0f}\n\n"

        # Write report
        with open(output_path, "w") as f:
            f.write(report)

        logger.info(f"Wrote evaluation report to {output_path}")

        # Also save detailed records
        records_df = pd.DataFrame([asdict(r) for r in records])
        records_path = str(output_path).replace(".md", "_details.parquet")
        records_df.to_parquet(records_path, index=False)
        logger.info(f"Wrote detailed records to {records_path}")

    async def close(self):
        """Close finder client"""
        if self._finder:
            await self._finder.close()


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate Contact Finder Pipeline")
    parser.add_argument("--contacts", default="./evaluation/data/contacts_truth.parquet",
                        help="Path to contacts ground truth")
    parser.add_argument("--companies", default=None,
                        help="Path to companies file (optional)")
    parser.add_argument("--config", default="contact-finder/config.yaml",
                        help="Contact finder config path")
    parser.add_argument("--output", default="./evaluation/data/pipeline_eval_report.md",
                        help="Output report path")
    parser.add_argument("--personas", nargs="+", default=None,
                        help="Personas to evaluate (default: all)")
    parser.add_argument("--max-companies", type=int, default=None,
                        help="Max companies to evaluate")
    parser.add_argument("--concurrent", type=int, default=3,
                        help="Max concurrent evaluations")

    args = parser.parse_args()

    evaluator = ContactFinderEvaluator(config_path=args.config)

    try:
        evaluator.load_ground_truth(
            contacts_path=args.contacts,
            companies_path=args.companies
        )

        summary, records = await evaluator.evaluate(
            personas=args.personas,
            max_companies=args.max_companies,
            max_concurrent=args.concurrent
        )

        evaluator.generate_report(summary, records, args.output)

        # Print summary
        print("\n=== Contact Finder Pipeline Evaluation ===")
        print(f"Discovery Rate: {summary.discovery_rate*100:.1f}% (target: {evaluator.targets['discovery_rate']*100:.0f}%)")
        print(f"Person Accuracy: {summary.person_accuracy*100:.1f}% (target: {evaluator.targets['person_accuracy']*100:.0f}%)")
        print(f"Email Accuracy: {summary.email_accuracy*100:.1f}% (target: {evaluator.targets['email_accuracy']*100:.0f}%)")
        print(f"LLM Calibration (ECE): {summary.expected_calibration_error:.3f} (target: <{evaluator.targets['ece']})")
        print(f"Cost per Correct: ${summary.cost_per_correct:.2f} (target: <${evaluator.targets['cost_per_correct']:.2f})")

        passed = sum(summary.targets_met.values())
        print(f"\nTargets: {passed}/{len(summary.targets_met)} passed")

    finally:
        await evaluator.close()


if __name__ == "__main__":
    asyncio.run(main())
