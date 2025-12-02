#!/usr/bin/env python3
"""
Multi-Source Contact Ground Truth Builder

Builds a verified contact dataset by cross-referencing multiple independent sources:
- Ocean.io people search
- Blitz waterfall-icp (cached)
- ZoomInfo page scraping
- News/funding search via Serper

Contacts are scored by source count:
- GOLD: 3+ sources agree
- SILVER: 2 sources agree
- BRONZE: 1 source (unverified)
"""

import asyncio
import os
import sys
import json
import logging
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
import aiohttp
import pandas as pd

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "contact-finder"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "domain-resolver"))

from harness.cache import EvaluationCache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Target personas and their title patterns
PERSONAS = {
    "owner_operator": {
        "seniorities": ["Founder", "Owner", "C-Level"],
        "titles": ["Owner", "Founder", "CEO", "Chief Executive Officer", "President",
                   "Principal", "Managing Partner", "Proprietor", "Co-Founder", "Co-Owner"],
        "ocean_seniorities": ["Founder", "Owner"],
        "ocean_job_titles": ["CEO", "Chief Executive Officer", "President", "Owner"]
    },
    "vp_marketing": {
        "seniorities": ["C-Level", "VP"],
        "titles": ["VP Marketing", "VP of Marketing", "Vice President Marketing",
                   "Head of Marketing", "CMO", "Chief Marketing Officer",
                   "Director of Marketing", "Marketing Director"],
        "ocean_seniorities": ["C-Level", "VP", "Director"],
        "ocean_job_titles": ["CMO", "Chief Marketing Officer", "VP Marketing",
                             "Vice President Marketing", "Head of Marketing", "Marketing Director"]
    },
    "vp_sales": {
        "seniorities": ["C-Level", "VP"],
        "titles": ["VP Sales", "VP of Sales", "Vice President Sales",
                   "Head of Sales", "CRO", "Chief Revenue Officer",
                   "Director of Sales", "Sales Director"],
        "ocean_seniorities": ["C-Level", "VP", "Director"],
        "ocean_job_titles": ["CRO", "Chief Revenue Officer", "VP Sales",
                             "Vice President Sales", "Head of Sales", "Sales Director"]
    }
}


@dataclass
class ContactSource:
    """A contact found from a single source"""
    source: str  # "ocean", "blitz", "zoominfo", "news", "scrapin"
    name: str
    title: str | None = None
    linkedin_url: str | None = None
    email: str | None = None
    phone: str | None = None
    confidence: float = 0.5
    raw_data: dict = field(default_factory=dict)


@dataclass
class VerifiedContact:
    """A contact verified across multiple sources"""
    # Company info
    company_name: str
    company_domain: str | None
    linkedin_company_url: str

    # Contact info (merged from sources)
    name: str
    title: str | None
    email: str | None
    linkedin_url: str | None
    phone: str | None

    # Verification metadata
    sources: list[str] = field(default_factory=list)
    source_count: int = 0
    tier: str = "bronze"  # gold, silver, bronze
    manual_verified: bool = False
    email_verified: bool = False

    # Target persona
    persona_type: str = ""

    # Source details
    source_contacts: list[dict] = field(default_factory=list)


class OceanPeopleClient:
    """Ocean.io People Search client"""

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = "https://api.ocean.io/v2"

    async def search_people(
        self,
        company_name: str | None = None,
        company_domain: str | None = None,
        seniorities: list[str] | None = None,
        job_titles: list[str] | None = None,
        size: int = 10
    ) -> list[dict]:
        """
        Search for people at a company.

        Args:
            company_name: Company name to search
            company_domain: Company domain to filter
            seniorities: List of seniority levels (e.g., ["Founder", "C-Level"])
            job_titles: List of job titles to filter
            size: Max results to return

        Returns:
            List of person dicts with name, title, linkedin_url, email
        """
        url = f"{self.base_url}/search/people"

        headers = {
            'x-api-token': self.api_key,
            'Content-Type': 'application/json'
        }

        # Build filters
        people_filters = {}
        if seniorities:
            people_filters["seniorities"] = seniorities
        if job_titles:
            people_filters["jobTitles"] = job_titles

        company_filters = {}
        if company_name:
            company_filters["name"] = company_name
        if company_domain:
            company_filters["domains"] = [company_domain]

        payload = {
            "peopleFilters": people_filters,
            "companyFilters": company_filters,
            "size": size,
            "peoplePerCompany": size
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        people = data.get("data", [])

                        results = []
                        for person in people:
                            results.append({
                                "name": person.get("fullName") or person.get("name"),
                                "title": person.get("jobTitle") or person.get("title"),
                                "linkedin_url": person.get("linkedInUrl"),
                                "email": person.get("email"),
                                "company": person.get("companyName"),
                                "raw": person
                            })
                        return results

                    elif response.status == 404:
                        logger.debug(f"No people found for: {company_name}")
                        return []
                    else:
                        error_text = await response.text()
                        logger.error(f"Ocean people search error {response.status}: {error_text}")
                        return []

        except Exception as e:
            logger.error(f"Ocean people search error: {e}")
            return []


class ZoomInfoScraper:
    """Scrape ZoomInfo company pages for team info"""

    def __init__(self, zenrows_api_key: str):
        self.zenrows_api_key = zenrows_api_key
        self.base_url = "https://api.zenrows.com/v1/"

    async def scrape_company_team(self, company_name: str) -> list[dict]:
        """
        Scrape ZoomInfo company page for team/leadership info.

        Args:
            company_name: Company name to search

        Returns:
            List of person dicts extracted from page
        """
        # Clean company name for URL
        slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "")
        slug = re.sub(r'[^a-z0-9-]', '', slug)

        url = f"https://www.zoominfo.com/c/{slug}"

        params = {
            "apikey": self.zenrows_api_key,
            "url": url,
            "js_render": "true",
            "wait": "3000"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._extract_people_from_html(html)
                    else:
                        logger.debug(f"ZoomInfo scrape failed for {company_name}: {response.status}")
                        return []

        except Exception as e:
            logger.error(f"ZoomInfo scrape error for {company_name}: {e}")
            return []

    def _extract_people_from_html(self, html: str) -> list[dict]:
        """Extract people from ZoomInfo HTML"""
        people = []

        # Look for common patterns in ZoomInfo pages
        # Pattern 1: JSON-LD structured data
        json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
        matches = re.findall(json_ld_pattern, html, re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match)
                if isinstance(data, dict):
                    if data.get("@type") == "Person":
                        people.append({
                            "name": data.get("name"),
                            "title": data.get("jobTitle"),
                            "linkedin_url": None,
                            "raw": data
                        })
                    elif "employee" in data or "member" in data:
                        for emp in data.get("employee", []) + data.get("member", []):
                            if isinstance(emp, dict):
                                people.append({
                                    "name": emp.get("name"),
                                    "title": emp.get("jobTitle"),
                                    "linkedin_url": None,
                                    "raw": emp
                                })
            except json.JSONDecodeError:
                continue

        # Pattern 2: Text extraction for leadership section
        leadership_pattern = r'(?:CEO|President|Founder|Owner|Director|VP|Vice President|Head of)[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)'
        title_matches = re.findall(leadership_pattern, html)

        for name in title_matches[:5]:  # Limit to top 5
            if name not in [p.get("name") for p in people]:
                people.append({
                    "name": name,
                    "title": None,
                    "linkedin_url": None,
                    "raw": {}
                })

        return people


class NewsSearcher:
    """Search for company news/funding for executive mentions"""

    def __init__(self, serper_api_key: str):
        self.serper_api_key = serper_api_key
        self.base_url = "https://google.serper.dev/search"

    async def search_executives(self, company_name: str) -> list[dict]:
        """
        Search for news mentions of company executives.

        Args:
            company_name: Company name to search

        Returns:
            List of person dicts mentioned in news
        """
        # Search for funding/leadership news
        queries = [
            f'"{company_name}" CEO OR founder OR owner',
            f'"{company_name}" raises funding OR acquired',
        ]

        people = []

        for query in queries:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.base_url,
                        json={"q": query, "num": 5},
                        headers={
                            "X-API-KEY": self.serper_api_key,
                            "Content-Type": "application/json"
                        },
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()

                            # Extract people from snippets
                            for result in data.get("organic", []):
                                snippet = result.get("snippet", "")
                                title = result.get("title", "")

                                # Look for "Name, CEO of Company" patterns
                                patterns = [
                                    rf'([A-Z][a-z]+ [A-Z][a-z]+),?\s+(?:CEO|founder|owner|president)\s+(?:of|at)?\s*{re.escape(company_name)}',
                                    rf'{re.escape(company_name)}[\'"s]*\s+(?:CEO|founder|owner|president)\s+([A-Z][a-z]+ [A-Z][a-z]+)',
                                    rf'([A-Z][a-z]+ [A-Z][a-z]+)\s+(?:founded|started|launched|owns)\s+{re.escape(company_name)}',
                                ]

                                for pattern in patterns:
                                    for text in [snippet, title]:
                                        matches = re.findall(pattern, text, re.IGNORECASE)
                                        for name in matches:
                                            if name and len(name) > 3:
                                                people.append({
                                                    "name": name,
                                                    "title": "CEO/Founder",
                                                    "linkedin_url": None,
                                                    "source_url": result.get("link"),
                                                    "raw": {"snippet": snippet}
                                                })

            except Exception as e:
                logger.debug(f"News search error for {company_name}: {e}")

        # Dedupe by name
        seen = set()
        unique = []
        for p in people:
            if p["name"] not in seen:
                seen.add(p["name"])
                unique.append(p)

        return unique


class ContactTruthBuilder:
    """
    Builds verified contact ground truth from multiple sources.
    """

    def __init__(
        self,
        ocean_api_key: str | None = None,
        blitz_api_key: str | None = None,
        zenrows_api_key: str | None = None,
        serper_api_key: str | None = None,
        cache_path: str = "./evaluation/data/cache.db"
    ):
        self.cache = EvaluationCache(cache_path)

        # Initialize clients
        self.ocean_client = OceanPeopleClient(ocean_api_key) if ocean_api_key else None
        self.zoominfo_scraper = ZoomInfoScraper(zenrows_api_key) if zenrows_api_key else None
        self.news_searcher = NewsSearcher(serper_api_key) if serper_api_key else None

        # Will load Blitz client if needed
        self.blitz_api_key = blitz_api_key
        self._blitz_client = None

    async def _get_blitz_client(self):
        """Get or create Blitz client"""
        if self._blitz_client is None and self.blitz_api_key:
            try:
                from modules.enrichment.blitz import BlitzClient
                self._blitz_client = BlitzClient(self.blitz_api_key)
            except ImportError:
                logger.warning("Could not import BlitzClient")
        return self._blitz_client

    async def collect_from_ocean(
        self,
        company_name: str,
        company_domain: str | None,
        persona: str
    ) -> list[ContactSource]:
        """Collect contacts from Ocean.io people search"""
        if not self.ocean_client:
            return []

        cache_key = f"{company_name}:{persona}"
        cached = self.cache.get("ocean_people", cache_key)
        if cached:
            return [ContactSource(**c) for c in cached]

        persona_config = PERSONAS.get(persona, {})

        try:
            people = await self.ocean_client.search_people(
                company_name=company_name,
                company_domain=company_domain,
                seniorities=persona_config.get("ocean_seniorities"),
                job_titles=persona_config.get("ocean_job_titles"),
                size=5
            )

            contacts = []
            for p in people:
                contacts.append(ContactSource(
                    source="ocean",
                    name=p.get("name", ""),
                    title=p.get("title"),
                    linkedin_url=p.get("linkedin_url"),
                    email=p.get("email"),
                    confidence=0.8,
                    raw_data=p.get("raw", {})
                ))

            # Cache results
            self.cache.set("ocean_people", cache_key, response=[asdict(c) for c in contacts])

            return contacts

        except Exception as e:
            logger.error(f"Ocean error for {company_name}: {e}")
            return []

    async def collect_from_blitz(
        self,
        linkedin_company_url: str,
        persona: str
    ) -> list[ContactSource]:
        """Collect contacts from Blitz waterfall-icp (cached)"""
        cache_key = f"{linkedin_company_url}:{persona}:False"
        cached = self.cache.get("blitz_waterfall", cache_key)

        if cached:
            contacts = []
            for c in cached.get("contacts", []):
                contacts.append(ContactSource(
                    source="blitz",
                    name=c.get("name", ""),
                    title=c.get("title"),
                    linkedin_url=c.get("linkedin_url"),
                    email=c.get("email"),
                    confidence=c.get("confidence", 0.7),
                    raw_data=c
                ))
            return contacts

        # Try to call Blitz if not cached
        client = await self._get_blitz_client()
        if not client:
            return []

        persona_config = PERSONAS.get(persona, {})
        titles = persona_config.get("titles", [])

        try:
            results = await client.waterfall_icp(
                linkedin_company_url=linkedin_company_url,
                titles=titles,
                max_results=5
            )

            contacts = []
            for r in results:
                contacts.append(ContactSource(
                    source="blitz",
                    name=r.name,
                    title=r.title,
                    linkedin_url=r.linkedin_url,
                    email=r.email,
                    confidence=r.confidence or 0.7,
                    raw_data=asdict(r) if hasattr(r, '__dict__') else {}
                ))

            # Cache results
            self.cache.set("blitz_waterfall", cache_key, response={
                "contacts": [asdict(c) for c in contacts],
                "credits": len(contacts)
            })

            return contacts

        except Exception as e:
            logger.debug(f"Blitz error for {linkedin_company_url}: {e}")
            return []

    async def collect_from_zoominfo(
        self,
        company_name: str
    ) -> list[ContactSource]:
        """Collect contacts from ZoomInfo page scraping"""
        if not self.zoominfo_scraper:
            return []

        cache_key = company_name
        cached = self.cache.get("zoominfo", cache_key)
        if cached:
            return [ContactSource(**c) for c in cached]

        try:
            people = await self.zoominfo_scraper.scrape_company_team(company_name)

            contacts = []
            for p in people:
                if p.get("name"):
                    contacts.append(ContactSource(
                        source="zoominfo",
                        name=p.get("name", ""),
                        title=p.get("title"),
                        linkedin_url=p.get("linkedin_url"),
                        confidence=0.75,
                        raw_data=p.get("raw", {})
                    ))

            # Cache results
            self.cache.set("zoominfo", cache_key, response=[asdict(c) for c in contacts])

            return contacts

        except Exception as e:
            logger.error(f"ZoomInfo error for {company_name}: {e}")
            return []

    async def collect_from_news(
        self,
        company_name: str
    ) -> list[ContactSource]:
        """Collect contacts from news/funding search"""
        if not self.news_searcher:
            return []

        cache_key = company_name
        cached = self.cache.get("news_search", cache_key)
        if cached:
            return [ContactSource(**c) for c in cached]

        try:
            people = await self.news_searcher.search_executives(company_name)

            contacts = []
            for p in people:
                if p.get("name"):
                    contacts.append(ContactSource(
                        source="news",
                        name=p.get("name", ""),
                        title=p.get("title"),
                        linkedin_url=p.get("linkedin_url"),
                        confidence=0.6,  # Lower confidence for news extraction
                        raw_data=p
                    ))

            # Cache results
            self.cache.set("news_search", cache_key, response=[asdict(c) for c in contacts])

            return contacts

        except Exception as e:
            logger.error(f"News search error for {company_name}: {e}")
            return []

    def _names_match(self, name1: str, name2: str) -> bool:
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

        # Normalize URLs
        def normalize(url):
            url = url.lower().rstrip("/")
            url = url.replace("http://", "https://")
            url = re.sub(r'\?.*$', '', url)  # Remove query params
            return url

        return normalize(url1) == normalize(url2)

    def merge_contacts(
        self,
        all_sources: list[ContactSource],
        persona: str
    ) -> list[VerifiedContact]:
        """
        Merge contacts from multiple sources into verified contacts.

        Contacts are merged by:
        1. LinkedIn URL match (most reliable)
        2. Name similarity (fallback)
        """
        if not all_sources:
            return []

        # Group contacts by identity
        groups: list[list[ContactSource]] = []

        for contact in all_sources:
            matched = False

            for group in groups:
                # Check if this contact matches any in the group
                for existing in group:
                    if self._linkedin_urls_match(contact.linkedin_url, existing.linkedin_url):
                        group.append(contact)
                        matched = True
                        break
                    elif self._names_match(contact.name, existing.name):
                        group.append(contact)
                        matched = True
                        break

                if matched:
                    break

            if not matched:
                groups.append([contact])

        # Create verified contacts from groups
        verified = []

        for group in groups:
            # Get best values from group
            sources = list(set(c.source for c in group))
            source_count = len(sources)

            # Determine tier
            if source_count >= 3:
                tier = "gold"
            elif source_count >= 2:
                tier = "silver"
            else:
                tier = "bronze"

            # Get best name (longest, most complete)
            best_name = max((c.name for c in group if c.name), key=len, default="")

            # Get best title
            best_title = next((c.title for c in group if c.title), None)

            # Get best email
            best_email = next((c.email for c in group if c.email), None)

            # Get best LinkedIn URL
            best_linkedin = next((c.linkedin_url for c in group if c.linkedin_url), None)

            # Get phone
            best_phone = next((c.phone for c in group if c.phone), None)

            verified.append(VerifiedContact(
                company_name="",  # Will be filled in later
                company_domain=None,
                linkedin_company_url="",
                name=best_name,
                title=best_title,
                email=best_email,
                linkedin_url=best_linkedin,
                phone=best_phone,
                sources=sources,
                source_count=source_count,
                tier=tier,
                persona_type=persona,
                source_contacts=[asdict(c) for c in group]
            ))

        # Sort by tier (gold first) and source count
        tier_order = {"gold": 0, "silver": 1, "bronze": 2}
        verified.sort(key=lambda v: (tier_order.get(v.tier, 3), -v.source_count))

        return verified

    async def build_for_company(
        self,
        company: dict,
        personas: list[str] | None = None
    ) -> list[VerifiedContact]:
        """
        Build verified contacts for a single company.

        Args:
            company: Dict with name, linkedin_company_url, expected_domain
            personas: List of personas to find (default: all)

        Returns:
            List of verified contacts
        """
        company_name = company.get("name", "")
        linkedin_url = company.get("linkedin_company_url", "")
        domain = company.get("expected_domain") or company.get("domain")

        personas = personas or list(PERSONAS.keys())
        all_verified = []

        for persona in personas:
            logger.info(f"  Collecting {persona} for {company_name}")

            # Collect from all sources in parallel
            tasks = [
                self.collect_from_ocean(company_name, domain, persona),
                self.collect_from_blitz(linkedin_url, persona) if linkedin_url else asyncio.coroutine(lambda: [])(),
                self.collect_from_zoominfo(company_name),
                self.collect_from_news(company_name),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Flatten results, handle exceptions
            all_sources = []
            for r in results:
                if isinstance(r, Exception):
                    logger.debug(f"Source error: {r}")
                elif isinstance(r, list):
                    all_sources.extend(r)

            # Merge contacts
            verified = self.merge_contacts(all_sources, persona)

            # Fill in company info
            for v in verified:
                v.company_name = company_name
                v.company_domain = domain
                v.linkedin_company_url = linkedin_url

            all_verified.extend(verified)

            logger.info(f"    Found {len(verified)} contacts ({sum(1 for v in verified if v.tier == 'gold')} gold)")

        return all_verified

    async def build_ground_truth(
        self,
        companies_path: str | Path,
        output_path: str | Path,
        personas: list[str] | None = None,
        max_companies: int | None = None,
        split: str | None = None
    ) -> pd.DataFrame:
        """
        Build ground truth for all companies.

        Args:
            companies_path: Path to companies parquet/csv
            output_path: Path for output parquet
            personas: List of personas to find
            max_companies: Limit number of companies (for testing)
            split: Filter to specific split (cal_dev, validation, blind)

        Returns:
            DataFrame of verified contacts
        """
        # Load companies
        if str(companies_path).endswith(".parquet"):
            df = pd.read_parquet(companies_path)
        else:
            df = pd.read_csv(companies_path)

        # Filter to companies with LinkedIn URLs
        df = df[df["linkedin_company_url"].notna()]

        # Filter by split if specified
        if split and "split" in df.columns:
            df = df[df["split"] == split]

        if max_companies:
            df = df.head(max_companies)

        logger.info(f"Building ground truth for {len(df)} companies")

        all_verified = []

        for i, (_, company) in enumerate(df.iterrows()):
            logger.info(f"[{i+1}/{len(df)}] Processing {company['name']}")

            verified = await self.build_for_company(company.to_dict(), personas)
            all_verified.extend(verified)

            # Rate limiting
            await asyncio.sleep(0.5)

        # Convert to DataFrame
        records = []
        for v in all_verified:
            records.append({
                "company_name": v.company_name,
                "company_domain": v.company_domain,
                "linkedin_company_url": v.linkedin_company_url,
                "contact_name": v.name,
                "contact_title": v.title,
                "contact_email": v.email,
                "contact_linkedin_url": v.linkedin_url,
                "contact_phone": v.phone,
                "sources": ",".join(v.sources),
                "source_count": v.source_count,
                "tier": v.tier,
                "persona_type": v.persona_type,
                "manual_verified": v.manual_verified,
                "email_verified": v.email_verified,
            })

        result_df = pd.DataFrame(records)

        # Save
        result_df.to_parquet(output_path, index=False)
        logger.info(f"Saved {len(result_df)} contacts to {output_path}")

        # Print summary
        print("\n=== Ground Truth Summary ===")
        print(f"Total contacts: {len(result_df)}")
        print(f"Gold tier (3+ sources): {len(result_df[result_df['tier'] == 'gold'])}")
        print(f"Silver tier (2 sources): {len(result_df[result_df['tier'] == 'silver'])}")
        print(f"Bronze tier (1 source): {len(result_df[result_df['tier'] == 'bronze'])}")
        print(f"\nBy persona:")
        print(result_df.groupby('persona_type')['tier'].value_counts().unstack(fill_value=0))

        return result_df


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Build multi-source contact ground truth")
    parser.add_argument("--companies", default="./evaluation/data/companies_truth.parquet",
                        help="Path to companies file")
    parser.add_argument("--output", default="./evaluation/data/contacts_truth.parquet",
                        help="Output path")
    parser.add_argument("--personas", nargs="+", default=None,
                        help="Personas to find (default: all)")
    parser.add_argument("--max-companies", type=int, default=None,
                        help="Max companies to process")
    parser.add_argument("--split", default=None,
                        help="Filter to split (cal_dev, validation, blind)")

    args = parser.parse_args()

    # Get API keys from environment
    ocean_key = os.environ.get("OCEAN_API_KEY")
    blitz_key = os.environ.get("BLITZ_API_KEY")
    zenrows_key = os.environ.get("ZENROWS_API_KEY")
    serper_key = os.environ.get("SERPER_API_KEY")

    if not any([ocean_key, blitz_key, zenrows_key, serper_key]):
        print("Warning: No API keys found. Set OCEAN_API_KEY, BLITZ_API_KEY, ZENROWS_API_KEY, SERPER_API_KEY")
        print("Will only use cached results.")

    builder = ContactTruthBuilder(
        ocean_api_key=ocean_key,
        blitz_api_key=blitz_key,
        zenrows_api_key=zenrows_key,
        serper_api_key=serper_key
    )

    await builder.build_ground_truth(
        companies_path=args.companies,
        output_path=args.output,
        personas=args.personas,
        max_companies=args.max_companies,
        split=args.split
    )


if __name__ == "__main__":
    asyncio.run(main())
