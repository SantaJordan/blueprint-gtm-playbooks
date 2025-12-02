#!/usr/bin/env python3
"""
Enrichment Source Comparison

Tests each enrichment source independently against ground truth:
- Scrapin
- Blitz
- Ocean.io
- LeadMagic
- Exa
- ZoomInfo scrape

Measures for each source:
- Coverage: % of companies where source returns any data
- Person Match Rate: % where source finds the verified contact
- Email Match Rate: % where email matches ground truth
- Cost per Hit: Credits / successful finds
- Latency: Average API response time
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

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "contact-finder"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "domain-resolver"))

from harness.cache import EvaluationCache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Persona title patterns
PERSONA_TITLES = {
    "owner_operator": ["Owner", "Founder", "CEO", "President", "Principal", "Managing Partner"],
    "vp_marketing": ["VP Marketing", "Head of Marketing", "CMO", "Marketing Director"],
    "vp_sales": ["VP Sales", "Head of Sales", "CRO", "Sales Director"]
}


@dataclass
class SourceTestResult:
    """Result of testing a single source for one company"""
    company_name: str
    persona_type: str
    source_name: str

    # What we were looking for
    gt_name: str
    gt_email: str | None
    gt_linkedin_url: str | None

    # What the source returned
    returned_any: bool = False
    returned_count: int = 0
    found_correct_person: bool = False
    found_correct_email: bool = False

    # Best match details
    best_name: str | None = None
    best_title: str | None = None
    best_email: str | None = None
    best_linkedin: str | None = None

    # Performance
    credits_used: float = 0.0
    latency_ms: float = 0.0
    error: str | None = None


@dataclass
class SourceSummary:
    """Summary for one source"""
    source_name: str
    total_tested: int = 0

    # Core metrics
    coverage: float = 0.0  # % returned any data
    person_match_rate: float = 0.0  # % found correct person
    email_match_rate: float = 0.0  # % found correct email

    # Cost
    total_credits: float = 0.0
    cost_per_hit: float = 0.0
    avg_latency_ms: float = 0.0

    # By persona
    by_persona: dict = field(default_factory=dict)


class SourceComparer:
    """
    Compares enrichment sources against ground truth.
    """

    def __init__(
        self,
        cache_path: str = "./evaluation/data/cache.db"
    ):
        self.cache = EvaluationCache(cache_path)

        # API clients (initialized lazily)
        self._scrapin = None
        self._blitz = None
        self._ocean = None
        self._leadmagic = None
        self._exa = None

        # Ground truth
        self.contacts_df: pd.DataFrame | None = None

    def _get_api_key(self, name: str) -> str | None:
        """Get API key from environment"""
        key_names = {
            "scrapin": "SCRAPIN_API_KEY",
            "blitz": "BLITZ_API_KEY",
            "ocean": "OCEAN_API_KEY",
            "leadmagic": "LEADMAGIC_API_KEY",
            "exa": "EXA_API_KEY"
        }
        return os.environ.get(key_names.get(name, ""))

    async def _get_scrapin(self):
        """Get Scrapin client"""
        if self._scrapin is None:
            api_key = self._get_api_key("scrapin")
            if api_key:
                from modules.enrichment.scrapin import ScrapinClient
                self._scrapin = ScrapinClient(api_key)
        return self._scrapin

    async def _get_blitz(self):
        """Get Blitz client"""
        if self._blitz is None:
            api_key = self._get_api_key("blitz")
            if api_key:
                from modules.enrichment.blitz import BlitzClient
                self._blitz = BlitzClient(api_key)
        return self._blitz

    async def _get_ocean(self):
        """Get Ocean client"""
        if self._ocean is None:
            api_key = self._get_api_key("ocean")
            if api_key:
                from build_contact_truth import OceanPeopleClient
                self._ocean = OceanPeopleClient(api_key)
        return self._ocean

    def load_ground_truth(self, contacts_path: str | Path):
        """Load ground truth contacts"""
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

    def _names_match(self, name1: str | None, name2: str | None) -> bool:
        """Check if two names match"""
        if not name1 or not name2:
            return False
        n1, n2 = name1.lower().strip(), name2.lower().strip()
        if n1 == n2 or n1 in n2 or n2 in n1:
            return True
        return SequenceMatcher(None, n1, n2).ratio() > 0.85

    def _linkedin_match(self, url1: str | None, url2: str | None) -> bool:
        """Check if LinkedIn URLs match"""
        if not url1 or not url2:
            return False
        import re
        def norm(u):
            u = u.lower().rstrip("/")
            return re.sub(r'\?.*$', '', u)
        return norm(url1) == norm(url2)

    def _email_match(self, e1: str | None, e2: str | None) -> bool:
        """Check if emails match"""
        if not e1 or not e2:
            return False
        return e1.lower().strip() == e2.lower().strip()

    def _title_matches_persona(self, title: str | None, persona: str) -> bool:
        """Check if title matches persona"""
        if not title:
            return False
        title_lower = title.lower()
        return any(p.lower() in title_lower for p in PERSONA_TITLES.get(persona, []))

    async def test_scrapin(
        self,
        company: dict,
        gt_contact: dict,
        persona: str
    ) -> SourceTestResult:
        """Test Scrapin for a company"""
        result = SourceTestResult(
            company_name=company.get("company_name") or company.get("name", ""),
            persona_type=persona,
            source_name="scrapin",
            gt_name=gt_contact.get("contact_name", ""),
            gt_email=gt_contact.get("contact_email"),
            gt_linkedin_url=gt_contact.get("contact_linkedin_url")
        )

        # Check cache first
        linkedin_url = company.get("linkedin_company_url", "")
        cache_key = f"scrapin_employees:{linkedin_url}"
        cached = self.cache.get("scrapin", cache_key)

        if cached:
            result.returned_any = len(cached) > 0
            result.returned_count = len(cached)
            # Check for matches
            for c in cached:
                if self._names_match(c.get("name"), result.gt_name) or \
                   self._linkedin_match(c.get("linkedin_url"), result.gt_linkedin_url):
                    result.found_correct_person = True
                    result.best_name = c.get("name")
                    result.best_title = c.get("title")
                    result.best_email = c.get("email")
                    result.best_linkedin = c.get("linkedin_url")
                    if self._email_match(c.get("email"), result.gt_email):
                        result.found_correct_email = True
                    break
            return result

        # Try API call - use profile endpoint with LinkedIn URL
        linkedin_url = gt_contact.get("contact_linkedin_url")
        if not linkedin_url:
            result.error = "No LinkedIn URL in ground truth"
            return result

        try:
            import aiohttp
            start = datetime.now()

            scrapin_key = self._get_api_key("scrapin")
            if not scrapin_key:
                result.error = "No API key"
                return result

            # Call Scrapin profile API directly
            url = "https://api.scrapin.io/v1/enrichment/profile"
            params = {
                "apikey": scrapin_key,
                "linkedInUrl": linkedin_url
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    result.latency_ms = (datetime.now() - start).total_seconds() * 1000
                    result.credits_used = 1

                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("success") and data.get("person"):
                            person = data["person"]
                            full_name = f"{person.get('firstName', '')} {person.get('lastName', '')}".strip()
                            result.returned_any = True
                            result.returned_count = 1
                            result.best_name = full_name
                            result.best_title = person.get("headline")
                            result.best_linkedin = linkedin_url

                            if self._names_match(full_name, result.gt_name):
                                result.found_correct_person = True

                            # Cache result
                            self.cache.set("scrapin", cache_key, response=[{
                                "name": full_name,
                                "title": person.get("headline"),
                                "linkedin_url": linkedin_url
                            }])
                    else:
                        error_text = await resp.text()
                        result.error = f"API error {resp.status}: {error_text[:100]}"

        except Exception as e:
            result.error = str(e)

        return result

    async def test_blitz(
        self,
        company: dict,
        gt_contact: dict,
        persona: str
    ) -> SourceTestResult:
        """Test Blitz for a company"""
        result = SourceTestResult(
            company_name=company.get("company_name") or company.get("name", ""),
            persona_type=persona,
            source_name="blitz",
            gt_name=gt_contact.get("contact_name", ""),
            gt_email=gt_contact.get("contact_email"),
            gt_linkedin_url=gt_contact.get("contact_linkedin_url")
        )

        linkedin_url = company.get("linkedin_company_url", "")
        cache_key = f"{linkedin_url}:{persona}:False"

        # Check cache
        cached = self.cache.get("blitz_waterfall", cache_key)
        if cached:
            contacts = cached.get("contacts", [])
            result.returned_any = len(contacts) > 0
            result.returned_count = len(contacts)
            result.credits_used = cached.get("credits", 0)

            for c in contacts:
                if self._names_match(c.get("name"), result.gt_name) or \
                   self._linkedin_match(c.get("linkedin_url"), result.gt_linkedin_url):
                    result.found_correct_person = True
                    result.best_name = c.get("name")
                    result.best_title = c.get("title")
                    result.best_email = c.get("email")
                    result.best_linkedin = c.get("linkedin_url")
                    if self._email_match(c.get("email"), result.gt_email):
                        result.found_correct_email = True
                    break

            return result

        # Try API
        client = await self._get_blitz()
        if not client:
            result.error = "No API key"
            return result

        try:
            start = datetime.now()
            titles = PERSONA_TITLES.get(persona, [])
            contacts = await client.waterfall_icp(
                linkedin_company_url=linkedin_url,
                titles=titles,
                max_results=5
            )
            result.latency_ms = (datetime.now() - start).total_seconds() * 1000
            result.credits_used = len(contacts)

            result.returned_any = len(contacts) > 0
            result.returned_count = len(contacts)

            for c in contacts:
                if self._names_match(c.name, result.gt_name) or \
                   self._linkedin_match(c.linkedin_url, result.gt_linkedin_url):
                    result.found_correct_person = True
                    result.best_name = c.name
                    result.best_title = c.title
                    result.best_email = c.email
                    result.best_linkedin = c.linkedin_url
                    if self._email_match(c.email, result.gt_email):
                        result.found_correct_email = True
                    break

            # Cache
            self.cache.set("blitz_waterfall", cache_key, response={
                "contacts": [{"name": c.name, "title": c.title, "email": c.email, "linkedin_url": c.linkedin_url} for c in contacts],
                "credits": len(contacts)
            })

        except Exception as e:
            result.error = str(e)

        return result

    async def test_ocean(
        self,
        company: dict,
        gt_contact: dict,
        persona: str
    ) -> SourceTestResult:
        """Test Ocean.io for a company"""
        result = SourceTestResult(
            company_name=company.get("company_name") or company.get("name", ""),
            persona_type=persona,
            source_name="ocean",
            gt_name=gt_contact.get("contact_name", ""),
            gt_email=gt_contact.get("contact_email"),
            gt_linkedin_url=gt_contact.get("contact_linkedin_url")
        )

        cache_key = f"{result.company_name}:{persona}"
        cached = self.cache.get("ocean_people", cache_key)

        if cached:
            result.returned_any = len(cached) > 0
            result.returned_count = len(cached)
            result.credits_used = 1 if cached else 0

            for c in cached:
                if self._names_match(c.get("name"), result.gt_name) or \
                   self._linkedin_match(c.get("linkedin_url"), result.gt_linkedin_url):
                    result.found_correct_person = True
                    result.best_name = c.get("name")
                    result.best_title = c.get("title")
                    result.best_email = c.get("email")
                    result.best_linkedin = c.get("linkedin_url")
                    if self._email_match(c.get("email"), result.gt_email):
                        result.found_correct_email = True
                    break

            return result

        # Try API
        client = await self._get_ocean()
        if not client:
            result.error = "No API key"
            return result

        try:
            start = datetime.now()
            domain = company.get("company_domain") or company.get("expected_domain")

            seniorities = {
                "owner_operator": ["Founder", "Owner"],
                "vp_marketing": ["C-Level", "VP", "Director"],
                "vp_sales": ["C-Level", "VP", "Director"]
            }.get(persona, [])

            people = await client.search_people(
                company_name=result.company_name,
                company_domain=domain,
                seniorities=seniorities,
                size=5
            )
            result.latency_ms = (datetime.now() - start).total_seconds() * 1000
            result.credits_used = 1

            result.returned_any = len(people) > 0
            result.returned_count = len(people)

            for p in people:
                if self._names_match(p.get("name"), result.gt_name) or \
                   self._linkedin_match(p.get("linkedin_url"), result.gt_linkedin_url):
                    result.found_correct_person = True
                    result.best_name = p.get("name")
                    result.best_title = p.get("title")
                    result.best_email = p.get("email")
                    result.best_linkedin = p.get("linkedin_url")
                    if self._email_match(p.get("email"), result.gt_email):
                        result.found_correct_email = True
                    break

            # Cache
            self.cache.set("ocean_people", cache_key, response=people)

        except Exception as e:
            result.error = str(e)

        return result

    async def test_leadmagic(
        self,
        company: dict,
        gt_contact: dict,
        persona: str
    ) -> SourceTestResult:
        """Test LeadMagic Role Finder for a company"""
        result = SourceTestResult(
            company_name=company.get("company_name") or company.get("name", ""),
            persona_type=persona,
            source_name="leadmagic",
            gt_name=gt_contact.get("contact_name", ""),
            gt_email=gt_contact.get("contact_email"),
            gt_linkedin_url=gt_contact.get("contact_linkedin_url")
        )

        domain = company.get("company_domain") or company.get("expected_domain")
        if not domain:
            result.error = "No domain"
            return result

        # Get target job title for persona
        job_title = {
            "owner_operator": "CEO",
            "vp_marketing": "VP Marketing",
            "vp_sales": "VP Sales"
        }.get(persona, "CEO")

        cache_key = f"leadmagic_role:{domain}:{job_title}"
        cached = self.cache.get("leadmagic", cache_key)

        if cached:
            result.returned_any = bool(cached.get("name"))
            result.returned_count = 1 if cached.get("name") else 0
            result.credits_used = cached.get("credits", 2)
            if cached.get("name"):
                result.best_name = cached.get("name")
                result.best_linkedin = cached.get("profile_url")
                if self._names_match(cached.get("name"), result.gt_name) or \
                   self._linkedin_match(cached.get("profile_url"), result.gt_linkedin_url):
                    result.found_correct_person = True
            return result

        # Try API
        api_key = self._get_api_key("leadmagic")
        if not api_key:
            result.error = "No API key"
            return result

        try:
            import aiohttp
            start = datetime.now()

            url = "https://api.leadmagic.io/v1/people/role-finder"
            headers = {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "company_domain": domain,
                "job_title": job_title
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    result.latency_ms = (datetime.now() - start).total_seconds() * 1000
                    result.credits_used = 2

                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("name"):
                            result.returned_any = True
                            result.returned_count = 1
                            result.best_name = data.get("name")
                            result.best_linkedin = data.get("profile_url")
                            result.credits_used = data.get("credits_consumed", 2)

                            if self._names_match(data.get("name"), result.gt_name) or \
                               self._linkedin_match(data.get("profile_url"), result.gt_linkedin_url):
                                result.found_correct_person = True

                            # Cache
                            self.cache.set("leadmagic", cache_key, response={
                                "name": data.get("name"),
                                "profile_url": data.get("profile_url"),
                                "credits": data.get("credits_consumed", 2)
                            })
                    else:
                        error_text = await resp.text()
                        result.error = f"API error {resp.status}: {error_text[:100]}"

        except Exception as e:
            result.error = str(e)

        return result

    def compute_source_summary(
        self,
        results: list[SourceTestResult],
        source_name: str
    ) -> SourceSummary:
        """Compute summary for a source"""
        source_results = [r for r in results if r.source_name == source_name]

        summary = SourceSummary(source_name=source_name)
        summary.total_tested = len(source_results)

        if not source_results:
            return summary

        # Core metrics
        summary.coverage = sum(1 for r in source_results if r.returned_any) / len(source_results)
        summary.person_match_rate = sum(1 for r in source_results if r.found_correct_person) / len(source_results)

        email_results = [r for r in source_results if r.gt_email]
        if email_results:
            summary.email_match_rate = sum(1 for r in email_results if r.found_correct_email) / len(email_results)

        # Cost
        summary.total_credits = sum(r.credits_used for r in source_results)
        hits = sum(1 for r in source_results if r.found_correct_person)
        summary.cost_per_hit = summary.total_credits / hits if hits > 0 else float('inf')

        latencies = [r.latency_ms for r in source_results if r.latency_ms > 0]
        summary.avg_latency_ms = sum(latencies) / len(latencies) if latencies else 0

        # By persona
        for persona in PERSONA_TITLES.keys():
            p_results = [r for r in source_results if r.persona_type == persona]
            if p_results:
                summary.by_persona[persona] = {
                    "count": len(p_results),
                    "coverage": sum(1 for r in p_results if r.returned_any) / len(p_results),
                    "person_match_rate": sum(1 for r in p_results if r.found_correct_person) / len(p_results)
                }

        return summary

    async def compare(
        self,
        sources: list[str] | None = None,
        personas: list[str] | None = None,
        max_companies: int | None = None,
        max_concurrent: int = 3
    ) -> tuple[list[SourceSummary], list[SourceTestResult]]:
        """
        Run comparison for all sources.

        Args:
            sources: Sources to test (default: all available)
            personas: Personas to test (default: all)
            max_companies: Limit companies
            max_concurrent: Max concurrent tests

        Returns:
            Tuple of (summaries, detailed_results)
        """
        if self.contacts_df is None:
            raise ValueError("Load ground truth first")

        sources = sources or ["scrapin", "blitz", "ocean"]
        personas = personas or list(PERSONA_TITLES.keys())

        # Get unique companies
        companies = self.contacts_df.groupby(
            ["company_name", "linkedin_company_url"]
        ).first().reset_index()

        if max_companies:
            companies = companies.head(max_companies)

        logger.info(f"Comparing {len(sources)} sources on {len(companies)} companies")

        semaphore = asyncio.Semaphore(max_concurrent)
        all_results: list[SourceTestResult] = []

        source_fns = {
            "scrapin": self.test_scrapin,
            "blitz": self.test_blitz,
            "ocean": self.test_ocean,
            "leadmagic": self.test_leadmagic,
        }

        async def test_one(company_row, persona: str, source: str):
            async with semaphore:
                gt_contacts = self.contacts_df[
                    (self.contacts_df["company_name"] == company_row["company_name"]) &
                    (self.contacts_df["persona_type"] == persona)
                ]
                if len(gt_contacts) == 0:
                    return None

                gt_contact = gt_contacts.iloc[0].to_dict()
                test_fn = source_fns.get(source)
                if not test_fn:
                    return None

                return await test_fn(company_row.to_dict(), gt_contact, persona)

        # Create tasks
        tasks = []
        for _, company in companies.iterrows():
            for persona in personas:
                gt_exists = len(self.contacts_df[
                    (self.contacts_df["company_name"] == company["company_name"]) &
                    (self.contacts_df["persona_type"] == persona)
                ]) > 0

                if gt_exists:
                    for source in sources:
                        tasks.append(test_one(company, persona, source))

        # Run tests
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Test error: {r}")
            elif r is not None:
                all_results.append(r)

        # Compute summaries
        summaries = [self.compute_source_summary(all_results, s) for s in sources]

        return summaries, all_results

    def generate_report(
        self,
        summaries: list[SourceSummary],
        results: list[SourceTestResult],
        output_path: str | Path
    ):
        """Generate comparison report"""
        report = f"""# Enrichment Source Comparison Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Comparison

| Source | Coverage | Person Match | Email Match | Cost/Hit | Latency |
|--------|----------|--------------|-------------|----------|---------|
"""
        for s in summaries:
            cost = f"${s.cost_per_hit:.2f}" if s.cost_per_hit != float('inf') else "N/A"
            report += f"| {s.source_name} | {s.coverage*100:.1f}% | {s.person_match_rate*100:.1f}% | {s.email_match_rate*100:.1f}% | {cost} | {s.avg_latency_ms:.0f}ms |\n"

        report += "\n## By Persona\n"

        for persona in PERSONA_TITLES.keys():
            report += f"\n### {persona}\n\n"
            report += "| Source | Coverage | Person Match |\n"
            report += "|--------|----------|-------------|\n"
            for s in summaries:
                p_data = s.by_persona.get(persona, {})
                if p_data:
                    report += f"| {s.source_name} | {p_data['coverage']*100:.1f}% | {p_data['person_match_rate']*100:.1f}% |\n"

        report += "\n## Recommendations\n\n"

        # Find best overall
        best = max(summaries, key=lambda s: s.person_match_rate)
        report += f"- **Best Person Match Rate**: {best.source_name} ({best.person_match_rate*100:.1f}%)\n"

        cheapest = min([s for s in summaries if s.cost_per_hit != float('inf')],
                       key=lambda s: s.cost_per_hit, default=None)
        if cheapest:
            report += f"- **Most Cost Effective**: {cheapest.source_name} (${cheapest.cost_per_hit:.2f}/hit)\n"

        # Best coverage
        best_cov = max(summaries, key=lambda s: s.coverage)
        report += f"- **Best Coverage**: {best_cov.source_name} ({best_cov.coverage*100:.1f}%)\n"

        # Write report
        with open(output_path, "w") as f:
            f.write(report)

        logger.info(f"Wrote comparison report to {output_path}")

        # Save detailed results
        results_df = pd.DataFrame([asdict(r) for r in results])
        results_path = str(output_path).replace(".md", "_details.parquet")
        results_df.to_parquet(results_path, index=False)

    async def close(self):
        """Close clients"""
        if self._scrapin:
            await self._scrapin.close()
        if self._blitz:
            await self._blitz.close()


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Compare Enrichment Sources")
    parser.add_argument("--contacts", default="./evaluation/data/contacts_truth.parquet",
                        help="Path to contacts ground truth")
    parser.add_argument("--output", default="./evaluation/data/source_comparison.md",
                        help="Output report path")
    parser.add_argument("--sources", nargs="+", default=None,
                        help="Sources to test (default: scrapin, blitz, ocean)")
    parser.add_argument("--personas", nargs="+", default=None,
                        help="Personas to test")
    parser.add_argument("--max-companies", type=int, default=None,
                        help="Max companies to test")

    args = parser.parse_args()

    comparer = SourceComparer()

    try:
        comparer.load_ground_truth(args.contacts)

        summaries, results = await comparer.compare(
            sources=args.sources,
            personas=args.personas,
            max_companies=args.max_companies
        )

        comparer.generate_report(summaries, results, args.output)

        # Print summary
        print("\n=== Source Comparison ===")
        for s in summaries:
            print(f"\n{s.source_name}:")
            print(f"  Coverage: {s.coverage*100:.1f}%")
            print(f"  Person Match: {s.person_match_rate*100:.1f}%")
            print(f"  Email Match: {s.email_match_rate*100:.1f}%")
            if s.cost_per_hit != float('inf'):
                print(f"  Cost/Hit: ${s.cost_per_hit:.2f}")

    finally:
        await comparer.close()


if __name__ == "__main__":
    asyncio.run(main())
