"""
RapidAPI LinkedIn Data Scraper Client
https://rapidapi.com/freshdata-freshdata-default/api/linkedin-data-scraper

Endpoints:
- POST /person - Get person details from LinkedIn URL

Rate Limit: 1 concurrent request, use semaphore and delays.
"""

import aiohttp
import asyncio
import re
from dataclasses import dataclass


@dataclass
class RapidAPIPersonResult:
    """Result from profile endpoint"""
    name: str | None
    first_name: str | None
    last_name: str | None
    title: str | None
    company: str | None
    linkedin_url: str | None
    location: str | None
    status: str
    latency_ms: int = 0
    raw_response: dict = None

    def __post_init__(self):
        if self.raw_response is None:
            self.raw_response = {}


@dataclass
class RapidAPIEmailLookupResult:
    """Result from email lookup (not supported by this API)"""
    linkedin_url: str | None
    name: str | None
    status: str
    latency_ms: int = 0
    raw_response: dict = None

    def __post_init__(self):
        if self.raw_response is None:
            self.raw_response = {}


class RapidAPILinkedInClient:
    """
    RapidAPI Fresh LinkedIn Scraper client.

    Usage:
        client = RapidAPILinkedInClient(api_key="xxx")

        # Get person details
        result = await client.get_person("https://www.linkedin.com/in/johndoe")
        print(result.name, result.title, result.company)

        await client.close()
    """

    BASE_URL = "https://realtime-linkedin-fresh-data.p.rapidapi.com"
    HOST = "realtime-linkedin-fresh-data.p.rapidapi.com"

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None
        # Rate limit: 1 concurrent request, 1 request per second
        self._semaphore = asyncio.Semaphore(1)
        self._last_request_time = 0
        self._min_delay = 1.5  # 1.5s between requests (rate limit is 1/sec)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "X-RapidAPI-Key": self.api_key,
                    "X-RapidAPI-Host": self.HOST,
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _rate_limit(self):
        """Enforce rate limiting"""
        import time
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_delay:
            await asyncio.sleep(self._min_delay - elapsed)
        self._last_request_time = time.time()

    async def _post(self, endpoint: str, json_body: dict) -> tuple[dict, int]:
        """
        Make a POST request to RapidAPI.
        Returns (response_dict, status_code)
        """
        async with self._semaphore:
            await self._rate_limit()

            session = await self._get_session()
            url = f"{self.BASE_URL}{endpoint}"

            import time
            start = time.time()

            try:
                async with session.post(url, json=json_body) as response:
                    latency = int((time.time() - start) * 1000)

                    if response.status == 429:
                        # Rate limited - back off
                        self._min_delay = min(self._min_delay * 2, 10.0)
                        return {"error": "rate_limited"}, response.status

                    if response.status == 401:
                        return {"error": "invalid_api_key"}, response.status

                    if response.status == 402:
                        return {"error": "insufficient_credits"}, response.status

                    try:
                        result = await response.json()
                    except:
                        result = {"error": "invalid_json", "text": await response.text()}

                    result["_latency_ms"] = latency
                    return result, response.status

            except asyncio.TimeoutError:
                return {"error": "timeout"}, 0
            except Exception as e:
                return {"error": str(e)}, 0

    def _extract_username(self, linkedin_url: str) -> str | None:
        """Extract username from LinkedIn URL."""
        # Handle various URL formats:
        # https://www.linkedin.com/in/johndoe
        # https://linkedin.com/in/johndoe/
        # linkedin.com/in/johndoe
        # johndoe (just username)

        linkedin_url = linkedin_url.strip()

        # If it's just a username (no slashes or dots)
        if '/' not in linkedin_url and '.' not in linkedin_url:
            return linkedin_url

        # Extract from URL
        match = re.search(r'linkedin\.com/in/([^/?]+)', linkedin_url)
        if match:
            return match.group(1).rstrip('/')

        return None

    async def get_person(self, linkedin_url: str) -> RapidAPIPersonResult:
        """
        Get person details from LinkedIn URL.

        Args:
            linkedin_url: Full LinkedIn profile URL
                          (e.g., https://www.linkedin.com/in/johndoe)

        Returns:
            RapidAPIPersonResult with name, title, company, etc.
        """
        # Normalize URL - ensure it has protocol
        linkedin_url = linkedin_url.strip()
        if not linkedin_url.startswith("http"):
            # Check if it's just a username or partial URL
            if "linkedin.com" not in linkedin_url:
                linkedin_url = f"https://www.linkedin.com/in/{linkedin_url}"
            else:
                linkedin_url = f"https://{linkedin_url}"

        # Use POST /person with {"link": url}
        result, status = await self._post("/person", {"link": linkedin_url})

        latency = result.pop("_latency_ms", 0)

        if "error" in result:
            return RapidAPIPersonResult(
                name=None,
                first_name=None,
                last_name=None,
                title=None,
                company=None,
                linkedin_url=linkedin_url,
                location=None,
                status=f"error: {result['error']}",
                latency_ms=latency,
                raw_response=result
            )

        # Check for subscription error
        if result.get("message", "").startswith("You are not subscribed"):
            return RapidAPIPersonResult(
                name=None,
                first_name=None,
                last_name=None,
                title=None,
                company=None,
                linkedin_url=linkedin_url,
                location=None,
                status="error: not_subscribed - Subscribe to the API plan on RapidAPI first",
                latency_ms=latency,
                raw_response=result
            )

        # Parse response - field names may vary, try common patterns
        # The API might return data nested under "data" or at top level
        data = result.get("data", result)

        # Extract name - try various field patterns
        full_name = (
            data.get("full_name") or
            data.get("fullName") or
            data.get("name") or
            f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or
            None
        )

        first_name = data.get("first_name") or data.get("firstName")
        last_name = data.get("last_name") or data.get("lastName")

        # Extract title/headline
        title = (
            data.get("headline") or
            data.get("job_title") or
            data.get("title") or
            data.get("occupation") or
            None
        )

        # Extract company from experiences (first/current position)
        company = None
        experiences = data.get("experiences", [])
        if experiences and isinstance(experiences, list) and len(experiences) > 0:
            # Company is in 'subtitle' field for this API
            company = (
                experiences[0].get("subtitle") or
                experiences[0].get("company") or
                experiences[0].get("company_name") or
                None
            )

        return RapidAPIPersonResult(
            name=full_name,
            first_name=first_name,
            last_name=last_name,
            title=title,
            company=company,
            linkedin_url=data.get("linkedin_url") or linkedin_url,
            location=data.get("location") or data.get("city"),
            status="success" if full_name else "no_data",
            latency_ms=latency,
            raw_response=result
        )

    async def email_to_linkedin(self, email: str) -> RapidAPIEmailLookupResult:
        """
        Find LinkedIn profile from email address.
        NOTE: This endpoint is not supported by Fresh LinkedIn Scraper API.

        Args:
            email: Email address to look up

        Returns:
            RapidAPIEmailLookupResult with error status
        """
        return RapidAPIEmailLookupResult(
            linkedin_url=None,
            name=None,
            status="error: email lookup not supported by this API",
            latency_ms=0,
            raw_response={}
        )


# Convenience function for testing
async def test_rapidapi_linkedin(api_key: str, test_url: str = None):
    """Test RapidAPI LinkedIn connection"""
    client = RapidAPILinkedInClient(api_key)
    try:
        # Test with a known LinkedIn URL
        test_url = test_url or "https://www.linkedin.com/in/williamhgates"
        print(f"Testing RapidAPI LinkedIn with: {test_url}")

        result = await client.get_person(test_url)

        if result.name:
            print(f"Success! Found: {result.name}")
            print(f"  Title: {result.title}")
            print(f"  Company: {result.company}")
            print(f"  Latency: {result.latency_ms}ms")
            return True
        else:
            print(f"No data returned. Status: {result.status}")
            return False

    except Exception as e:
        print(f"RapidAPI LinkedIn error: {e}")
        return False
    finally:
        await client.close()


if __name__ == "__main__":
    import os
    import asyncio

    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        print("Set RAPIDAPI_KEY environment variable")
    else:
        asyncio.run(test_rapidapi_linkedin(api_key))
