#!/usr/bin/env python3
"""
Minimal Configuration Test

Tests if the minimal cost configuration can achieve good results:
- Scrapin (FREE LinkedIn enrichment)
- ZenRows (web scraping)
- LLM judgment (GPT-4o-mini)

Hypothesis: Can we achieve good contact finding with just:
1. Get Scrapin employee list for company
2. For each employee matching target title:
   - Scrape their LinkedIn profile via ZenRows
   - Pass profile content + company context to LLM
   - LLM decides: accept/reject with confidence
3. Compare LLM decisions to ground truth

This tests the core question: Can cheaper methods + LLM judgment
replace expensive enrichment APIs?
"""

import asyncio
import os
import sys
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
import pandas as pd
import re

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "contact-finder"))

from harness.cache import EvaluationCache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


PERSONA_TITLES = {
    "owner_operator": ["Owner", "Founder", "CEO", "President", "Principal"],
    "vp_marketing": ["VP Marketing", "Head of Marketing", "CMO", "Marketing Director"],
    "vp_sales": ["VP Sales", "Head of Sales", "CRO", "Sales Director"]
}


@dataclass
class MinimalTestResult:
    """Result of minimal config test for one company"""
    company_name: str
    company_domain: str | None
    linkedin_company_url: str
    persona_type: str

    # Ground truth
    gt_name: str
    gt_title: str | None
    gt_email: str | None
    gt_linkedin_url: str | None

    # Scrapin results
    scrapin_found_any: bool = False
    scrapin_candidates: int = 0
    scrapin_title_matches: int = 0

    # LLM judgment
    llm_evaluated: int = 0
    llm_accepted: int = 0
    llm_best_confidence: float = 0.0
    llm_best_name: str | None = None
    llm_best_title: str | None = None
    llm_reasoning: str = ""

    # Accuracy
    found_correct_person: bool = False
    llm_accepted_correct: bool = False  # LLM said yes AND it was correct
    llm_rejected_correct: bool = False  # LLM said no on correct (false negative)
    llm_accepted_wrong: bool = False    # LLM said yes on wrong (false positive)

    # Cost
    scrapin_credits: float = 0.0
    zenrows_credits: float = 0.0
    llm_tokens: int = 0
    total_cost_estimate: float = 0.0

    # Errors
    errors: list[str] = field(default_factory=list)


@dataclass
class MinimalTestSummary:
    """Summary of minimal config test"""
    total_tested: int = 0

    # Scrapin coverage
    scrapin_coverage: float = 0.0
    scrapin_title_match_rate: float = 0.0

    # LLM performance
    llm_precision: float = 0.0  # correct / accepted
    llm_recall: float = 0.0    # accepted correct / total correct
    llm_f1: float = 0.0

    # Calibration
    calibration_by_confidence: dict = field(default_factory=dict)

    # Overall accuracy
    person_accuracy: float = 0.0
    discovery_rate: float = 0.0

    # Cost
    avg_cost_per_company: float = 0.0
    cost_per_correct: float = 0.0

    # By persona
    by_persona: dict = field(default_factory=dict)


class MinimalConfigTester:
    """
    Tests minimal cost configuration against ground truth.
    """

    def __init__(
        self,
        scrapin_api_key: str | None = None,
        zenrows_api_key: str | None = None,
        openai_api_key: str | None = None,
        cache_path: str = "./evaluation/data/cache.db"
    ):
        self.scrapin_api_key = scrapin_api_key or os.environ.get("SCRAPIN_API_KEY")
        self.zenrows_api_key = zenrows_api_key or os.environ.get("ZENROWS_API_KEY")
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")

        self.cache = EvaluationCache(cache_path)

        self._scrapin = None
        self._llm = None

        # Ground truth
        self.contacts_df: pd.DataFrame | None = None

    async def _get_scrapin(self):
        """Get Scrapin client"""
        if self._scrapin is None and self.scrapin_api_key:
            from modules.enrichment.scrapin import ScrapinClient
            self._scrapin = ScrapinClient(self.scrapin_api_key)
        return self._scrapin

    async def _get_llm(self):
        """Get LLM provider"""
        if self._llm is None and self.openai_api_key:
            from modules.llm.openai_provider import OpenAIProvider
            self._llm = OpenAIProvider(
                api_key=self.openai_api_key,
                model="gpt-4o-mini"
            )
        return self._llm

    async def _scrape_linkedin_profile(self, linkedin_url: str) -> str | None:
        """Scrape LinkedIn profile via ZenRows"""
        if not self.zenrows_api_key:
            return None

        cache_key = f"zenrows:{linkedin_url}"
        cached = self.cache.get("zenrows", cache_key)
        if cached:
            return cached.get("content")

        import aiohttp

        params = {
            "apikey": self.zenrows_api_key,
            "url": linkedin_url,
            "js_render": "true",
            "wait": "3000"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Cache
                        self.cache.set("zenrows", cache_key, response={"content": content})
                        return content
        except Exception as e:
            logger.debug(f"ZenRows error for {linkedin_url}: {e}")

        return None

    async def _llm_evaluate_contact(
        self,
        company_name: str,
        company_domain: str | None,
        candidate_name: str,
        candidate_title: str | None,
        profile_content: str | None,
        target_persona: str
    ) -> tuple[bool, float, str]:
        """
        Use LLM to evaluate if contact is correct for target persona.

        Returns: (accept, confidence, reasoning)
        """
        llm = await self._get_llm()
        if not llm:
            return False, 0.0, "No LLM available"

        target_titles = PERSONA_TITLES.get(target_persona, [])

        prompt = f"""You are evaluating whether a contact is correct for a company.

Company: {company_name}
Domain: {company_domain or 'unknown'}
Target Role: {target_persona} (looking for: {', '.join(target_titles[:3])})

Candidate Contact:
- Name: {candidate_name}
- Title: {candidate_title or 'unknown'}

{f'LinkedIn Profile Content (truncated):{chr(10)}{profile_content[:2000]}' if profile_content else 'No profile content available.'}

Questions to answer:
1. Does this person appear to work at {company_name}?
2. Does their title match the target role ({target_persona})?
3. Is there any evidence this might be the wrong person or outdated info?

Respond in this exact format:
ACCEPT: [yes/no]
CONFIDENCE: [0-100]
REASONING: [1-2 sentences]
"""

        try:
            response = await llm.complete(prompt, max_tokens=200)

            # Parse response
            accept = "yes" in response.lower().split("accept:")[1][:20] if "accept:" in response.lower() else False

            conf_match = re.search(r'confidence:\s*(\d+)', response.lower())
            confidence = float(conf_match.group(1)) if conf_match else 50.0

            reasoning = ""
            if "reasoning:" in response.lower():
                reasoning = response.split("reasoning:")[-1].strip()[:200]

            return accept, confidence / 100, reasoning

        except Exception as e:
            logger.debug(f"LLM error: {e}")
            return False, 0.0, str(e)

    def load_ground_truth(self, contacts_path: str | Path):
        """Load ground truth contacts"""
        if str(contacts_path).endswith(".parquet"):
            self.contacts_df = pd.read_parquet(contacts_path)
        else:
            self.contacts_df = pd.read_csv(contacts_path)

        # Filter to verified contacts
        if "tier" in self.contacts_df.columns:
            self.contacts_df = self.contacts_df[
                self.contacts_df["tier"].isin(["gold", "silver"])
            ]

        logger.info(f"Loaded {len(self.contacts_df)} verified contacts")

    def _names_match(self, name1: str | None, name2: str | None) -> bool:
        """Check if names match"""
        if not name1 or not name2:
            return False
        n1, n2 = name1.lower().strip(), name2.lower().strip()
        if n1 == n2 or n1 in n2 or n2 in n1:
            return True
        return SequenceMatcher(None, n1, n2).ratio() > 0.85

    def _title_matches_persona(self, title: str | None, persona: str) -> bool:
        """Check if title matches persona"""
        if not title:
            return False
        title_lower = title.lower()
        return any(p.lower() in title_lower for p in PERSONA_TITLES.get(persona, []))

    async def test_single(
        self,
        company: dict,
        gt_contact: dict,
        persona: str
    ) -> MinimalTestResult:
        """Test minimal config for one company"""
        result = MinimalTestResult(
            company_name=company.get("company_name") or company.get("name", ""),
            company_domain=company.get("company_domain") or company.get("expected_domain"),
            linkedin_company_url=company.get("linkedin_company_url", ""),
            persona_type=persona,
            gt_name=gt_contact.get("contact_name", ""),
            gt_title=gt_contact.get("contact_title"),
            gt_email=gt_contact.get("contact_email"),
            gt_linkedin_url=gt_contact.get("contact_linkedin_url")
        )

        # Step 1: Get Scrapin employees (via person matching since no employees endpoint)
        scrapin = await self._get_scrapin()
        candidates = []

        if scrapin:
            try:
                # Try to find people with common founder/owner titles
                for title in PERSONA_TITLES.get(persona, [])[:2]:
                    profile = await scrapin.match_person(
                        first_name=title.split()[0] if " " in title else title,
                        company_name=result.company_name
                    )
                    if profile and profile.full_name:
                        candidates.append({
                            "name": profile.full_name,
                            "title": profile.title,
                            "linkedin_url": profile.linkedin_url
                        })
                        result.scrapin_credits += 1

            except Exception as e:
                result.errors.append(f"Scrapin: {e}")

        result.scrapin_found_any = len(candidates) > 0
        result.scrapin_candidates = len(candidates)

        # Filter to title matches
        title_matches = [c for c in candidates if self._title_matches_persona(c.get("title"), persona)]
        result.scrapin_title_matches = len(title_matches)

        # Step 2: For each candidate, scrape profile and evaluate with LLM
        best_confidence = 0.0
        best_candidate = None
        accepted_any = False

        for candidate in title_matches[:3]:  # Limit to top 3
            # Scrape LinkedIn profile
            profile_content = None
            if candidate.get("linkedin_url"):
                profile_content = await self._scrape_linkedin_profile(candidate["linkedin_url"])
                result.zenrows_credits += 0.01  # Approximate cost

            # LLM evaluation
            accept, confidence, reasoning = await self._llm_evaluate_contact(
                company_name=result.company_name,
                company_domain=result.company_domain,
                candidate_name=candidate.get("name", ""),
                candidate_title=candidate.get("title"),
                profile_content=profile_content,
                target_persona=persona
            )

            result.llm_evaluated += 1
            result.llm_tokens += 200  # Approximate

            if accept:
                result.llm_accepted += 1
                accepted_any = True

            if confidence > best_confidence:
                best_confidence = confidence
                best_candidate = candidate
                result.llm_best_confidence = confidence
                result.llm_best_name = candidate.get("name")
                result.llm_best_title = candidate.get("title")
                result.llm_reasoning = reasoning

        # Check accuracy
        is_correct = self._names_match(result.llm_best_name, result.gt_name)
        result.found_correct_person = is_correct

        if accepted_any:
            if is_correct:
                result.llm_accepted_correct = True
            else:
                result.llm_accepted_wrong = True
        else:
            if is_correct:
                result.llm_rejected_correct = True  # False negative

        # Estimate total cost
        result.total_cost_estimate = (
            result.scrapin_credits * 0.01 +  # Scrapin ~$0.01/credit
            result.zenrows_credits +          # ZenRows ~$0.01/request
            result.llm_tokens * 0.00001       # GPT-4o-mini ~$0.01/1K tokens
        )

        return result

    def compute_summary(self, results: list[MinimalTestResult]) -> MinimalTestSummary:
        """Compute summary statistics"""
        summary = MinimalTestSummary()
        summary.total_tested = len(results)

        if not results:
            return summary

        # Scrapin coverage
        summary.scrapin_coverage = sum(1 for r in results if r.scrapin_found_any) / len(results)
        has_candidates = [r for r in results if r.scrapin_candidates > 0]
        if has_candidates:
            summary.scrapin_title_match_rate = sum(r.scrapin_title_matches for r in has_candidates) / sum(r.scrapin_candidates for r in has_candidates)

        # LLM precision/recall
        accepted_correct = sum(1 for r in results if r.llm_accepted_correct)
        accepted_wrong = sum(1 for r in results if r.llm_accepted_wrong)
        rejected_correct = sum(1 for r in results if r.llm_rejected_correct)

        total_accepted = accepted_correct + accepted_wrong
        total_correct = accepted_correct + rejected_correct

        summary.llm_precision = accepted_correct / total_accepted if total_accepted > 0 else 0
        summary.llm_recall = accepted_correct / total_correct if total_correct > 0 else 0

        if summary.llm_precision + summary.llm_recall > 0:
            summary.llm_f1 = 2 * summary.llm_precision * summary.llm_recall / (summary.llm_precision + summary.llm_recall)

        # Overall accuracy
        summary.person_accuracy = sum(1 for r in results if r.found_correct_person) / len(results)
        summary.discovery_rate = sum(1 for r in results if r.llm_accepted > 0) / len(results)

        # Cost
        total_cost = sum(r.total_cost_estimate for r in results)
        summary.avg_cost_per_company = total_cost / len(results)
        correct_count = sum(1 for r in results if r.llm_accepted_correct)
        summary.cost_per_correct = total_cost / correct_count if correct_count > 0 else float('inf')

        # By persona
        for persona in PERSONA_TITLES.keys():
            p_results = [r for r in results if r.persona_type == persona]
            if p_results:
                p_accepted_correct = sum(1 for r in p_results if r.llm_accepted_correct)
                p_accepted = sum(1 for r in p_results if r.llm_accepted > 0)
                summary.by_persona[persona] = {
                    "count": len(p_results),
                    "scrapin_coverage": sum(1 for r in p_results if r.scrapin_found_any) / len(p_results),
                    "llm_precision": p_accepted_correct / p_accepted if p_accepted > 0 else 0,
                    "discovery_rate": p_accepted / len(p_results)
                }

        return summary

    async def run_test(
        self,
        personas: list[str] | None = None,
        max_companies: int | None = None,
        max_concurrent: int = 3
    ) -> tuple[MinimalTestSummary, list[MinimalTestResult]]:
        """
        Run minimal config test.

        Args:
            personas: Personas to test
            max_companies: Limit companies
            max_concurrent: Max concurrent tests

        Returns:
            Tuple of (summary, results)
        """
        if self.contacts_df is None:
            raise ValueError("Load ground truth first")

        personas = personas or list(PERSONA_TITLES.keys())

        companies = self.contacts_df.groupby(
            ["company_name", "linkedin_company_url"]
        ).first().reset_index()

        if max_companies:
            companies = companies.head(max_companies)

        logger.info(f"Testing minimal config on {len(companies)} companies")

        semaphore = asyncio.Semaphore(max_concurrent)
        all_results: list[MinimalTestResult] = []

        async def test_one(company_row, persona: str):
            async with semaphore:
                gt_contacts = self.contacts_df[
                    (self.contacts_df["company_name"] == company_row["company_name"]) &
                    (self.contacts_df["persona_type"] == persona)
                ]
                if len(gt_contacts) == 0:
                    return None

                gt_contact = gt_contacts.iloc[0].to_dict()
                return await self.test_single(company_row.to_dict(), gt_contact, persona)

        # Create tasks
        tasks = []
        for _, company in companies.iterrows():
            for persona in personas:
                gt_exists = len(self.contacts_df[
                    (self.contacts_df["company_name"] == company["company_name"]) &
                    (self.contacts_df["persona_type"] == persona)
                ]) > 0

                if gt_exists:
                    tasks.append(test_one(company, persona))

        # Run tests
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Test error: {r}")
            elif r is not None:
                all_results.append(r)

        # Compute summary
        summary = self.compute_summary(all_results)

        return summary, all_results

    def generate_report(
        self,
        summary: MinimalTestSummary,
        results: list[MinimalTestResult],
        output_path: str | Path
    ):
        """Generate test report"""
        report = f"""# Minimal Configuration Test Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Configuration Tested

- **Scrapin**: FREE LinkedIn enrichment
- **ZenRows**: Web scraping (~$0.01/request)
- **LLM**: GPT-4o-mini (~$0.01/1K tokens)

## Summary

| Metric | Value |
|--------|-------|
| Total Tested | {summary.total_tested} |
| Scrapin Coverage | {summary.scrapin_coverage*100:.1f}% |
| Discovery Rate | {summary.discovery_rate*100:.1f}% |
| Person Accuracy | {summary.person_accuracy*100:.1f}% |

## LLM Performance

| Metric | Value |
|--------|-------|
| LLM Precision | {summary.llm_precision*100:.1f}% |
| LLM Recall | {summary.llm_recall*100:.1f}% |
| LLM F1 Score | {summary.llm_f1*100:.1f}% |

## Cost Analysis

| Metric | Value |
|--------|-------|
| Avg Cost/Company | ${summary.avg_cost_per_company:.4f} |
| Cost/Correct Contact | ${summary.cost_per_correct:.4f} |

## By Persona

| Persona | Count | Scrapin Coverage | LLM Precision | Discovery Rate |
|---------|-------|------------------|---------------|----------------|
"""
        for persona, data in summary.by_persona.items():
            report += f"| {persona} | {data['count']} | {data['scrapin_coverage']*100:.1f}% | {data['llm_precision']*100:.1f}% | {data['discovery_rate']*100:.1f}% |\n"

        report += """
## Conclusions

"""
        if summary.llm_precision >= 0.7:
            report += "- LLM precision is good (>70%) - reliable when it says yes\n"
        else:
            report += "- LLM precision needs improvement (<70%) - too many false positives\n"

        if summary.llm_recall >= 0.6:
            report += "- LLM recall is acceptable (>60%) - finding most correct contacts\n"
        else:
            report += "- LLM recall is low (<60%) - missing too many correct contacts\n"

        if summary.cost_per_correct < 0.05:
            report += f"- Cost is very low (${summary.cost_per_correct:.4f}/correct) - highly efficient\n"
        else:
            report += f"- Cost is moderate (${summary.cost_per_correct:.4f}/correct) - consider optimization\n"

        # Write report
        with open(output_path, "w") as f:
            f.write(report)

        logger.info(f"Wrote report to {output_path}")

        # Save detailed results
        results_df = pd.DataFrame([asdict(r) for r in results])
        results_path = str(output_path).replace(".md", "_details.parquet")
        results_df.to_parquet(results_path, index=False)

    async def close(self):
        """Close clients"""
        if self._scrapin:
            await self._scrapin.close()


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Minimal Configuration")
    parser.add_argument("--contacts", default="./evaluation/data/contacts_truth.parquet",
                        help="Path to contacts ground truth")
    parser.add_argument("--output", default="./evaluation/data/minimal_config_report.md",
                        help="Output report path")
    parser.add_argument("--personas", nargs="+", default=None,
                        help="Personas to test")
    parser.add_argument("--max-companies", type=int, default=None,
                        help="Max companies to test")

    args = parser.parse_args()

    tester = MinimalConfigTester()

    try:
        tester.load_ground_truth(args.contacts)

        summary, results = await tester.run_test(
            personas=args.personas,
            max_companies=args.max_companies
        )

        tester.generate_report(summary, results, args.output)

        # Print summary
        print("\n=== Minimal Configuration Test ===")
        print(f"Scrapin Coverage: {summary.scrapin_coverage*100:.1f}%")
        print(f"LLM Precision: {summary.llm_precision*100:.1f}%")
        print(f"LLM Recall: {summary.llm_recall*100:.1f}%")
        print(f"LLM F1: {summary.llm_f1*100:.1f}%")
        print(f"Cost/Correct: ${summary.cost_per_correct:.4f}")

    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
