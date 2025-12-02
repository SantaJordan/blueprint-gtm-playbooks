"""
Serper OSINT Discovery

Uses Google Search to find executives at companies.
Much faster and more current than database providers.
"""

import os
import re
import logging
from dataclasses import dataclass, field
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class OsintResult:
    """Result from OSINT search"""
    name: str | None = None
    title: str | None = None
    linkedin_url: str | None = None
    source_url: str | None = None
    source_type: str | None = None  # "news", "linkedin", "company_site"
    snippet: str | None = None
    confidence: float = 0.0


@dataclass
class SerperSearchResult:
    """Aggregated results from Serper search"""
    candidates: list[OsintResult] = field(default_factory=list)
    best_match: OsintResult | None = None
    search_query: str = ""
    total_results: int = 0


class SerperOsint:
    """
    OSINT discovery using Serper (Google Search API).

    Cost: ~$0.001 per query
    Speed: ~500ms
    Recency: Immediate (finds news/changes within hours)
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"

    async def search(self, query: str, num_results: int = 10) -> dict:
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
                    text = await resp.text()
                    raise Exception(f"Serper API error {resp.status}: {text}")
                return await resp.json()

    def _extract_linkedin_url(self, text: str) -> str | None:
        """Extract LinkedIn URL from text"""
        patterns = [
            r'linkedin\.com/in/([a-zA-Z0-9\-]+)',
            r'linkedin\.com/company/([a-zA-Z0-9\-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and '/in/' in pattern:
                return f"https://www.linkedin.com/in/{match.group(1)}"
        return None

    def _extract_name_from_snippet(self, snippet: str, title_pattern: str) -> str | None:
        """Try to extract person name from search snippet"""
        # Common patterns like "John Smith, CEO of Company"
        patterns = [
            rf'([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?),?\s+(?:as\s+)?{title_pattern}',
            rf'{title_pattern}\s+([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)',
            rf'([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+(?:is|was|has been)\s+(?:appointed|named|promoted)',
        ]

        for pattern in patterns:
            match = re.search(pattern, snippet, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _score_result(self, result: OsintResult, target_title: str) -> float:
        """Score a result for relevance"""
        score = 0.0

        # Has name
        if result.name:
            score += 30

        # Has LinkedIn
        if result.linkedin_url:
            score += 25

        # Source type bonus
        if result.source_type == "news":
            score += 20  # News is most reliable for recency
        elif result.source_type == "linkedin":
            score += 15
        elif result.source_type == "company_site":
            score += 10

        # Title match
        if result.title and target_title.lower() in result.title.lower():
            score += 20

        return score

    async def find_executive(
        self,
        company_domain: str,
        target_title: str,
        company_name: str | None = None
    ) -> SerperSearchResult:
        """
        Find an executive at a company using OSINT.

        Args:
            company_domain: Company domain (e.g., "acme.com")
            target_title: Title to search for (e.g., "CEO", "VP Marketing")
            company_name: Optional company name for better search

        Returns:
            SerperSearchResult with candidates and best match
        """
        # Build search query
        company_ref = company_name or company_domain.split('.')[0]

        # Search with current year to prioritize recent results
        query = f'{company_ref} {target_title} 2025'

        result = SerperSearchResult(search_query=query)

        try:
            search_data = await self.search(query, num_results=10)
            organic = search_data.get("organic", [])
            result.total_results = len(organic)

            for item in organic:
                url = item.get("link", "")
                title = item.get("title", "")
                snippet = item.get("snippet", "")

                candidate = OsintResult(
                    source_url=url,
                    snippet=snippet
                )

                # Determine source type
                if "linkedin.com" in url:
                    candidate.source_type = "linkedin"
                    candidate.linkedin_url = self._extract_linkedin_url(url)
                    # Extract name from LinkedIn title
                    if " - " in title:
                        candidate.name = title.split(" - ")[0].strip()
                        candidate.title = title.split(" - ")[1].split("|")[0].strip() if "|" in title else None
                elif any(x in url.lower() for x in ["businesswire", "prnewswire", "globenewswire", "reuters", "bloomberg"]):
                    candidate.source_type = "news"
                    candidate.name = self._extract_name_from_snippet(snippet, target_title)
                    candidate.title = target_title
                elif company_domain in url:
                    candidate.source_type = "company_site"
                    candidate.name = self._extract_name_from_snippet(snippet, target_title)

                # Look for LinkedIn URL in snippet
                if not candidate.linkedin_url:
                    candidate.linkedin_url = self._extract_linkedin_url(snippet)

                # Score the result
                candidate.confidence = self._score_result(candidate, target_title)

                if candidate.name or candidate.linkedin_url:
                    result.candidates.append(candidate)

            # Sort by confidence and pick best
            result.candidates.sort(key=lambda x: x.confidence, reverse=True)
            if result.candidates:
                result.best_match = result.candidates[0]

        except Exception as e:
            logger.error(f"Serper search failed: {e}")

        return result

    async def find_person_linkedin(
        self,
        name: str,
        company: str,
    ) -> OsintResult:
        """
        Search for a person's LinkedIn profile URL given name + company.
        Uses Google search: "{name}" "{company}" site:linkedin.com/in

        Args:
            name: Person's full name
            company: Company name they work at

        Returns:
            OsintResult with linkedin_url if found
        """
        # Try exact match first
        query = f'"{name}" "{company}" site:linkedin.com/in'
        result = OsintResult(confidence=0.0)

        try:
            search_data = await self.search(query, num_results=5)
            organic = search_data.get("organic", [])

            for item in organic:
                url = item.get("link", "")
                title = item.get("title", "")
                snippet = item.get("snippet", "")

                # Must be a LinkedIn profile URL
                if "linkedin.com/in/" not in url:
                    continue

                # Extract LinkedIn URL
                linkedin_url = self._extract_linkedin_url(url)
                if not linkedin_url:
                    continue

                # Check if name is in title (LinkedIn titles are "Name - Title | Company")
                name_parts = name.lower().split()
                title_lower = title.lower()

                # At least first and last name should be in title
                name_matches = sum(1 for part in name_parts if part in title_lower)
                if name_matches >= 2 or (len(name_parts) == 1 and name_parts[0] in title_lower):
                    # Extract name and title from LinkedIn result
                    if " - " in title:
                        result.name = title.split(" - ")[0].strip()
                        title_part = title.split(" - ")[1] if len(title.split(" - ")) > 1 else ""
                        result.title = title_part.split("|")[0].strip() if "|" in title_part else title_part.strip()

                    result.linkedin_url = linkedin_url
                    result.source_url = url
                    result.source_type = "linkedin"
                    result.snippet = snippet

                    # Score based on match quality
                    if name_matches >= len(name_parts):
                        result.confidence = 0.9  # Full name match
                    else:
                        result.confidence = 0.7  # Partial match

                    return result

            # If no exact match, try without quotes for broader search
            if not result.linkedin_url:
                query = f'{name} {company} site:linkedin.com/in'
                search_data = await self.search(query, num_results=5)
                organic = search_data.get("organic", [])

                for item in organic:
                    url = item.get("link", "")
                    title = item.get("title", "")

                    if "linkedin.com/in/" not in url:
                        continue

                    linkedin_url = self._extract_linkedin_url(url)
                    if linkedin_url:
                        if " - " in title:
                            result.name = title.split(" - ")[0].strip()
                        result.linkedin_url = linkedin_url
                        result.source_url = url
                        result.source_type = "linkedin"
                        result.confidence = 0.5  # Lower confidence for broad search
                        return result

        except Exception as e:
            logger.error(f"LinkedIn search failed: {e}")

        return result

    async def validate_person_at_company(
        self,
        person_name: str,
        company_domain: str,
        expected_title: str | None = None
    ) -> tuple[bool, str | None, float]:
        """
        Validate that a person works at a company.

        Returns:
            Tuple of (is_valid, actual_title, confidence)
        """
        query = f'"{person_name}" site:{company_domain}'

        try:
            search_data = await self.search(query, num_results=5)
            organic = search_data.get("organic", [])

            if not organic:
                # Try without site restriction
                query = f'"{person_name}" {company_domain}'
                search_data = await self.search(query, num_results=5)
                organic = search_data.get("organic", [])

            for item in organic:
                snippet = item.get("snippet", "")
                title = item.get("title", "")

                # Person mentioned in results
                if person_name.lower() in (snippet + title).lower():
                    # Try to extract title
                    title_match = None
                    if expected_title:
                        if expected_title.lower() in snippet.lower():
                            title_match = expected_title
                            return True, title_match, 0.85

                    return True, title_match, 0.6

            return False, None, 0.0

        except Exception as e:
            logger.error(f"Validation search failed: {e}")
            return False, None, 0.0


# Test function
async def test_serper_osint():
    """Test OSINT discovery"""
    osint = SerperOsint()

    # Test finding Kohl's CEO (recent change)
    print("Testing: Find CEO of Kohl's")
    result = await osint.find_executive(
        company_domain="kohls.com",
        target_title="CEO",
        company_name="Kohl's"
    )

    print(f"Query: {result.search_query}")
    print(f"Total results: {result.total_results}")
    print(f"Candidates found: {len(result.candidates)}")

    if result.best_match:
        print(f"\nBest match:")
        print(f"  Name: {result.best_match.name}")
        print(f"  Title: {result.best_match.title}")
        print(f"  LinkedIn: {result.best_match.linkedin_url}")
        print(f"  Source: {result.best_match.source_type}")
        print(f"  Confidence: {result.best_match.confidence}")

    return result


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_serper_osint())
