"""
OpenWeb Ninja Search - Real-Time Web Search API (Native Direct API).
Alternative search provider to Serper for redundancy and coverage.

API: https://api.openwebninja.com/realtime-web-search
Authentication: x-api-key header with ak_* format key
"""
import httpx
import asyncio
from typing import Dict, List


class OpenWebNinjaSearch:
    """Async search client using OpenWeb Ninja Real-Time Web Search API (Native)."""

    # Native API endpoint (search-light for fast lightweight searches)
    BASE_URL = "https://api.openwebninja.com/realtime-web-search/search-light"

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize OpenWeb Ninja search client.

        Args:
            api_key: Native OpenWeb Ninja API key (ak_* format)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout

    async def search(
        self,
        query: str,
        num_results: int = 10,
        region: str = "us-en"
    ) -> Dict:
        """
        Perform a web search using OpenWeb Ninja native API.

        Args:
            query: Search query string
            num_results: Number of results to return (max 50)
            region: Region-language code (e.g., "us-en", "uk-en")

        Returns:
            {
                "query": str,
                "organic": [
                    {
                        "title": str,
                        "link": str,
                        "snippet": str,
                        "position": int
                    }
                ],
                "success": bool,
                "error": str | None,
                "source": "openweb_ninja"
            }
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.BASE_URL,
                    headers={
                        "x-api-key": self.api_key
                    },
                    params={
                        "q": query,
                        "limit": min(num_results, 50)
                    }
                )

                if response.status_code == 401:
                    return {
                        "query": query,
                        "organic": [],
                        "success": False,
                        "error": "Invalid API key",
                        "source": "openweb_ninja"
                    }

                if response.status_code == 402:
                    return {
                        "query": query,
                        "organic": [],
                        "success": False,
                        "error": "Insufficient credits",
                        "source": "openweb_ninja"
                    }

                if response.status_code != 200:
                    return {
                        "query": query,
                        "organic": [],
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "source": "openweb_ninja"
                    }

                data = response.json()

                # Extract and normalize results to match Serper format
                organic = []
                results = data.get("data", [])

                for i, result in enumerate(results):
                    organic.append({
                        "title": result.get("title", ""),
                        "link": result.get("url", ""),
                        "snippet": result.get("snippet", ""),
                        "position": i + 1
                    })

                return {
                    "query": query,
                    "organic": organic,
                    "success": True,
                    "error": None,
                    "source": "openweb_ninja"
                }

        except httpx.TimeoutException:
            return {
                "query": query,
                "organic": [],
                "success": False,
                "error": "Search timeout",
                "source": "openweb_ninja"
            }
        except Exception as e:
            return {
                "query": query,
                "organic": [],
                "success": False,
                "error": str(e),
                "source": "openweb_ninja"
            }

    async def search_parallel(self, queries: List[str], num_results: int = 10) -> List[Dict]:
        """
        Perform multiple searches in parallel.

        Args:
            queries: List of search queries
            num_results: Number of results per query

        Returns:
            List of search results in same order as queries
        """
        tasks = [self.search(query, num_results) for query in queries]
        return await asyncio.gather(*tasks)


class RapidAPIOpenWebNinjaSearch:
    """OpenWeb Ninja search client via RapidAPI marketplace (fallback)."""

    BASE_URL = "https://real-time-web-search.p.rapidapi.com/search"

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout

    async def search(self, query: str, num_results: int = 10, region: str = "us-en") -> Dict:
        """Perform search via RapidAPI."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.BASE_URL,
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "real-time-web-search.p.rapidapi.com"
                    },
                    params={"q": query, "limit": min(num_results, 50)}
                )

                if response.status_code != 200:
                    return {
                        "query": query, "organic": [], "success": False,
                        "error": f"API error: {response.status_code}", "source": "openweb_ninja_rapidapi"
                    }

                data = response.json()
                organic = []
                for i, result in enumerate(data.get("data", [])):
                    organic.append({
                        "title": result.get("title", ""),
                        "link": result.get("url", ""),
                        "snippet": result.get("snippet", ""),
                        "position": i + 1
                    })

                return {"query": query, "organic": organic, "success": True, "error": None, "source": "openweb_ninja_rapidapi"}
        except Exception as e:
            return {"query": query, "organic": [], "success": False, "error": str(e), "source": "openweb_ninja_rapidapi"}


class DualProviderSearch:
    """
    Combined search using both Serper and OpenWeb Ninja in parallel.
    Merges results for better coverage and redundancy.
    """

    def __init__(self, serper_key: str, ninja_key: str, timeout: int = 30, use_native: bool = True):
        from .web_search import WebSearch
        self.serper = WebSearch(serper_key, timeout)
        # Use native OpenWeb Ninja API if use_native=True, otherwise use RapidAPI
        if use_native:
            self.ninja = OpenWebNinjaSearch(ninja_key, timeout)
        else:
            self.ninja = RapidAPIOpenWebNinjaSearch(ninja_key, timeout)

    async def search(self, query: str, num_results: int = 10) -> Dict:
        """
        Search using both providers and merge results.

        Returns combined results with source attribution.
        """
        serper_result, ninja_result = await asyncio.gather(
            self.serper.search(query, num_results),
            self.ninja.search(query, num_results)
        )

        # Merge organic results, preferring Serper (generally higher quality)
        seen_urls = set()
        merged_organic = []
        position = 1

        # Add Serper results first (higher priority)
        for r in serper_result.get("organic", []):
            url = r.get("link", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                merged_organic.append({
                    **r,
                    "position": position,
                    "source": "serper"
                })
                position += 1

        # Add OpenWeb Ninja results that aren't duplicates
        for r in ninja_result.get("organic", []):
            url = r.get("link", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                merged_organic.append({
                    **r,
                    "position": position,
                    "source": "openweb_ninja"
                })
                position += 1

        return {
            "query": query,
            "organic": merged_organic,
            "success": serper_result.get("success") or ninja_result.get("success"),
            "serper_success": serper_result.get("success"),
            "ninja_success": ninja_result.get("success"),
            "serper_error": serper_result.get("error"),
            "ninja_error": ninja_result.get("error"),
            "knowledgeGraph": serper_result.get("knowledgeGraph"),
            "answerBox": serper_result.get("answerBox")
        }

    async def search_parallel(self, queries: List[str], num_results: int = 10) -> List[Dict]:
        """Perform multiple dual-provider searches in parallel."""
        tasks = [self.search(query, num_results) for query in queries]
        return await asyncio.gather(*tasks)
