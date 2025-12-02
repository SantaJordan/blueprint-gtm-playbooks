"""
Serper Data Filler - Fill missing company data using cheap Serper queries

Cost: $0.001 per query - use liberally!
"""

import asyncio
import os
import re
import logging
from dataclasses import dataclass, field
from typing import Any
import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class FillResult:
    """Result of filling missing company data"""
    original: dict
    filled: dict
    queries_run: int
    fields_filled: list[str]
    cost: float  # $0.001 per query


class SerperDataFiller:
    """
    Use cheap Serper queries ($0.001 each) to fill missing company data.

    Can fill: domain, address, phone, owner name
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"
        self.cost_per_query = 0.001

    async def search(self, query: str, num_results: int = 5) -> dict:
        """Execute a Serper search"""
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not set")

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "q": query,
            "num": num_results
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    return {}
                return await resp.json()

    def _extract_domain(self, search_results: dict, company_name: str) -> str | None:
        """Extract company domain from search results"""
        organic = search_results.get("organic", [])
        company_lower = company_name.lower()

        for result in organic:
            url = result.get("link", "")
            title = result.get("title", "").lower()

            # Skip social media and directories
            if any(x in url for x in ["facebook.com", "linkedin.com", "yelp.com", "yellowpages", "bbb.org"]):
                continue

            # Check if result seems related to company
            if company_lower.split()[0] in title or company_lower.split()[0] in url.lower():
                # Extract domain
                domain = re.search(r'https?://(?:www\.)?([^/]+)', url)
                if domain:
                    return domain.group(1)

        # Check knowledge graph
        kg = search_results.get("knowledgeGraph", {})
        if kg.get("website"):
            domain = re.search(r'https?://(?:www\.)?([^/]+)', kg["website"])
            if domain:
                return domain.group(1)

        return None

    def _extract_address(self, search_results: dict) -> dict | None:
        """Extract address from knowledge graph or search results"""
        kg = search_results.get("knowledgeGraph", {})

        if kg.get("address"):
            addr = kg["address"]
            # Try to parse city, state from address
            parts = addr.split(",")
            if len(parts) >= 2:
                return {
                    "address": addr,
                    "city": parts[-2].strip() if len(parts) >= 2 else None,
                    "state": parts[-1].strip()[:2] if len(parts) >= 1 else None
                }
            return {"address": addr}

        return None

    def _extract_phone(self, search_results: dict) -> str | None:
        """Extract phone from knowledge graph"""
        kg = search_results.get("knowledgeGraph", {})
        return kg.get("phone") or kg.get("telephone")

    # Common words that should NOT be names (includes business terms)
    INVALID_NAME_WORDS = {
        # Common words
        "the", "and", "or", "of", "is", "in", "on", "at", "to", "for", "with",
        "our", "we", "us", "you", "your", "this", "that", "which", "who",
        "also", "got", "get", "has", "have", "had", "was", "were", "are",
        "its", "their", "his", "her", "from", "into", "but", "not", "can",
        "will", "may", "about", "more", "just", "some", "any", "all", "new",
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

        for part in parts:
            # Each part must be 2+ chars
            if len(part) < 2:
                return False
            # Must start with capital
            if not part[0].isupper():
                return False
            # Check against invalid words
            if part.lower() in self.INVALID_NAME_WORDS:
                return False

        return True

    def _extract_owner_from_results(self, search_results: dict, company_name: str) -> dict | None:
        """Try to extract owner name from search results"""
        organic = search_results.get("organic", [])

        # Case-sensitive patterns for proper names
        owner_patterns = [
            r'(?i)(?:owner|founder|president|ceo)[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)[,\s]+(?i)(?:owner|founder|president)',
            r'(?i)(?:owned by|founded by)[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]

        for result in organic:
            snippet = result.get("snippet", "")
            title = result.get("title", "")
            text = f"{title} {snippet}"

            for pattern in owner_patterns:
                match = re.search(pattern, text)
                if match:
                    name = match.group(1).strip()
                    if self._is_valid_name(name):
                        return {"owner": name, "owner_title": "Owner"}

        return None

    async def fill_missing(
        self,
        company: dict,
        missing_fields: list[str]
    ) -> FillResult:
        """
        Fill missing company data using Serper queries.

        Args:
            company: Company dict with at least company_name
            missing_fields: List of fields to try to fill (domain, address, phone, owner)

        Returns:
            FillResult with filled data
        """
        filled = dict(company)
        queries_run = 0
        fields_filled = []

        company_name = company.get("company_name", "")
        city = company.get("city", "")
        state = company.get("state", "")
        location = f"{city} {state}".strip()

        if not company_name:
            return FillResult(
                original=company,
                filled=filled,
                queries_run=0,
                fields_filled=[],
                cost=0.0
            )

        # Build queries based on what's missing
        queries = []

        if "domain" in missing_fields and not company.get("domain"):
            query = f'"{company_name}"'
            if location:
                query += f" {location}"
            query += " official website"
            queries.append(("domain", query))

        if "address" in missing_fields and not company.get("address"):
            query = f'"{company_name}"'
            if location:
                query += f" {location}"
            query += " address"
            queries.append(("address", query))

        if "phone" in missing_fields and not company.get("phone"):
            query = f'"{company_name}"'
            if location:
                query += f" {location}"
            query += " phone number"
            queries.append(("phone", query))

        if "owner" in missing_fields and not company.get("owner"):
            query = f'"{company_name}"'
            if location:
                query += f" {location}"
            query += " owner founder"
            queries.append(("owner", query))

        # Run queries in parallel (they're cheap!)
        async def run_query(field_type: str, query: str):
            try:
                return field_type, await self.search(query)
            except Exception as e:
                logger.warning(f"Query failed for {field_type}: {e}")
                return field_type, {}

        results = await asyncio.gather(*[run_query(ft, q) for ft, q in queries])
        queries_run = len(results)

        for field_type, search_results in results:
            if not search_results:
                continue

            if field_type == "domain":
                domain = self._extract_domain(search_results, company_name)
                if domain and not filled.get("domain"):
                    filled["domain"] = domain
                    fields_filled.append("domain")

            elif field_type == "address":
                addr_data = self._extract_address(search_results)
                if addr_data:
                    if addr_data.get("address") and not filled.get("address"):
                        filled["address"] = addr_data["address"]
                        fields_filled.append("address")
                    if addr_data.get("city") and not filled.get("city"):
                        filled["city"] = addr_data["city"]
                    if addr_data.get("state") and not filled.get("state"):
                        filled["state"] = addr_data["state"]

            elif field_type == "phone":
                phone = self._extract_phone(search_results)
                if phone and not filled.get("phone"):
                    filled["phone"] = phone
                    fields_filled.append("phone")

            elif field_type == "owner":
                owner_data = self._extract_owner_from_results(search_results, company_name)
                if owner_data:
                    if owner_data.get("owner") and not filled.get("owner"):
                        filled["owner"] = owner_data["owner"]
                        fields_filled.append("owner")
                    if owner_data.get("owner_title") and not filled.get("owner_title"):
                        filled["owner_title"] = owner_data["owner_title"]

        return FillResult(
            original=company,
            filled=filled,
            queries_run=queries_run,
            fields_filled=fields_filled,
            cost=queries_run * self.cost_per_query
        )

    async def batch_fill(
        self,
        companies: list[dict],
        missing_fields: list[str],
        concurrency: int = 10
    ) -> list[FillResult]:
        """
        Fill missing data for multiple companies.

        Args:
            companies: List of company dicts
            missing_fields: Fields to try to fill
            concurrency: Max concurrent companies to process

        Returns:
            List of FillResults
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def fill_one(company: dict) -> FillResult:
            async with semaphore:
                return await self.fill_missing(company, missing_fields)

        return await asyncio.gather(*[fill_one(c) for c in companies])


# Test
async def test_serper_filler():
    """Test the data filler"""
    filler = SerperDataFiller()

    company = {
        "company_name": "Joe's Plumbing",
        "city": "Phoenix",
        "state": "AZ"
    }

    result = await filler.fill_missing(company, ["domain", "phone", "owner"])

    print(f"Original: {result.original}")
    print(f"Filled: {result.filled}")
    print(f"Queries run: {result.queries_run}")
    print(f"Fields filled: {result.fields_filled}")
    print(f"Cost: ${result.cost:.4f}")


if __name__ == "__main__":
    asyncio.run(test_serper_filler())
