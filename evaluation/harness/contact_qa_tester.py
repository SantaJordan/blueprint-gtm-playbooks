"""
Contact QA Tester

Comprehensive testing framework for comparing enrichment APIs against
LinkedIn connections export as ground truth.

Test Scenarios:
1. Person Lookup: LinkedIn URL -> verify name/company/title
2. Email Lookup: Email -> verify returns correct LinkedIn URL
3. Company Search: Company + title -> find exact person (future)
"""

import asyncio
import csv
import io
import os
import re
import sys
import time
import zipfile
from dataclasses import dataclass, field, asdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
import logging

import pandas as pd

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "contact-finder"))

from .cache import EvaluationCache
from .rapidapi_linkedin import RapidAPILinkedInClient, RapidAPIPersonResult

logger = logging.getLogger(__name__)


@dataclass
class LinkedInContact:
    """A contact from LinkedIn export - ground truth"""
    first_name: str
    last_name: str
    full_name: str
    linkedin_url: str
    email: str | None
    company: str | None
    position: str | None
    connected_on: str | None

    @property
    def has_email(self) -> bool:
        return bool(self.email)


@dataclass
class QATestResult:
    """Result of testing one API call against ground truth"""
    scenario: str  # person_lookup, email_lookup, company_search
    api_name: str  # rapidapi, blitz, scrapin, leadmagic
    ground_truth_url: str

    # Ground truth values
    gt_name: str
    gt_email: str | None
    gt_company: str | None
    gt_position: str | None

    # API returned values
    api_returned: bool = False
    api_name_found: str | None = None
    api_email_found: str | None = None
    api_company_found: str | None = None
    api_title_found: str | None = None
    api_linkedin_url: str | None = None

    # Match results
    name_match: bool = False
    name_similarity: float = 0.0
    email_match: bool = False
    company_match: bool = False
    company_similarity: float = 0.0
    linkedin_match: bool = False

    # Performance
    latency_ms: int = 0
    cached: bool = False

    # Error info
    error: str | None = None


@dataclass
class QAScenarioMetrics:
    """Aggregated metrics for one scenario/API combination"""
    scenario: str
    api_name: str
    total_tested: int = 0

    # Coverage and accuracy
    coverage: float = 0.0  # % where API returned any data
    name_match_rate: float = 0.0  # % where name matched (fuzzy)
    email_match_rate: float = 0.0  # % where email matched (exact)
    company_match_rate: float = 0.0  # % where company matched (fuzzy)
    linkedin_match_rate: float = 0.0  # % where LinkedIn URL matched

    # Latency stats (ms)
    latency_mean: float = 0.0
    latency_p50: float = 0.0
    latency_p95: float = 0.0

    # Error rate
    error_rate: float = 0.0

    # Detailed results
    results: list[QATestResult] = field(default_factory=list)


class ContactQATester:
    """
    Main QA testing framework.

    Usage:
        tester = ContactQATester(cache_path="./cache.db")

        # Load ground truth from LinkedIn export
        tester.load_linkedin_export("./Complete_LinkedInDataExport.zip")

        # Run tests
        results = await tester.run_person_lookup_test(
            apis=["rapidapi", "scrapin"],
            sample_size=100
        )

        # Print summary
        tester.print_summary(results)

        # Generate report
        tester.generate_report(results, "./report.md")
    """

    # Supported APIs
    SUPPORTED_APIS = ["rapidapi", "blitz", "scrapin", "leadmagic"]

    def __init__(
        self,
        cache_path: str | Path = "./evaluation/data/cache.db"
    ):
        self.cache = EvaluationCache(cache_path)
        self._clients: dict[str, Any] = {}
        self.ground_truth: list[LinkedInContact] = []

    # -------------------------------------------------------------------------
    # Ground Truth Loading
    # -------------------------------------------------------------------------

    def load_linkedin_export(self, zip_path: str | Path) -> int:
        """
        Load LinkedIn connections export as ground truth.

        Args:
            zip_path: Path to LinkedIn export zip file

        Returns:
            Number of contacts loaded
        """
        zip_path = Path(zip_path)
        if not zip_path.exists():
            raise FileNotFoundError(f"LinkedIn export not found: {zip_path}")

        with zipfile.ZipFile(zip_path, 'r') as zf:
            with zf.open("Connections.csv") as f:
                content = f.read().decode('utf-8')

        # Skip header notes (first 3-4 lines until "First Name,")
        lines = content.split('\n')
        header_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("First Name"):
                header_idx = i
                break

        csv_content = '\n'.join(lines[header_idx:])
        reader = csv.DictReader(io.StringIO(csv_content))

        self.ground_truth = []
        for row in reader:
            first_name = row.get("First Name", "").strip()
            last_name = row.get("Last Name", "").strip()

            if not first_name:
                continue

            # Clean up names with credentials like "PMP, CSP-SM"
            last_name = self._clean_name(last_name)

            contact = LinkedInContact(
                first_name=first_name,
                last_name=last_name,
                full_name=f"{first_name} {last_name}".strip(),
                linkedin_url=row.get("URL", "").strip(),
                email=row.get("Email Address", "").strip() or None,
                company=row.get("Company", "").strip() or None,
                position=row.get("Position", "").strip() or None,
                connected_on=row.get("Connected On", "").strip() or None
            )

            if contact.linkedin_url:
                self.ground_truth.append(contact)

        logger.info(f"Loaded {len(self.ground_truth)} contacts from LinkedIn export")
        logger.info(f"  - {sum(1 for c in self.ground_truth if c.has_email)} have verified email")

        return len(self.ground_truth)

    def _clean_name(self, name: str) -> str:
        """Remove credentials and suffixes from name"""
        # Remove common credentials
        credentials = r',?\s*(PMP|CSP-SM|CSP|MBA|PhD|MD|CPA|Esq|Jr|Sr|II|III|IV|A-CSPO|CSPO)\.?'
        name = re.sub(credentials, '', name, flags=re.IGNORECASE)
        # Remove trailing commas/spaces
        name = re.sub(r',\s*$', '', name).strip()
        return name

    def get_contacts_with_email(self) -> list[LinkedInContact]:
        """Get only contacts that have verified email"""
        return [c for c in self.ground_truth if c.has_email]

    def sample_contacts(
        self,
        n: int,
        email_only: bool = False,
        seed: int = 42
    ) -> list[LinkedInContact]:
        """Get a random sample of contacts"""
        import random
        random.seed(seed)

        pool = self.get_contacts_with_email() if email_only else self.ground_truth

        if n >= len(pool):
            return pool

        return random.sample(pool, n)

    # -------------------------------------------------------------------------
    # API Clients
    # -------------------------------------------------------------------------

    async def _get_client(self, api_name: str):
        """Get or create API client"""
        if api_name in self._clients:
            return self._clients[api_name]

        client = None

        if api_name == "rapidapi":
            key = os.environ.get("RAPIDAPI_KEY")
            if key:
                client = RapidAPILinkedInClient(key)

        elif api_name == "blitz":
            key = os.environ.get("BLITZ_API_KEY")
            if key:
                from modules.enrichment.blitz import BlitzClient
                client = BlitzClient(key)

        elif api_name == "scrapin":
            key = os.environ.get("SCRAPIN_API_KEY")
            if key:
                from modules.enrichment.scrapin import ScrapinClient
                client = ScrapinClient(key)

        elif api_name == "leadmagic":
            key = os.environ.get("LEADMAGIC_API_KEY")
            if key:
                from modules.enrichment.leadmagic import LeadMagicClient
                client = LeadMagicClient(key)

        if client:
            self._clients[api_name] = client

        return client

    async def close(self):
        """Close all API clients"""
        for client in self._clients.values():
            if hasattr(client, 'close'):
                await client.close()

    # -------------------------------------------------------------------------
    # Matching Logic
    # -------------------------------------------------------------------------

    def _normalize_name(self, name: str | None) -> str:
        """Normalize name for comparison"""
        if not name:
            return ""
        name = name.lower().strip()
        # Remove credentials
        name = re.sub(r',?\s*(pmp|csp|csm|mba|phd|md|cpa|esq|jr|sr|ii|iii)\.?', '', name, flags=re.I)
        name = re.sub(r',\s*$', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name

    def _names_match(self, name1: str | None, name2: str | None) -> tuple[bool, float]:
        """
        Check if names match with fuzzy matching.
        Returns (match, similarity_score)
        """
        n1 = self._normalize_name(name1)
        n2 = self._normalize_name(name2)

        if not n1 or not n2:
            return False, 0.0

        # Exact match
        if n1 == n2:
            return True, 1.0

        # Containment (handles "Jack Coyle" vs "Jack Thomas Coyle")
        if n1 in n2 or n2 in n1:
            return True, 0.9

        # Fuzzy match
        similarity = SequenceMatcher(None, n1, n2).ratio()
        return similarity >= 0.85, similarity

    def _emails_match(self, email1: str | None, email2: str | None) -> bool:
        """Check if emails match exactly (case-insensitive)"""
        if not email1 or not email2:
            return False
        return email1.lower().strip() == email2.lower().strip()

    def _companies_match(self, company1: str | None, company2: str | None) -> tuple[bool, float]:
        """Check if companies match with fuzzy matching"""
        if not company1 or not company2:
            return False, 0.0

        c1 = company1.lower().strip()
        c2 = company2.lower().strip()

        if c1 == c2:
            return True, 1.0

        if c1 in c2 or c2 in c1:
            return True, 0.9

        similarity = SequenceMatcher(None, c1, c2).ratio()
        return similarity >= 0.8, similarity

    def _linkedin_urls_match(self, url1: str | None, url2: str | None) -> bool:
        """Check if LinkedIn URLs point to same profile"""
        if not url1 or not url2:
            return False

        def normalize_url(url: str) -> str:
            url = url.lower().strip().rstrip('/')
            # Extract username from URL
            match = re.search(r'linkedin\.com/in/([^/?]+)', url)
            if match:
                return match.group(1)
            return url

        return normalize_url(url1) == normalize_url(url2)

    # -------------------------------------------------------------------------
    # Test Execution - Person Lookup
    # -------------------------------------------------------------------------

    async def _test_person_lookup_rapidapi(
        self,
        contact: LinkedInContact
    ) -> QATestResult:
        """Test RapidAPI person lookup for one contact"""
        result = QATestResult(
            scenario="person_lookup",
            api_name="rapidapi",
            ground_truth_url=contact.linkedin_url,
            gt_name=contact.full_name,
            gt_email=contact.email,
            gt_company=contact.company,
            gt_position=contact.position
        )

        # Check cache first
        cache_key = f"rapidapi_person:{contact.linkedin_url}"
        cached = self.cache.get("rapidapi_person", contact.linkedin_url)

        if cached:
            result.cached = True
            api_result = cached
        else:
            client = await self._get_client("rapidapi")
            if not client:
                result.error = "No RAPIDAPI_KEY"
                return result

            api_response = await client.get_person(contact.linkedin_url)
            result.latency_ms = api_response.latency_ms

            # Cache the response
            api_result = asdict(api_response)
            self.cache.set("rapidapi_person", contact.linkedin_url, response=api_result)

        # Parse results
        if api_result.get("status", "").startswith("error"):
            result.error = api_result.get("status")
            return result

        result.api_returned = bool(api_result.get("name"))
        result.api_name_found = api_result.get("name")
        result.api_company_found = api_result.get("company")
        result.api_title_found = api_result.get("title")
        result.api_linkedin_url = api_result.get("linkedin_url")

        # Calculate matches
        if result.api_returned:
            result.name_match, result.name_similarity = self._names_match(
                contact.full_name, result.api_name_found
            )
            result.company_match, result.company_similarity = self._companies_match(
                contact.company, result.api_company_found
            )

        return result

    async def _test_person_lookup_scrapin(
        self,
        contact: LinkedInContact
    ) -> QATestResult:
        """Test Scrapin person lookup for one contact"""
        result = QATestResult(
            scenario="person_lookup",
            api_name="scrapin",
            ground_truth_url=contact.linkedin_url,
            gt_name=contact.full_name,
            gt_email=contact.email,
            gt_company=contact.company,
            gt_position=contact.position
        )

        # Check cache first
        cached = self.cache.get("scrapin", "person", contact.linkedin_url)

        if cached:
            result.cached = True
            api_result = cached
        else:
            client = await self._get_client("scrapin")
            if not client:
                result.error = "No SCRAPIN_API_KEY"
                return result

            start = time.time()
            try:
                api_response = await client.get_person_profile(contact.linkedin_url)
                result.latency_ms = int((time.time() - start) * 1000)

                api_result = {
                    "full_name": api_response.full_name,
                    "title": api_response.title,
                    "company": api_response.company,
                    "linkedin_url": api_response.linkedin_url
                }
                self.cache.set("scrapin", "person", contact.linkedin_url, response=api_result)
            except Exception as e:
                result.error = str(e)
                result.latency_ms = int((time.time() - start) * 1000)
                return result

        result.api_returned = bool(api_result.get("full_name"))
        result.api_name_found = api_result.get("full_name")
        result.api_company_found = api_result.get("company")
        result.api_title_found = api_result.get("title")
        result.api_linkedin_url = api_result.get("linkedin_url")

        if result.api_returned:
            result.name_match, result.name_similarity = self._names_match(
                contact.full_name, result.api_name_found
            )
            result.company_match, result.company_similarity = self._companies_match(
                contact.company, result.api_company_found
            )

        return result

    async def run_person_lookup_test(
        self,
        apis: list[str] | None = None,
        sample_size: int = 100,
        seed: int = 42,
        progress_callback: callable = None
    ) -> dict[str, QAScenarioMetrics]:
        """
        Run person lookup test: LinkedIn URL -> verify name/company/title

        Args:
            apis: List of APIs to test (default: all supported)
            sample_size: Number of contacts to test
            seed: Random seed for sampling
            progress_callback: Function(api, idx, total, result) called after each test

        Returns:
            Dict of API name -> QAScenarioMetrics
        """
        apis = apis or ["rapidapi", "scrapin"]
        contacts = self.sample_contacts(sample_size, seed=seed)

        logger.info(f"Running person_lookup test on {len(contacts)} contacts")

        results: dict[str, QAScenarioMetrics] = {}

        for api in apis:
            metrics = QAScenarioMetrics(
                scenario="person_lookup",
                api_name=api,
                total_tested=len(contacts)
            )

            for idx, contact in enumerate(contacts, 1):
                # Run test based on API
                if api == "rapidapi":
                    result = await self._test_person_lookup_rapidapi(contact)
                elif api == "scrapin":
                    result = await self._test_person_lookup_scrapin(contact)
                elif api == "blitz":
                    # Blitz doesn't support person profile lookup - skip
                    logger.warning(f"Blitz doesn't support person_lookup, skipping")
                    continue
                else:
                    continue

                metrics.results.append(result)

                if progress_callback:
                    progress_callback(api, idx, len(contacts), result)

            # Calculate aggregate metrics
            self._calculate_scenario_metrics(metrics)
            results[api] = metrics

        return results

    # -------------------------------------------------------------------------
    # Test Execution - Email Lookup
    # -------------------------------------------------------------------------

    async def _test_email_lookup_rapidapi(
        self,
        contact: LinkedInContact
    ) -> QATestResult:
        """Test RapidAPI email->LinkedIn lookup for one contact"""
        result = QATestResult(
            scenario="email_lookup",
            api_name="rapidapi",
            ground_truth_url=contact.linkedin_url,
            gt_name=contact.full_name,
            gt_email=contact.email,
            gt_company=contact.company,
            gt_position=contact.position
        )

        if not contact.email:
            result.error = "No ground truth email"
            return result

        # Check cache first
        cached = self.cache.get("rapidapi_email", contact.email)

        if cached:
            result.cached = True
            api_result = cached
        else:
            client = await self._get_client("rapidapi")
            if not client:
                result.error = "No RAPIDAPI_KEY"
                return result

            api_response = await client.email_to_linkedin(contact.email)
            result.latency_ms = api_response.latency_ms

            api_result = asdict(api_response)
            self.cache.set("rapidapi_email", contact.email, response=api_result)

        if api_result.get("status", "").startswith("error"):
            result.error = api_result.get("status")
            return result

        result.api_returned = bool(api_result.get("linkedin_url"))
        result.api_linkedin_url = api_result.get("linkedin_url")
        result.api_name_found = api_result.get("name")

        if result.api_returned:
            result.linkedin_match = self._linkedin_urls_match(
                contact.linkedin_url, result.api_linkedin_url
            )
            if result.api_name_found:
                result.name_match, result.name_similarity = self._names_match(
                    contact.full_name, result.api_name_found
                )

        return result

    async def run_email_lookup_test(
        self,
        apis: list[str] | None = None,
        sample_size: int | None = None,
        seed: int = 42,
        progress_callback: callable = None
    ) -> dict[str, QAScenarioMetrics]:
        """
        Run email lookup test: Email -> verify returns correct LinkedIn URL

        Args:
            apis: List of APIs to test (default: rapidapi only)
            sample_size: Number of contacts to test (default: all with email)
            seed: Random seed for sampling
            progress_callback: Function(api, idx, total, result) called after each test

        Returns:
            Dict of API name -> QAScenarioMetrics
        """
        apis = apis or ["rapidapi"]
        contacts = self.get_contacts_with_email()

        if sample_size and sample_size < len(contacts):
            import random
            random.seed(seed)
            contacts = random.sample(contacts, sample_size)

        logger.info(f"Running email_lookup test on {len(contacts)} contacts with email")

        results: dict[str, QAScenarioMetrics] = {}

        for api in apis:
            metrics = QAScenarioMetrics(
                scenario="email_lookup",
                api_name=api,
                total_tested=len(contacts)
            )

            for idx, contact in enumerate(contacts, 1):
                if api == "rapidapi":
                    result = await self._test_email_lookup_rapidapi(contact)
                else:
                    continue

                metrics.results.append(result)

                if progress_callback:
                    progress_callback(api, idx, len(contacts), result)

            self._calculate_scenario_metrics(metrics)
            results[api] = metrics

        return results

    # -------------------------------------------------------------------------
    # Test Execution - Email Enrichment (LinkedIn URL -> Email)
    # -------------------------------------------------------------------------

    async def _test_email_enrichment_blitz(
        self,
        contact: LinkedInContact
    ) -> QATestResult:
        """Test Blitz email enrichment: LinkedIn URL -> email"""
        result = QATestResult(
            scenario="email_enrichment",
            api_name="blitz",
            ground_truth_url=contact.linkedin_url,
            gt_name=contact.full_name,
            gt_email=contact.email,
            gt_company=contact.company,
            gt_position=contact.position
        )

        if not contact.email:
            result.error = "No ground truth email to verify"
            return result

        # Check cache first
        cached = self.cache.get("blitz", "email", contact.linkedin_url)

        if cached:
            result.cached = True
            api_result = cached
        else:
            client = await self._get_client("blitz")
            if not client:
                result.error = "No BLITZ_API_KEY"
                return result

            start = time.time()
            try:
                api_response = await client.find_email(contact.linkedin_url)
                result.latency_ms = int((time.time() - start) * 1000)

                api_result = {
                    "email": api_response.email,
                    "status": api_response.status,
                    "credits_consumed": api_response.credits_consumed
                }
                self.cache.set("blitz", "email", contact.linkedin_url, response=api_result)
            except Exception as e:
                result.error = str(e)
                result.latency_ms = int((time.time() - start) * 1000)
                return result

        if "error" in api_result.get("status", "").lower():
            result.error = api_result.get("status")
            return result

        result.api_returned = bool(api_result.get("email"))
        result.api_email_found = api_result.get("email")

        if result.api_returned:
            result.email_match = self._emails_match(contact.email, result.api_email_found)

        return result

    async def _test_email_enrichment_scrapin(
        self,
        contact: LinkedInContact
    ) -> QATestResult:
        """Test Scrapin email enrichment: LinkedIn URL -> email"""
        result = QATestResult(
            scenario="email_enrichment",
            api_name="scrapin",
            ground_truth_url=contact.linkedin_url,
            gt_name=contact.full_name,
            gt_email=contact.email,
            gt_company=contact.company,
            gt_position=contact.position
        )

        if not contact.email:
            result.error = "No ground truth email to verify"
            return result

        # Check cache first
        cached = self.cache.get("scrapin", "email", contact.linkedin_url)

        if cached:
            result.cached = True
            api_result = cached
        else:
            client = await self._get_client("scrapin")
            if not client:
                result.error = "No SCRAPIN_API_KEY"
                return result

            start = time.time()
            try:
                api_response = await client.find_email(linkedin_url=contact.linkedin_url)
                result.latency_ms = int((time.time() - start) * 1000)

                api_result = {
                    "email": api_response.email,
                    "email_type": api_response.email_type,
                    "confidence": api_response.confidence
                }
                self.cache.set("scrapin", "email", contact.linkedin_url, response=api_result)
            except Exception as e:
                result.error = str(e)
                result.latency_ms = int((time.time() - start) * 1000)
                return result

        result.api_returned = bool(api_result.get("email"))
        result.api_email_found = api_result.get("email")

        if result.api_returned:
            result.email_match = self._emails_match(contact.email, result.api_email_found)

        return result

    async def run_email_enrichment_test(
        self,
        apis: list[str] | None = None,
        sample_size: int | None = None,
        seed: int = 42,
        progress_callback: callable = None
    ) -> dict[str, QAScenarioMetrics]:
        """
        Run email enrichment test: LinkedIn URL -> verify returned email matches ground truth

        Args:
            apis: List of APIs to test (default: blitz, scrapin)
            sample_size: Number of contacts to test (default: all with email)
            seed: Random seed for sampling
            progress_callback: Function(api, idx, total, result) called after each test

        Returns:
            Dict of API name -> QAScenarioMetrics
        """
        apis = apis or ["blitz", "scrapin"]
        contacts = self.get_contacts_with_email()

        if sample_size and sample_size < len(contacts):
            import random
            random.seed(seed)
            contacts = random.sample(contacts, sample_size)

        logger.info(f"Running email_enrichment test on {len(contacts)} contacts with verified email")

        results: dict[str, QAScenarioMetrics] = {}

        for api in apis:
            metrics = QAScenarioMetrics(
                scenario="email_enrichment",
                api_name=api,
                total_tested=len(contacts)
            )

            for idx, contact in enumerate(contacts, 1):
                if api == "blitz":
                    result = await self._test_email_enrichment_blitz(contact)
                elif api == "scrapin":
                    result = await self._test_email_enrichment_scrapin(contact)
                else:
                    continue

                metrics.results.append(result)

                if progress_callback:
                    progress_callback(api, idx, len(contacts), result)

            self._calculate_scenario_metrics(metrics)
            results[api] = metrics

        return results

    # -------------------------------------------------------------------------
    # Metrics Calculation
    # -------------------------------------------------------------------------

    def _calculate_scenario_metrics(self, metrics: QAScenarioMetrics):
        """Calculate aggregate metrics from individual results"""
        if not metrics.results:
            return

        n = len(metrics.results)
        returned = [r for r in metrics.results if r.api_returned]
        errors = [r for r in metrics.results if r.error]

        # Coverage and accuracy
        metrics.coverage = len(returned) / n * 100 if n > 0 else 0
        metrics.error_rate = len(errors) / n * 100 if n > 0 else 0

        # Name match rate (of those returned)
        name_matches = sum(1 for r in returned if r.name_match)
        metrics.name_match_rate = name_matches / n * 100 if n > 0 else 0

        # Company match rate (of those with ground truth company)
        with_gt_company = [r for r in metrics.results if r.gt_company]
        company_matches = sum(1 for r in with_gt_company if r.company_match)
        metrics.company_match_rate = (
            company_matches / len(with_gt_company) * 100
            if with_gt_company else 0
        )

        # Email match rate (for person_lookup scenario)
        with_gt_email = [r for r in metrics.results if r.gt_email]
        email_matches = sum(1 for r in with_gt_email if r.email_match)
        metrics.email_match_rate = (
            email_matches / len(with_gt_email) * 100
            if with_gt_email else 0
        )

        # LinkedIn match rate (for email_lookup scenario)
        linkedin_matches = sum(1 for r in returned if r.linkedin_match)
        metrics.linkedin_match_rate = linkedin_matches / n * 100 if n > 0 else 0

        # Latency (exclude cached and errors)
        latencies = [r.latency_ms for r in metrics.results if r.latency_ms > 0 and not r.cached]
        if latencies:
            latencies.sort()
            metrics.latency_mean = sum(latencies) / len(latencies)
            metrics.latency_p50 = latencies[len(latencies) // 2]
            metrics.latency_p95 = latencies[int(len(latencies) * 0.95)]

    # -------------------------------------------------------------------------
    # Output and Reporting
    # -------------------------------------------------------------------------

    def print_progress(self, api: str, idx: int, total: int, result: QATestResult):
        """Print progress inline during test execution"""
        status = "?" if result.error else ("+" if result.api_returned else "-")

        match_indicators = ""
        if result.name_match:
            match_indicators += "N"
        if result.company_match:
            match_indicators += "C"
        if result.email_match:
            match_indicators += "E"
        if result.linkedin_match:
            match_indicators += "L"

        cached = " (cached)" if result.cached else ""

        name = result.gt_name[:25] if result.gt_name else "Unknown"
        print(f"  [{idx}/{total}] {status} {name:<25} {match_indicators or '-':<4}{cached}")

    def print_summary(self, all_results: dict[str, QAScenarioMetrics]):
        """Print summary table"""
        if not all_results:
            print("No results to display")
            return

        # Get scenario from first result
        scenario = list(all_results.values())[0].scenario

        print("\n" + "=" * 80)
        print(f"RESULTS: {scenario}")
        print("=" * 80)

        if scenario == "person_lookup":
            print(f"{'Source':<12} {'Coverage':>10} {'Name Match':>12} {'Company Match':>14} {'Latency p50':>12}")
            print("-" * 80)

            for api, metrics in sorted(all_results.items()):
                print(f"{api:<12} {metrics.coverage:>9.1f}% {metrics.name_match_rate:>11.1f}% "
                      f"{metrics.company_match_rate:>13.1f}% {metrics.latency_p50:>11.0f}ms")

        elif scenario == "email_lookup":
            print(f"{'Source':<12} {'Coverage':>10} {'LinkedIn Match':>15} {'Name Match':>12} {'Latency p50':>12}")
            print("-" * 80)

            for api, metrics in sorted(all_results.items()):
                print(f"{api:<12} {metrics.coverage:>9.1f}% {metrics.linkedin_match_rate:>14.1f}% "
                      f"{metrics.name_match_rate:>11.1f}% {metrics.latency_p50:>11.0f}ms")

        elif scenario == "email_enrichment":
            print(f"{'Source':<12} {'Coverage':>10} {'Email Match':>12} {'Latency p50':>12} {'Error Rate':>12}")
            print("-" * 80)

            for api, metrics in sorted(all_results.items()):
                print(f"{api:<12} {metrics.coverage:>9.1f}% {metrics.email_match_rate:>11.1f}% "
                      f"{metrics.latency_p50:>11.0f}ms {metrics.error_rate:>11.1f}%")

        print("=" * 80)

    def generate_report(
        self,
        all_results: dict[str, dict[str, QAScenarioMetrics]],
        output_path: str | Path
    ):
        """
        Generate markdown report.

        Args:
            all_results: Dict of scenario -> {api -> metrics}
            output_path: Path for output markdown file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "# Contact QA Test Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Ground Truth:** {len(self.ground_truth)} LinkedIn connections "
            f"({sum(1 for c in self.ground_truth if c.has_email)} with verified email)",
            "",
            "---",
            ""
        ]

        for scenario, api_results in all_results.items():
            lines.append(f"## {scenario.replace('_', ' ').title()}")
            lines.append("")

            if scenario == "person_lookup":
                lines.append("| Source | Coverage | Name Match | Company Match | Latency p50 | Errors |")
                lines.append("|--------|----------|------------|---------------|-------------|--------|")

                for api, metrics in sorted(api_results.items()):
                    lines.append(
                        f"| {api} | {metrics.coverage:.1f}% | {metrics.name_match_rate:.1f}% | "
                        f"{metrics.company_match_rate:.1f}% | {metrics.latency_p50:.0f}ms | {metrics.error_rate:.1f}% |"
                    )

            elif scenario == "email_lookup":
                lines.append("| Source | Coverage | LinkedIn Match | Name Match | Latency p50 | Errors |")
                lines.append("|--------|----------|----------------|------------|-------------|--------|")

                for api, metrics in sorted(api_results.items()):
                    lines.append(
                        f"| {api} | {metrics.coverage:.1f}% | {metrics.linkedin_match_rate:.1f}% | "
                        f"{metrics.name_match_rate:.1f}% | {metrics.latency_p50:.0f}ms | {metrics.error_rate:.1f}% |"
                    )

            elif scenario == "email_enrichment":
                lines.append("| Source | Coverage | Email Match | Latency p50 | Errors |")
                lines.append("|--------|----------|-------------|-------------|--------|")

                for api, metrics in sorted(api_results.items()):
                    lines.append(
                        f"| {api} | {metrics.coverage:.1f}% | {metrics.email_match_rate:.1f}% | "
                        f"{metrics.latency_p50:.0f}ms | {metrics.error_rate:.1f}% |"
                    )

            lines.append("")

        # Write report
        output_path.write_text("\n".join(lines))
        logger.info(f"Report saved to {output_path}")
