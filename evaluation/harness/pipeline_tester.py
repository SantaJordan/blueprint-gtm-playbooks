"""
Contact Discovery Pipeline Tester

Tests the full contact discovery flow:
1. Company + Domain → Contact Discovery (Serper OSINT, Blitz, Scrapin)
2. Multi-source enrichment (RapidAPI, Scrapin)
3. LLM verification (is this the right person? do they work there?)

Ground truth: LinkedIn connections export
"""

import asyncio
import csv
import json
import zipfile
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from io import TextIOWrapper, StringIO
from typing import Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from evaluation.harness.rapidapi_linkedin import RapidAPILinkedInClient, RapidAPIPersonResult

# Import Scrapin client
import importlib.util
_scrapin_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "contact-finder", "modules", "enrichment", "scrapin.py"
)
_spec = importlib.util.spec_from_file_location("scrapin", _scrapin_path)
_scrapin_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_scrapin_module)
ScrapinClient = _scrapin_module.ScrapinClient

# Import LeadMagic client
_leadmagic_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "contact-finder", "modules", "enrichment", "leadmagic.py"
)
_lm_spec = importlib.util.spec_from_file_location("leadmagic", _leadmagic_path)
_leadmagic_module = importlib.util.module_from_spec(_lm_spec)
_lm_spec.loader.exec_module(_leadmagic_module)
LeadMagicClient = _leadmagic_module.LeadMagicClient

# Import OpenWeb Ninja client
_openweb_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "contact-finder", "modules", "discovery", "openweb_ninja.py"
)
_openweb_spec = importlib.util.spec_from_file_location("openweb_ninja", _openweb_path)
_openweb_module = importlib.util.module_from_spec(_openweb_spec)
_openweb_spec.loader.exec_module(_openweb_module)
OpenWebNinjaClient = _openweb_module.OpenWebNinjaClient
LocalBusinessResult = _openweb_module.LocalBusinessResult
OpenWebContactResult = _openweb_module.OpenWebContactResult
SocialLinksResult = _openweb_module.SocialLinksResult


@dataclass
class LinkedInConnection:
    """Ground truth from LinkedIn export"""
    first_name: str
    last_name: str
    full_name: str
    company: str
    title: str
    linkedin_url: str
    email: str | None = None
    connected_on: str | None = None


@dataclass
class EnrichmentResult:
    """Result from a single enrichment source"""
    source: str  # 'rapidapi', 'scrapin'
    success: bool
    name: str | None = None
    title: str | None = None
    company: str | None = None
    linkedin_url: str | None = None
    experiences: list[dict] = field(default_factory=list)
    latency_ms: int = 0
    error: str | None = None
    raw_response: dict = field(default_factory=dict)


@dataclass
class VerificationResult:
    """Result of LLM verification"""
    is_same_person: bool
    currently_employed: bool
    confidence: float  # 0-100
    reasoning: str
    red_flags: list[str] = field(default_factory=list)


@dataclass
class PipelineTestResult:
    """Result of testing one LinkedIn connection"""
    # Ground truth
    ground_truth: LinkedInConnection

    # Enrichment results from each source
    enrichments: dict[str, EnrichmentResult] = field(default_factory=dict)

    # Verification (if done)
    verification: VerificationResult | None = None

    # Summary metrics
    sources_agree_on_name: bool = False
    sources_agree_on_company: bool = False
    any_source_found_data: bool = False

    # Timing
    total_latency_ms: int = 0


class PipelineTester:
    """
    Tests contact discovery pipeline against LinkedIn connections as ground truth.

    Focus: Is this the right person? Is the LinkedIn URL correct? Do they work there?
    """

    def __init__(
        self,
        rapidapi_key: str | None = None,
        scrapin_key: str | None = None,
        leadmagic_key: str | None = None,
        openai_key: str | None = None,
    ):
        self.rapidapi_key = rapidapi_key or os.environ.get("RAPIDAPI_KEY")
        self.scrapin_key = scrapin_key or os.environ.get("SCRAPIN_API_KEY")
        self.leadmagic_key = leadmagic_key or os.environ.get("LEADMAGIC_API_KEY")
        self.openai_key = openai_key or os.environ.get("OPENAI_API_KEY")

        # Clients (lazy init)
        self._rapidapi: RapidAPILinkedInClient | None = None
        self._scrapin: ScrapinClient | None = None
        self._leadmagic: LeadMagicClient | None = None
        self._openweb_ninja: OpenWebNinjaClient | None = None

    async def _get_rapidapi(self) -> RapidAPILinkedInClient:
        if not self._rapidapi:
            if not self.rapidapi_key:
                raise ValueError("RAPIDAPI_KEY not set")
            self._rapidapi = RapidAPILinkedInClient(self.rapidapi_key)
        return self._rapidapi

    async def _get_scrapin(self) -> ScrapinClient:
        if not self._scrapin:
            if not self.scrapin_key:
                raise ValueError("SCRAPIN_API_KEY not set")
            self._scrapin = ScrapinClient(self.scrapin_key)
        return self._scrapin

    async def _get_leadmagic(self) -> LeadMagicClient:
        if not self._leadmagic:
            if not self.leadmagic_key:
                raise ValueError("LEADMAGIC_API_KEY not set")
            self._leadmagic = LeadMagicClient(self.leadmagic_key)
        return self._leadmagic

    async def _get_openweb_ninja(self) -> OpenWebNinjaClient:
        if not self._openweb_ninja:
            if not self.rapidapi_key:
                raise ValueError("RAPIDAPI_KEY not set (needed for OpenWeb Ninja)")
            self._openweb_ninja = OpenWebNinjaClient(self.rapidapi_key)
        return self._openweb_ninja

    async def close(self):
        """Close all clients"""
        if self._rapidapi:
            await self._rapidapi.close()
        if self._scrapin:
            await self._scrapin.close()
        if self._leadmagic:
            await self._leadmagic.close()
        if self._openweb_ninja:
            await self._openweb_ninja.close()

    @staticmethod
    def load_linkedin_export(zip_path: str, sample_size: int | None = None) -> list[LinkedInConnection]:
        """
        Load LinkedIn connections from export ZIP file.

        Args:
            zip_path: Path to LinkedIn export ZIP
            sample_size: If set, return random sample of this size

        Returns:
            List of LinkedInConnection objects
        """
        connections = []

        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Find Connections.csv
            csv_files = [f for f in zf.namelist() if 'connections' in f.lower() and f.endswith('.csv')]
            if not csv_files:
                raise ValueError(f"No Connections.csv found in {zip_path}")

            csv_filename = csv_files[0]

            with zf.open(csv_filename) as f:
                text_file = TextIOWrapper(f, encoding='utf-8-sig')
                lines = text_file.readlines()

                # Skip header notes (LinkedIn exports have notes before actual CSV)
                header_idx = 0
                for i, line in enumerate(lines):
                    if 'First Name' in line or 'first_name' in line.lower():
                        header_idx = i
                        break

                csv_content = ''.join(lines[header_idx:])
                reader = csv.DictReader(StringIO(csv_content))

                for row in reader:
                    # Handle various column name formats
                    first = row.get('First Name', row.get('first_name', ''))
                    last = row.get('Last Name', row.get('last_name', ''))
                    company = row.get('Company', row.get('company', ''))
                    title = row.get('Position', row.get('position', row.get('Title', '')))
                    email = row.get('Email Address', row.get('email', row.get('Email', '')))
                    url = row.get('URL', row.get('url', row.get('Profile URL', '')))
                    connected = row.get('Connected On', row.get('connected_on', ''))

                    if not url or 'linkedin.com' not in url:
                        continue

                    connections.append(LinkedInConnection(
                        first_name=first.strip() if first else '',
                        last_name=last.strip() if last else '',
                        full_name=f"{first} {last}".strip() if first or last else '',
                        company=company.strip() if company else '',
                        title=title.strip() if title else '',
                        linkedin_url=url.strip(),
                        email=email.strip() if email else None,
                        connected_on=connected.strip() if connected else None,
                    ))

        # Sample if requested
        if sample_size and sample_size < len(connections):
            import random
            connections = random.sample(connections, sample_size)

        return connections

    async def enrich_with_rapidapi(self, linkedin_url: str) -> EnrichmentResult:
        """Enrich a LinkedIn URL using RapidAPI"""
        try:
            client = await self._get_rapidapi()
            result = await client.get_person(linkedin_url)

            # Extract experiences if available
            experiences = []
            raw_data = result.raw_response.get('data', {})
            for exp in raw_data.get('experiences', [])[:5]:
                experiences.append({
                    'title': exp.get('title'),
                    'company': exp.get('subtitle'),
                    'duration': exp.get('caption'),
                    'company_url': exp.get('companyLink1'),
                })

            return EnrichmentResult(
                source='rapidapi',
                success=result.status == 'success' and result.name is not None,
                name=result.name,
                title=result.title,
                company=result.company,
                linkedin_url=result.linkedin_url,
                experiences=experiences,
                latency_ms=result.latency_ms,
                error=None if result.status == 'success' else result.status,
                raw_response=result.raw_response,
            )
        except Exception as e:
            return EnrichmentResult(
                source='rapidapi',
                success=False,
                error=str(e),
            )

    async def enrich_with_scrapin(self, linkedin_url: str) -> EnrichmentResult:
        """Enrich a LinkedIn URL using Scrapin"""
        try:
            client = await self._get_scrapin()
            result = await client.get_person_profile(linkedin_url)

            # Extract experiences (note: Scrapin uses 'experience' singular)
            experiences = []
            exp_list = getattr(result, 'experience', None) or []
            for exp in exp_list[:5]:
                if isinstance(exp, dict):
                    experiences.append({
                        'title': exp.get('title'),
                        'company': exp.get('company_name') or exp.get('company') or exp.get('companyName'),
                        'duration': exp.get('duration') or exp.get('dateRange'),
                        'is_current': exp.get('is_current', False),
                    })

            # Check if we got data
            has_data = result.full_name is not None

            return EnrichmentResult(
                source='scrapin',
                success=has_data,
                name=result.full_name,
                title=result.headline or result.title,
                company=result.company,
                linkedin_url=result.linkedin_url,
                experiences=experiences,
                latency_ms=getattr(result, 'latency_ms', 0),
                error=None if has_data else "no_data",
                raw_response=result.raw_response,
            )
        except Exception as e:
            return EnrichmentResult(
                source='scrapin',
                success=False,
                error=str(e),
            )

    async def enrich_with_leadmagic(self, linkedin_url: str) -> EnrichmentResult:
        """Enrich a LinkedIn URL using LeadMagic profile-search"""
        import time
        start_time = time.time()
        try:
            client = await self._get_leadmagic()
            result = await client.profile_search(linkedin_url)
            latency_ms = int((time.time() - start_time) * 1000)

            # Extract experiences
            experiences = []
            for exp in result.work_experience[:5]:
                if isinstance(exp, dict):
                    experiences.append({
                        'title': exp.get('title'),
                        'company': exp.get('company_name') or exp.get('company'),
                        'duration': exp.get('date_range') or exp.get('duration'),
                        'is_current': exp.get('is_current', False),
                    })

            return EnrichmentResult(
                source='leadmagic',
                success=result.success,
                name=result.full_name,
                title=result.professional_title,
                company=result.company_name,
                linkedin_url=result.linkedin_url,
                experiences=experiences,
                latency_ms=latency_ms,
                error=result.error,
                raw_response=result.raw_response,
            )
        except Exception as e:
            return EnrichmentResult(
                source='leadmagic',
                success=False,
                error=str(e),
            )

    # =========================================================================
    # OpenWeb Ninja Testing Methods (SMB Discovery)
    # =========================================================================

    async def test_openweb_google_maps(
        self,
        company_name: str,
        location: str | None = None,
    ) -> LocalBusinessResult:
        """
        Test OpenWeb Ninja Local Business Data API (Google Maps).
        Cost: $0.002/query

        Args:
            company_name: Business name to search
            location: Optional city/state (e.g., "Denver, CO")

        Returns:
            LocalBusinessResult with owner info, contact details, reviews
        """
        import time
        start_time = time.time()
        try:
            client = await self._get_openweb_ninja()
            result = await client.search_local_business(company_name, location)
            latency_ms = int((time.time() - start_time) * 1000)

            # Log for debugging
            if result.success:
                print(f"  [GoogleMaps] Found: {result.name}")
                if result.owner_name:
                    print(f"  [GoogleMaps] Owner: {result.owner_name}")
                print(f"  [GoogleMaps] Rating: {result.rating} ({result.reviews_count} reviews)")
            else:
                print(f"  [GoogleMaps] Error: {result.error}")

            return result
        except Exception as e:
            return LocalBusinessResult(
                place_id=None, name=None, owner_name=None,
                phone=None, email=None, website=None,
                address=None, city=None, state=None,
                rating=None, reviews_count=None, category=None,
                error=str(e)
            )

    async def test_openweb_contacts(self, domain: str) -> OpenWebContactResult:
        """
        Test OpenWeb Ninja Website Contacts Scraper API.
        Cost: $0.002/query

        Args:
            domain: Website domain (e.g., "joesplumbing.com")

        Returns:
            OpenWebContactResult with emails, phones, social links
        """
        import time
        start_time = time.time()
        try:
            client = await self._get_openweb_ninja()
            result = await client.scrape_contacts(domain)
            latency_ms = int((time.time() - start_time) * 1000)

            # Log for debugging
            if result.success:
                print(f"  [WebContacts] Emails: {len(result.emails)}")
                if result.primary_email:
                    print(f"  [WebContacts] Primary: {result.primary_email}")
                if result.linkedin:
                    print(f"  [WebContacts] LinkedIn: {result.linkedin}")
            else:
                print(f"  [WebContacts] Error: {result.error}")

            return result
        except Exception as e:
            return OpenWebContactResult(
                domain=domain,
                error=str(e)
            )

    async def test_openweb_social_links(
        self,
        name: str,
        platform: str = "linkedin"
    ) -> SocialLinksResult:
        """
        Test OpenWeb Ninja Social Links Search API.
        Cost: $0.002/query

        Args:
            name: Person or company name to search
            platform: Primary platform to search ("linkedin", "facebook", etc.)

        Returns:
            SocialLinksResult with social profile URLs
        """
        import time
        start_time = time.time()
        try:
            client = await self._get_openweb_ninja()
            result = await client.search_social_links(name, platform)
            latency_ms = int((time.time() - start_time) * 1000)

            # Log for debugging
            if result.success:
                print(f"  [SocialLinks] LinkedIn URLs: {len(result.linkedin_urls)}")
                if result.primary_linkedin:
                    print(f"  [SocialLinks] Primary: {result.primary_linkedin}")
            else:
                print(f"  [SocialLinks] Error: {result.error}")

            return result
        except Exception as e:
            return SocialLinksResult(
                query=name,
                error=str(e)
            )

    async def test_openweb_full_discovery(
        self,
        company_name: str,
        domain: str | None = None,
        location: str | None = None,
    ) -> dict:
        """
        Test full OpenWeb Ninja SMB discovery flow (all 3 APIs).

        Args:
            company_name: Business name
            domain: Website domain (if known)
            location: City/state for Google Maps search

        Returns:
            Dict with results from all 3 APIs
        """
        results = {
            "company_name": company_name,
            "domain": domain,
            "location": location,
            "google_maps": None,
            "web_contacts": None,
            "social_links": None,
            "owner_found": False,
            "email_found": False,
            "linkedin_found": False,
            "total_cost": 0.0,
        }

        # Stage 1: Google Maps (get owner, phone, website)
        print(f"\n[1/3] Google Maps: {company_name}")
        gmaps = await self.test_openweb_google_maps(company_name, location)
        results["google_maps"] = gmaps
        results["total_cost"] += 0.002

        if gmaps.success:
            if gmaps.owner_name:
                results["owner_found"] = True
            if gmaps.email:
                results["email_found"] = True
            # Get domain from Google Maps if not provided
            if not domain and gmaps.website:
                from urllib.parse import urlparse
                domain = urlparse(gmaps.website).netloc.replace("www.", "")
                results["domain"] = domain

        # Stage 2: Website Contacts (if we have a domain)
        if domain:
            print(f"\n[2/3] Website Contacts: {domain}")
            contacts = await self.test_openweb_contacts(domain)
            results["web_contacts"] = contacts
            results["total_cost"] += 0.002

            if contacts.success:
                if contacts.emails:
                    results["email_found"] = True
                if contacts.linkedin:
                    results["linkedin_found"] = True
        else:
            print(f"\n[2/3] Website Contacts: SKIPPED (no domain)")

        # Stage 3: Social Links (if we found an owner name)
        if results["owner_found"]:
            owner_name = gmaps.owner_name
            search_query = f"{owner_name} {company_name}"
            print(f"\n[3/3] Social Links: {search_query}")
            social = await self.test_openweb_social_links(search_query)
            results["social_links"] = social
            results["total_cost"] += 0.002

            if social.success:
                results["linkedin_found"] = True
        else:
            print(f"\n[3/3] Social Links: SKIPPED (no owner found)")

        # Summary
        print(f"\n=== Discovery Summary ===")
        print(f"  Owner found: {results['owner_found']}")
        print(f"  Email found: {results['email_found']}")
        print(f"  LinkedIn found: {results['linkedin_found']}")
        print(f"  Total cost: ${results['total_cost']:.4f}")

        return results

    def _fuzzy_match(self, str1: str | None, str2: str | None, threshold: float = 0.8) -> bool:
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
            if overlap >= threshold:
                return True

        return False

    async def verify_with_llm(
        self,
        ground_truth: LinkedInConnection,
        enrichments: dict[str, EnrichmentResult],
    ) -> VerificationResult:
        """
        Use LLM to verify if the enriched data matches ground truth.

        Checks:
        1. Is this the right person?
        2. Do they currently work at the expected company?
        """
        if not self.openai_key:
            # Simple rule-based verification if no LLM
            return self._rule_based_verification(ground_truth, enrichments)

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.openai_key)

            # Build context from all enrichment sources
            enrichment_context = []
            for source, result in enrichments.items():
                if result.success:
                    enrichment_context.append(f"""
Source: {source}
Name: {result.name}
Title: {result.title}
Company: {result.company}
Recent Experiences:
{json.dumps(result.experiences[:3], indent=2)}
""")

            prompt = f"""Verify if this person's enriched data matches expectations.

EXPECTED (from LinkedIn connection):
- Name: {ground_truth.full_name}
- Company: {ground_truth.company}
- Title: {ground_truth.title}

ENRICHED DATA FROM MULTIPLE SOURCES:
{''.join(enrichment_context) if enrichment_context else 'No data from any source'}

Questions to answer:
1. Is this the SAME PERSON as expected? (name match)
2. Do they CURRENTLY work at "{ground_truth.company}"? (check recent experiences)

Consider:
- Name variations are OK (Bill vs William, Bob vs Robert)
- Title changes are OK if same company
- If they left the company (not in recent experiences), mark as NOT currently employed

Respond in JSON:
{{
  "is_same_person": true/false,
  "currently_employed": true/false,
  "confidence": 0-100,
  "reasoning": "brief explanation",
  "red_flags": ["list of concerns if any"]
}}"""

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data verification assistant. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            return VerificationResult(
                is_same_person=result.get("is_same_person", False),
                currently_employed=result.get("currently_employed", False),
                confidence=float(result.get("confidence", 0)),
                reasoning=result.get("reasoning", ""),
                red_flags=result.get("red_flags", []),
            )

        except Exception as e:
            # Fallback to rule-based
            return self._rule_based_verification(ground_truth, enrichments, error=str(e))

    def _rule_based_verification(
        self,
        ground_truth: LinkedInConnection,
        enrichments: dict[str, EnrichmentResult],
        error: str | None = None,
    ) -> VerificationResult:
        """Simple rule-based verification when LLM is not available"""
        is_same_person = False
        currently_employed = False
        confidence = 0
        red_flags = []

        if error:
            red_flags.append(f"LLM error: {error}")

        # Check each source
        for source, result in enrichments.items():
            if not result.success:
                continue

            # Name match
            if self._fuzzy_match(result.name, ground_truth.full_name):
                is_same_person = True
                confidence += 30

            # Company match in current position
            if result.company and self._fuzzy_match(result.company, ground_truth.company):
                currently_employed = True
                confidence += 40

            # Check experiences for company
            for exp in result.experiences[:3]:
                exp_company = exp.get('company')
                if exp_company and self._fuzzy_match(exp_company, ground_truth.company):
                    currently_employed = True
                    confidence += 20
                    break

        # Cap confidence at 100
        confidence = min(confidence, 100)

        if not is_same_person:
            red_flags.append("Name does not match")
        if not currently_employed:
            red_flags.append("Company not found in recent experiences")

        return VerificationResult(
            is_same_person=is_same_person,
            currently_employed=currently_employed,
            confidence=confidence,
            reasoning="Rule-based verification" + (f" (LLM failed: {error})" if error else ""),
            red_flags=red_flags,
        )

    async def test_connection(
        self,
        connection: LinkedInConnection,
        sources: list[str] = ['rapidapi', 'scrapin'],
        verify: bool = True,
    ) -> PipelineTestResult:
        """
        Test a single LinkedIn connection against enrichment sources.

        Args:
            connection: Ground truth from LinkedIn export
            sources: Which enrichment sources to use
            verify: Whether to run LLM verification

        Returns:
            PipelineTestResult with enrichment and verification data
        """
        result = PipelineTestResult(ground_truth=connection)
        start_time = datetime.now()

        # Run enrichment from all sources in parallel
        tasks = []
        source_list = []

        if 'rapidapi' in sources and self.rapidapi_key:
            tasks.append(self.enrich_with_rapidapi(connection.linkedin_url))
            source_list.append('rapidapi')

        if 'scrapin' in sources and self.scrapin_key:
            tasks.append(self.enrich_with_scrapin(connection.linkedin_url))
            source_list.append('scrapin')

        if 'leadmagic' in sources and self.leadmagic_key:
            tasks.append(self.enrich_with_leadmagic(connection.linkedin_url))
            source_list.append('leadmagic')

        if tasks:
            enrichment_results = await asyncio.gather(*tasks, return_exceptions=True)

            for source, enrichment in zip(source_list, enrichment_results):
                if isinstance(enrichment, Exception):
                    result.enrichments[source] = EnrichmentResult(
                        source=source,
                        success=False,
                        error=str(enrichment),
                    )
                else:
                    result.enrichments[source] = enrichment

        # Check if any source found data
        result.any_source_found_data = any(
            e.success for e in result.enrichments.values()
        )

        # Check if sources agree on name
        names = [e.name for e in result.enrichments.values() if e.success and e.name]
        if len(names) >= 2:
            result.sources_agree_on_name = self._fuzzy_match(names[0], names[1])
        elif len(names) == 1:
            result.sources_agree_on_name = True  # Only one source

        # Check if sources agree on company
        companies = [e.company for e in result.enrichments.values() if e.success and e.company]
        if len(companies) >= 2:
            result.sources_agree_on_company = self._fuzzy_match(companies[0], companies[1])
        elif len(companies) == 1:
            result.sources_agree_on_company = True

        # LLM verification
        if verify and result.any_source_found_data:
            result.verification = await self.verify_with_llm(connection, result.enrichments)

        # Total latency
        result.total_latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        return result

    async def run_batch(
        self,
        connections: list[LinkedInConnection],
        sources: list[str] = ['rapidapi', 'scrapin'],
        verify: bool = True,
        concurrency: int = 2,
        delay: float = 1.5,
        progress_callback: callable = None,
    ) -> list[PipelineTestResult]:
        """
        Run pipeline test on multiple connections.

        Args:
            connections: List of ground truth connections
            sources: Enrichment sources to use
            verify: Whether to run LLM verification
            concurrency: Max parallel requests
            delay: Delay between requests (rate limiting)
            progress_callback: Called with (current, total, result) after each

        Returns:
            List of PipelineTestResult
        """
        results = []
        semaphore = asyncio.Semaphore(concurrency)

        async def process_one(idx: int, conn: LinkedInConnection) -> PipelineTestResult:
            async with semaphore:
                result = await self.test_connection(conn, sources=sources, verify=verify)

                if progress_callback:
                    progress_callback(idx + 1, len(connections), result)

                # Rate limiting
                await asyncio.sleep(delay)

                return result

        # Process all connections
        tasks = [process_one(i, conn) for i, conn in enumerate(connections)]
        results = await asyncio.gather(*tasks)

        return results


def generate_report(results: list[PipelineTestResult]) -> str:
    """Generate markdown report from test results"""

    total = len(results)
    if total == 0:
        return "# Pipeline Test Report\n\nNo results to report."

    # Calculate metrics
    any_data = sum(1 for r in results if r.any_source_found_data)

    rapidapi_success = sum(1 for r in results if r.enrichments.get('rapidapi', EnrichmentResult(source='', success=False)).success)
    scrapin_success = sum(1 for r in results if r.enrichments.get('scrapin', EnrichmentResult(source='', success=False)).success)
    leadmagic_success = sum(1 for r in results if r.enrichments.get('leadmagic', EnrichmentResult(source='', success=False)).success)

    verified = [r for r in results if r.verification]
    same_person = sum(1 for r in verified if r.verification.is_same_person)
    currently_employed = sum(1 for r in verified if r.verification.currently_employed)

    sources_agree_name = sum(1 for r in results if r.sources_agree_on_name)
    sources_agree_company = sum(1 for r in results if r.sources_agree_on_company)

    avg_latency = sum(r.total_latency_ms for r in results) / total if total > 0 else 0

    report = f"""# Contact Discovery Pipeline Test Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value | Percentage |
|--------|-------|------------|
| Total Tested | {total} | - |
| Any Source Found Data | {any_data} | {any_data/total*100:.1f}% |
| RapidAPI Success | {rapidapi_success} | {rapidapi_success/total*100:.1f}% |
| Scrapin Success | {scrapin_success} | {scrapin_success/total*100:.1f}% |
| LeadMagic Success | {leadmagic_success} | {leadmagic_success/total*100:.1f}% |
| Sources Agree (Name) | {sources_agree_name} | {sources_agree_name/total*100:.1f}% |
| Sources Agree (Company) | {sources_agree_company} | {sources_agree_company/total*100:.1f}% |

## Verification Results

| Metric | Value | Percentage |
|--------|-------|------------|
| Verified Total | {len(verified)} | - |
| Same Person Confirmed | {same_person} | {same_person/len(verified)*100:.1f}% if verified else 0% |
| Currently Employed | {currently_employed} | {currently_employed/len(verified)*100:.1f}% if verified else 0% |

## Performance

- Average Latency: {avg_latency:.0f}ms

## Sample Results

"""

    # Add sample results
    for i, r in enumerate(results[:10]):
        gt = r.ground_truth
        report += f"""
### {i+1}. {gt.full_name}
- **Expected**: {gt.title} at {gt.company}
- **LinkedIn**: {gt.linkedin_url}
"""

        for source, enrichment in r.enrichments.items():
            if enrichment.success:
                report += f"- **{source}**: {enrichment.name} | {enrichment.title} | {enrichment.company}\n"
            else:
                report += f"- **{source}**: FAILED - {enrichment.error}\n"

        if r.verification:
            v = r.verification
            report += f"- **Verification**: Same person: {v.is_same_person}, Currently employed: {v.currently_employed}, Confidence: {v.confidence}%\n"
            if v.red_flags:
                report += f"- **Red flags**: {', '.join(v.red_flags)}\n"

    return report
