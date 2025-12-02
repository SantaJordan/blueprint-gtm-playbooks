"""
Multi-Source LinkedIn Profile Enricher

Fetches profile data from MULTIPLE sources in parallel:
- RapidAPI LinkedIn Fresh Data
- Scrapin LinkedIn API

Aggregates results for comparison and LLM verification.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

# Import our enrichment clients
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from evaluation.harness.rapidapi_linkedin import RapidAPILinkedInClient, RapidAPIPersonResult

# Import scrapin from contact-finder (hyphen in directory name)
import importlib.util
_scrapin_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "contact-finder", "modules", "enrichment", "scrapin.py"
)
_spec = importlib.util.spec_from_file_location("scrapin", _scrapin_path)
_scrapin_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_scrapin_module)
ScrapinClient = _scrapin_module.ScrapinClient
ScrapinPersonProfile = _scrapin_module.ScrapinPersonProfile


@dataclass
class SourceResult:
    """Result from a single enrichment source"""
    source: str
    success: bool
    name: str | None
    title: str | None
    company: str | None
    experience: list[dict] = field(default_factory=list)
    latency_ms: int = 0
    error: str | None = None
    raw_response: dict = field(default_factory=dict)


@dataclass
class EnrichedProfile:
    """Aggregated profile data from multiple sources"""
    linkedin_url: str

    # Per-source results
    rapidapi: SourceResult | None = None
    scrapin: SourceResult | None = None

    # Unified/best fields (picked from sources)
    best_name: str | None = None
    best_title: str | None = None
    best_company: str | None = None
    all_experience: list[dict] = field(default_factory=list)

    # Metadata
    sources_attempted: int = 0
    sources_succeeded: int = 0
    total_latency_ms: int = 0

    def get_sources_summary(self) -> dict:
        """Get summary of which sources had data"""
        return {
            "rapidapi": self.rapidapi.success if self.rapidapi else False,
            "scrapin": self.scrapin.success if self.scrapin else False,
        }

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization"""
        return {
            "linkedin_url": self.linkedin_url,
            "best_name": self.best_name,
            "best_title": self.best_title,
            "best_company": self.best_company,
            "sources": self.get_sources_summary(),
            "sources_succeeded": self.sources_succeeded,
            "total_latency_ms": self.total_latency_ms,
            "rapidapi_data": self.rapidapi.raw_response if self.rapidapi else None,
            "scrapin_data": self.scrapin.raw_response if self.scrapin else None,
        }


class MultiSourceEnricher:
    """
    Fetch LinkedIn profile data from ALL available sources in parallel.

    Usage:
        enricher = MultiSourceEnricher(
            rapidapi_key="xxx",
            scrapin_key="yyy"
        )

        profile = await enricher.enrich("https://linkedin.com/in/johndoe")
        print(profile.best_name, profile.best_title)
        print(profile.get_sources_summary())

        await enricher.close()
    """

    def __init__(
        self,
        rapidapi_key: str | None = None,
        scrapin_key: str | None = None,
        timeout: int = 30
    ):
        self.rapidapi = RapidAPILinkedInClient(rapidapi_key, timeout) if rapidapi_key else None
        self.scrapin = ScrapinClient(scrapin_key, timeout) if scrapin_key else None
        self.timeout = timeout

    async def close(self):
        """Close all client connections"""
        if self.rapidapi:
            await self.rapidapi.close()
        if self.scrapin:
            await self.scrapin.close()

    async def _fetch_rapidapi(self, linkedin_url: str) -> SourceResult:
        """Fetch from RapidAPI LinkedIn"""
        if not self.rapidapi:
            return SourceResult(
                source="rapidapi",
                success=False,
                name=None,
                title=None,
                company=None,
                error="No API key configured"
            )

        start = time.time()
        try:
            result: RapidAPIPersonResult = await self.rapidapi.get_person(linkedin_url)
            latency = int((time.time() - start) * 1000)

            # Extract experience from raw response
            experience = []
            raw = result.raw_response or {}
            data = raw.get("data", raw)
            if "experiences" in data:
                experience = data.get("experiences", [])
            elif "positions" in data:
                experience = data.get("positions", [])

            return SourceResult(
                source="rapidapi",
                success=result.status == "success" and result.name is not None,
                name=result.name,
                title=result.title,
                company=result.company,
                experience=experience,
                latency_ms=latency,
                error=None if result.status == "success" else result.status,
                raw_response=result.raw_response or {}
            )

        except Exception as e:
            latency = int((time.time() - start) * 1000)
            return SourceResult(
                source="rapidapi",
                success=False,
                name=None,
                title=None,
                company=None,
                latency_ms=latency,
                error=str(e)
            )

    async def _fetch_scrapin(self, linkedin_url: str) -> SourceResult:
        """Fetch from Scrapin API"""
        if not self.scrapin:
            return SourceResult(
                source="scrapin",
                success=False,
                name=None,
                title=None,
                company=None,
                error="No API key configured"
            )

        start = time.time()
        try:
            result: ScrapinPersonProfile = await self.scrapin.get_person_profile(linkedin_url)
            latency = int((time.time() - start) * 1000)

            # Check for error in response
            raw = result.raw_response or {}
            if "error" in raw:
                return SourceResult(
                    source="scrapin",
                    success=False,
                    name=None,
                    title=None,
                    company=None,
                    latency_ms=latency,
                    error=raw.get("error"),
                    raw_response=raw
                )

            return SourceResult(
                source="scrapin",
                success=result.full_name is not None,
                name=result.full_name,
                title=result.title,
                company=result.company,
                experience=result.experience or [],
                latency_ms=latency,
                error=None,
                raw_response=raw
            )

        except Exception as e:
            latency = int((time.time() - start) * 1000)
            return SourceResult(
                source="scrapin",
                success=False,
                name=None,
                title=None,
                company=None,
                latency_ms=latency,
                error=str(e)
            )

    async def enrich(self, linkedin_url: str) -> EnrichedProfile:
        """
        Fetch profile from ALL sources in parallel.

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            EnrichedProfile with data from all sources
        """
        # Normalize URL
        linkedin_url = linkedin_url.strip()
        if not linkedin_url.startswith("http"):
            linkedin_url = f"https://www.linkedin.com/in/{linkedin_url}"

        # Fetch from all sources in parallel
        tasks = []
        source_names = []

        if self.rapidapi:
            tasks.append(self._fetch_rapidapi(linkedin_url))
            source_names.append("rapidapi")

        if self.scrapin:
            tasks.append(self._fetch_scrapin(linkedin_url))
            source_names.append("scrapin")

        # Execute all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        rapidapi_result = None
        scrapin_result = None

        for i, result in enumerate(results):
            source = source_names[i]

            if isinstance(result, Exception):
                # Convert exception to SourceResult
                result = SourceResult(
                    source=source,
                    success=False,
                    name=None,
                    title=None,
                    company=None,
                    error=str(result)
                )

            if source == "rapidapi":
                rapidapi_result = result
            elif source == "scrapin":
                scrapin_result = result

        # Aggregate results
        profile = EnrichedProfile(
            linkedin_url=linkedin_url,
            rapidapi=rapidapi_result,
            scrapin=scrapin_result,
            sources_attempted=len(tasks)
        )

        # Count successes and total latency
        for result in [rapidapi_result, scrapin_result]:
            if result:
                profile.total_latency_ms += result.latency_ms
                if result.success:
                    profile.sources_succeeded += 1

        # Pick best values (prefer first successful source)
        for result in [scrapin_result, rapidapi_result]:  # Scrapin priority - more reliable
            if result and result.success:
                if not profile.best_name and result.name:
                    profile.best_name = result.name
                if not profile.best_title and result.title:
                    profile.best_title = result.title
                if not profile.best_company and result.company:
                    profile.best_company = result.company
                if result.experience:
                    profile.all_experience.extend(result.experience)

        return profile

    async def enrich_batch(
        self,
        linkedin_urls: list[str],
        concurrency: int = 5,
        delay_between: float = 0.5
    ) -> list[EnrichedProfile]:
        """
        Enrich multiple profiles with rate limiting.

        Args:
            linkedin_urls: List of LinkedIn URLs
            concurrency: Max concurrent enrichments
            delay_between: Delay between batches (seconds)

        Returns:
            List of EnrichedProfile results
        """
        semaphore = asyncio.Semaphore(concurrency)
        results = []

        async def enrich_with_limit(url: str) -> EnrichedProfile:
            async with semaphore:
                result = await self.enrich(url)
                await asyncio.sleep(delay_between)
                return result

        tasks = [enrich_with_limit(url) for url in linkedin_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to empty profiles
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(EnrichedProfile(
                    linkedin_url=linkedin_urls[i],
                    sources_attempted=2,
                    sources_succeeded=0
                ))
            else:
                final_results.append(result)

        return final_results


# Test function
async def test_multi_source_enricher():
    """Test the multi-source enricher"""
    import os

    rapidapi_key = os.environ.get("RAPIDAPI_KEY")
    scrapin_key = os.environ.get("SCRAPIN_API_KEY")

    if not rapidapi_key and not scrapin_key:
        print("Set RAPIDAPI_KEY and/or SCRAPIN_API_KEY environment variables")
        return

    enricher = MultiSourceEnricher(
        rapidapi_key=rapidapi_key,
        scrapin_key=scrapin_key
    )

    try:
        # Test with a known profile
        test_url = "https://www.linkedin.com/in/williamhgates"
        print(f"Testing multi-source enrichment for: {test_url}\n")

        profile = await enricher.enrich(test_url)

        print(f"Best Name: {profile.best_name}")
        print(f"Best Title: {profile.best_title}")
        print(f"Best Company: {profile.best_company}")
        print(f"\nSources: {profile.get_sources_summary()}")
        print(f"Succeeded: {profile.sources_succeeded}/{profile.sources_attempted}")
        print(f"Total Latency: {profile.total_latency_ms}ms")

        # Show per-source details
        if profile.rapidapi:
            print(f"\nRapidAPI: {'Success' if profile.rapidapi.success else 'Failed'}")
            if profile.rapidapi.error:
                print(f"  Error: {profile.rapidapi.error}")
            else:
                print(f"  Name: {profile.rapidapi.name}")
                print(f"  Title: {profile.rapidapi.title}")

        if profile.scrapin:
            print(f"\nScrapin: {'Success' if profile.scrapin.success else 'Failed'}")
            if profile.scrapin.error:
                print(f"  Error: {profile.scrapin.error}")
            else:
                print(f"  Name: {profile.scrapin.name}")
                print(f"  Title: {profile.scrapin.title}")

    finally:
        await enricher.close()


if __name__ == "__main__":
    asyncio.run(test_multi_source_enricher())
