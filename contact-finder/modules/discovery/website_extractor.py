"""
Website Contact Extractor - Extract owner/contact info from SMB websites

Uses ZenRows for scale + Schema.org parsing + page scraping.
Designed to RIP through websites at scale.
"""

import asyncio
import json
import os
import re
import logging
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urljoin, urlparse
import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class ExtractedContact:
    """Contact found on website"""
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    linkedin_url: str | None = None
    source_page: str = ""
    source_type: str = ""  # schema_org, page_scrape, meta_tags
    confidence: float = 0.0


@dataclass
class WebsiteExtractionResult:
    """Result of extracting contacts from a website"""
    domain: str
    contacts: list[ExtractedContact] = field(default_factory=list)
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    company_name: str | None = None
    pages_scraped: int = 0
    errors: list[str] = field(default_factory=list)
    has_schema_org: bool = False


class WebsiteContactExtractor:
    """
    Extract contact info from SMB websites at scale.

    Uses ZenRows for reliable scraping, parses Schema.org,
    and extracts from contact/about pages.
    """

    # Pages to scrape (ordered by priority)
    CONTACT_PAGES = [
        "",           # homepage
        "contact",
        "contact-us",
        "about",
        "about-us",
        "team",
        "our-team",
        "leadership",
        "staff",
        "meet-the-team",
    ]

    # Owner-related keywords
    OWNER_KEYWORDS = [
        "owner", "founder", "president", "ceo", "chief executive",
        "proprietor", "principal", "managing partner", "general manager"
    ]

    # Email regex
    EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    # Phone regex
    PHONE_REGEX = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

    # LinkedIn URL regex
    LINKEDIN_REGEX = re.compile(r'linkedin\.com/in/([a-zA-Z0-9\-]+)')

    # Blacklist emails
    EMAIL_BLACKLIST = {
        'noreply', 'no-reply', 'info', 'contact', 'support', 'help',
        'sales', 'marketing', 'admin', 'webmaster', 'postmaster'
    }

    def __init__(
        self,
        zenrows_api_key: str | None = None,
        timeout: int = 15,
        max_pages: int = 5,
        concurrency: int = 5
    ):
        self.zenrows_api_key = zenrows_api_key or os.environ.get("ZENROWS_API_KEY")
        self.timeout = timeout
        self.max_pages = max_pages
        self.concurrency = concurrency
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _fetch_url(self, url: str, use_zenrows: bool = True) -> str | None:
        """Fetch URL content, using ZenRows for reliability"""
        session = await self._get_session()

        # Try ZenRows first (reliable for scale)
        if use_zenrows and self.zenrows_api_key:
            try:
                zenrows_url = "https://api.zenrows.com/v1/"
                params = {
                    "url": url,
                    "apikey": self.zenrows_api_key,
                    "js_render": "false",
                    "premium_proxy": "true"
                }
                async with session.get(zenrows_url, params=params) as response:
                    if response.status == 200:
                        return await response.text()
            except Exception as e:
                logger.debug(f"ZenRows failed for {url}: {e}")

        # Fallback to direct request
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    if len(html) > 500:
                        return html
        except Exception as e:
            logger.debug(f"Direct request failed for {url}: {e}")

        return None

    def _extract_schema_org(self, html: str) -> list[dict]:
        """Extract JSON-LD Schema.org data"""
        schemas = []

        # Find all JSON-LD blocks
        pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)

        for match in matches:
            try:
                data = json.loads(match.strip())

                # Handle @graph array
                if isinstance(data, dict) and "@graph" in data:
                    schemas.extend(data["@graph"])
                elif isinstance(data, list):
                    schemas.extend(data)
                else:
                    schemas.append(data)
            except json.JSONDecodeError:
                continue

        return schemas

    def _extract_contacts_from_schema(self, schemas: list[dict], source_page: str) -> list[ExtractedContact]:
        """Extract contact info from Schema.org data"""
        contacts = []

        for schema in schemas:
            schema_type = schema.get("@type", "")

            # Person schema
            if schema_type == "Person" or "Person" in str(schema_type):
                contact = ExtractedContact(
                    name=schema.get("name"),
                    email=schema.get("email"),
                    phone=schema.get("telephone"),
                    title=schema.get("jobTitle"),
                    source_page=source_page,
                    source_type="schema_org",
                    confidence=0.9
                )
                if contact.name:
                    contacts.append(contact)

            # Organization schema - may have founder/employee
            elif schema_type in ("Organization", "LocalBusiness", "Store", "Restaurant"):
                # Check for founder
                founder = schema.get("founder")
                if founder:
                    if isinstance(founder, dict):
                        contact = ExtractedContact(
                            name=founder.get("name"),
                            email=founder.get("email"),
                            title="Founder",
                            source_page=source_page,
                            source_type="schema_org",
                            confidence=0.95
                        )
                        if contact.name:
                            contacts.append(contact)
                    elif isinstance(founder, str):
                        contacts.append(ExtractedContact(
                            name=founder,
                            title="Founder",
                            source_page=source_page,
                            source_type="schema_org",
                            confidence=0.9
                        ))

                # Check for employee array
                employees = schema.get("employee", [])
                if isinstance(employees, dict):
                    employees = [employees]
                for emp in employees[:5]:  # Limit
                    if isinstance(emp, dict):
                        contacts.append(ExtractedContact(
                            name=emp.get("name"),
                            email=emp.get("email"),
                            title=emp.get("jobTitle"),
                            source_page=source_page,
                            source_type="schema_org",
                            confidence=0.85
                        ))

                # Check for contact info
                if schema.get("email"):
                    contacts.append(ExtractedContact(
                        email=schema.get("email"),
                        phone=schema.get("telephone"),
                        source_page=source_page,
                        source_type="schema_org",
                        confidence=0.7
                    ))

        return [c for c in contacts if c.name or c.email]

    def _extract_emails(self, html: str, domain: str) -> list[str]:
        """Extract emails from HTML, filtering to domain emails"""
        all_emails = set(self.EMAIL_REGEX.findall(html))

        valid_emails = []
        for email in all_emails:
            email = email.lower()

            # Filter blacklist
            local_part = email.split("@")[0]
            if any(bl in local_part for bl in self.EMAIL_BLACKLIST):
                continue

            # Skip image files
            if any(email.endswith(ext) for ext in ['.png', '.jpg', '.gif', '.svg']):
                continue

            # Prefer domain emails
            if domain in email:
                valid_emails.insert(0, email)  # Priority
            elif any(email.endswith(d) for d in ['@gmail.com', '@yahoo.com', '@outlook.com']):
                # Personal email - might be owner
                valid_emails.append(email)

        return valid_emails[:10]

    def _extract_phones(self, html: str) -> list[str]:
        """Extract phone numbers"""
        phones = set()
        for match in self.PHONE_REGEX.findall(html):
            phone = re.sub(r'[^\d]', '', match)
            if len(phone) >= 10:
                phones.add(phone[-10:])
        return list(phones)[:5]

    # Common words that should NOT be names (includes business terms)
    INVALID_NAME_WORDS = {
        # Common words
        "the", "and", "or", "of", "is", "in", "on", "at", "to", "for", "with",
        "our", "we", "us", "you", "your", "this", "that", "which", "who",
        "also", "got", "get", "has", "have", "had", "was", "were", "are",
        "its", "their", "his", "her", "from", "into", "but", "not", "can",
        "will", "may", "about", "more", "just", "some", "any", "all", "new",
        "one", "two", "report", "project", "genesis", "contact", "here",
        # Business/Organization terms
        "business", "company", "corporation", "corp", "inc", "llc", "ltd",
        "group", "services", "solutions", "enterprises", "associates",
        "partners", "consulting", "management", "technology", "technologies",
        "systems", "health", "healthcare", "medical", "clinic", "center",
        "independent", "national", "regional", "local", "global", "international",
        "american", "western", "eastern", "northern", "southern", "central",
        "professional", "premier", "quality", "express", "complete", "total"
    }

    def _is_valid_name(self, name: str) -> bool:
        """Check if a string looks like a valid person name"""
        if not name:
            return False

        parts = name.split()

        # Must have 2-4 parts
        if len(parts) < 2 or len(parts) > 4:
            return False

        # Check each part
        for part in parts:
            # Part must be 2+ chars
            if len(part) < 2:
                return False
            # Must start with capital letter
            if not part[0].isupper():
                return False
            # Rest should be lowercase (allow O'Brien, McDonald etc)
            rest = part[1:]
            if not all(c.islower() or c in "'-" or (c.isupper() and i > 0) for i, c in enumerate(rest)):
                return False
            # Check against invalid words
            if part.lower() in self.INVALID_NAME_WORDS:
                return False

        return True

    def _extract_contacts_from_page(self, html: str, domain: str, source_page: str) -> list[ExtractedContact]:
        """Extract contacts by parsing page content"""
        contacts = []

        # Look for owner/founder patterns (case-sensitive for proper names)
        for keyword in self.OWNER_KEYWORDS:
            # Pattern: "Owner: John Smith" or "John Smith, Owner"
            # Use word boundary and proper capitalization
            patterns = [
                rf'(?i)\b{keyword}\b[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                rf'([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)[,\s]+(?i)\b{keyword}\b',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html)
                for match in matches:
                    name = match.strip()
                    if self._is_valid_name(name):
                        contacts.append(ExtractedContact(
                            name=name,
                            title=keyword.title(),
                            source_page=source_page,
                            source_type="page_scrape",
                            confidence=0.7
                        ))

        # Look for LinkedIn URLs and extract names
        for match in self.LINKEDIN_REGEX.findall(html):
            linkedin_url = f"https://www.linkedin.com/in/{match}"
            # Try to find associated name
            contacts.append(ExtractedContact(
                linkedin_url=linkedin_url,
                source_page=source_page,
                source_type="page_scrape",
                confidence=0.6
            ))

        return contacts

    async def extract(self, domain: str) -> WebsiteExtractionResult:
        """
        Extract contacts from a domain.

        Args:
            domain: Company domain (e.g., "joesplumbing.com")

        Returns:
            WebsiteExtractionResult with all found contacts
        """
        result = WebsiteExtractionResult(domain=domain)

        # Ensure proper URL format
        base_url = f"https://{domain}" if not domain.startswith("http") else domain
        domain = urlparse(base_url).netloc.replace("www.", "")

        # Build URLs to scrape
        pages_to_try = [
            urljoin(base_url, f"/{page}")
            for page in self.CONTACT_PAGES[:self.max_pages]
        ]

        all_contacts = []
        all_emails = set()
        all_phones = set()

        # Scrape pages (with concurrency limit)
        semaphore = asyncio.Semaphore(self.concurrency)

        async def scrape_page(url: str):
            async with semaphore:
                return url, await self._fetch_url(url)

        page_results = await asyncio.gather(*[scrape_page(url) for url in pages_to_try])

        for url, html in page_results:
            if not html:
                result.errors.append(f"Failed to fetch: {url}")
                continue

            result.pages_scraped += 1

            # Extract Schema.org
            schemas = self._extract_schema_org(html)
            if schemas:
                result.has_schema_org = True
                schema_contacts = self._extract_contacts_from_schema(schemas, url)
                all_contacts.extend(schema_contacts)

                # Try to get company name from schema
                for schema in schemas:
                    if schema.get("@type") in ("Organization", "LocalBusiness", "Store"):
                        if schema.get("name") and not result.company_name:
                            result.company_name = schema["name"]

            # Extract emails
            emails = self._extract_emails(html, domain)
            all_emails.update(emails)

            # Extract phones
            phones = self._extract_phones(html)
            all_phones.update(phones)

            # Extract from page content
            page_contacts = self._extract_contacts_from_page(html, domain, url)
            all_contacts.extend(page_contacts)

        # Deduplicate contacts by name
        seen_names = set()
        unique_contacts = []
        for contact in sorted(all_contacts, key=lambda x: x.confidence, reverse=True):
            name_key = (contact.name or "").lower()
            if name_key and name_key not in seen_names:
                seen_names.add(name_key)
                unique_contacts.append(contact)
            elif not contact.name and contact.email:
                unique_contacts.append(contact)

        result.contacts = unique_contacts
        result.emails = list(all_emails)
        result.phones = list(all_phones)

        return result

    async def batch_extract(
        self,
        domains: list[str],
        concurrency: int = 10
    ) -> list[WebsiteExtractionResult]:
        """
        Extract contacts from multiple domains in parallel.

        Args:
            domains: List of domains
            concurrency: Max concurrent extractions

        Returns:
            List of results
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def extract_one(domain: str) -> WebsiteExtractionResult:
            async with semaphore:
                try:
                    return await self.extract(domain)
                except Exception as e:
                    logger.error(f"Failed to extract {domain}: {e}")
                    return WebsiteExtractionResult(
                        domain=domain,
                        errors=[str(e)]
                    )

        return await asyncio.gather(*[extract_one(d) for d in domains])


# Test
async def test_website_extractor():
    """Test the extractor"""
    extractor = WebsiteContactExtractor()

    try:
        result = await extractor.extract("joesplumbing.com")

        print(f"Domain: {result.domain}")
        print(f"Company name: {result.company_name}")
        print(f"Pages scraped: {result.pages_scraped}")
        print(f"Has Schema.org: {result.has_schema_org}")
        print(f"Emails found: {result.emails}")
        print(f"Phones found: {result.phones}")

        print(f"\nContacts found: {len(result.contacts)}")
        for contact in result.contacts[:5]:
            print(f"  - {contact.name} ({contact.title}) - {contact.email}")
            print(f"    Source: {contact.source_type}, Confidence: {contact.confidence}")

    finally:
        await extractor.close()


if __name__ == "__main__":
    asyncio.run(test_website_extractor())
