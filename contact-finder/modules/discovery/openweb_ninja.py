"""
OpenWeb Ninja API Client
https://rapidapi.com/letscrape-6bRBa3QguO5/

APIs (all $0.002/query via RapidAPI):
- Local Business Data - Google Maps search for businesses
- Website Contacts Scraper - Extract emails, phones, social links from domain
- Social Links Search - Find LinkedIn/social profiles for a person
"""

import aiohttp
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class LocalBusinessResult:
    """Result from Local Business Data API (Google Maps)"""
    place_id: str | None
    name: str | None
    owner_name: str | None
    phone: str | None
    email: str | None
    website: str | None
    address: str | None
    city: str | None
    state: str | None
    rating: float | None
    reviews_count: int | None
    category: str | None
    social_links: dict = field(default_factory=dict)
    raw_response: dict = field(default_factory=dict)
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None and self.name is not None


@dataclass
class OpenWebContactResult:
    """Result from Website Contacts Scraper API"""
    domain: str
    emails: list[dict] = field(default_factory=list)  # [{value, sources}]
    phone_numbers: list[dict] = field(default_factory=list)
    linkedin: str | None = None
    facebook: str | None = None
    twitter: str | None = None
    instagram: str | None = None
    youtube: str | None = None
    tiktok: str | None = None
    github: str | None = None
    pinterest: str | None = None
    snapchat: str | None = None
    raw_response: dict = field(default_factory=dict)
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None and (len(self.emails) > 0 or self.linkedin is not None)

    @property
    def primary_email(self) -> str | None:
        if self.emails:
            return self.emails[0].get("value")
        return None

    @property
    def primary_phone(self) -> str | None:
        if self.phone_numbers:
            return self.phone_numbers[0].get("value")
        return None


@dataclass
class SocialLinksResult:
    """Result from Social Links Search API"""
    query: str
    linkedin_urls: list[str] = field(default_factory=list)
    facebook_urls: list[str] = field(default_factory=list)
    twitter_urls: list[str] = field(default_factory=list)
    instagram_urls: list[str] = field(default_factory=list)
    github_urls: list[str] = field(default_factory=list)
    youtube_urls: list[str] = field(default_factory=list)
    raw_response: dict = field(default_factory=dict)
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None and len(self.linkedin_urls) > 0

    @property
    def primary_linkedin(self) -> str | None:
        if self.linkedin_urls:
            return self.linkedin_urls[0]
        return None


class OpenWebNinjaClient:
    """OpenWeb Ninja API client for SMB contact discovery"""

    # RapidAPI hosts for each API
    LOCAL_BUSINESS_HOST = "local-business-data.p.rapidapi.com"
    WEBSITE_CONTACTS_HOST = "website-contacts-scraper.p.rapidapi.com"
    SOCIAL_LINKS_HOST = "social-links-search.p.rapidapi.com"

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self._sessions: dict[str, aiohttp.ClientSession] = {}

    async def _get_session(self, host: str) -> aiohttp.ClientSession:
        """Get or create session for specific API host"""
        if host not in self._sessions or self._sessions[host].closed:
            self._sessions[host] = aiohttp.ClientSession(
                headers={
                    "X-RapidAPI-Key": self.api_key,
                    "X-RapidAPI-Host": host,
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._sessions[host]

    async def close(self):
        """Close all sessions"""
        for session in self._sessions.values():
            if not session.closed:
                await session.close()
        self._sessions.clear()

    # =========================================================================
    # Local Business Data API (Google Maps)
    # =========================================================================

    async def search_local_business(
        self,
        query: str,
        location: str | None = None,
        limit: int = 1
    ) -> LocalBusinessResult:
        """
        Search Google Maps for local businesses.
        Cost: $0.002/query

        Args:
            query: Business name or search query (e.g., "Joe's Plumbing")
            location: City/state to narrow search (e.g., "Denver, CO")
            limit: Number of results (default 1 for best match)

        Returns:
            LocalBusinessResult with owner info, contact details, etc.
        """
        session = await self._get_session(self.LOCAL_BUSINESS_HOST)
        url = f"https://{self.LOCAL_BUSINESS_HOST}/search"

        # Combine query with location if provided
        full_query = f"{query} {location}" if location else query

        params = {
            "query": full_query,
            "limit": str(limit),
            "language": "en",
            "region": "us"
        }

        try:
            async with session.get(url, params=params) as response:
                if response.status == 401:
                    return LocalBusinessResult(
                        place_id=None, name=None, owner_name=None,
                        phone=None, email=None, website=None,
                        address=None, city=None, state=None,
                        rating=None, reviews_count=None, category=None,
                        error="Invalid API key"
                    )
                if response.status == 402:
                    return LocalBusinessResult(
                        place_id=None, name=None, owner_name=None,
                        phone=None, email=None, website=None,
                        address=None, city=None, state=None,
                        rating=None, reviews_count=None, category=None,
                        error="Insufficient credits"
                    )

                result = await response.json()

                # Response has "data" array with businesses
                data = result.get("data", [])
                if not data:
                    return LocalBusinessResult(
                        place_id=None, name=None, owner_name=None,
                        phone=None, email=None, website=None,
                        address=None, city=None, state=None,
                        rating=None, reviews_count=None, category=None,
                        raw_response=result,
                        error="No results found"
                    )

                # Get first (best match) result
                business = data[0]

                # Extract address components
                address = business.get("full_address") or business.get("address")
                city = business.get("city")
                state = business.get("state")

                # Extract social links
                social_links = {}
                if business.get("facebook_url"):
                    social_links["facebook"] = business.get("facebook_url")
                if business.get("instagram_url"):
                    social_links["instagram"] = business.get("instagram_url")
                if business.get("twitter_url"):
                    social_links["twitter"] = business.get("twitter_url")
                if business.get("linkedin_url"):
                    social_links["linkedin"] = business.get("linkedin_url")

                return LocalBusinessResult(
                    place_id=business.get("place_id") or business.get("google_id"),
                    name=business.get("name"),
                    owner_name=business.get("owner_name") or business.get("owner"),
                    phone=business.get("phone") or business.get("phone_number"),
                    email=business.get("email"),
                    website=business.get("website"),
                    address=address,
                    city=city,
                    state=state,
                    rating=business.get("rating"),
                    reviews_count=business.get("reviews") or business.get("review_count"),
                    category=business.get("type") or business.get("category"),
                    social_links=social_links,
                    raw_response=result
                )

        except Exception as e:
            return LocalBusinessResult(
                place_id=None, name=None, owner_name=None,
                phone=None, email=None, website=None,
                address=None, city=None, state=None,
                rating=None, reviews_count=None, category=None,
                error=str(e)
            )

    # =========================================================================
    # Website Contacts Scraper API
    # =========================================================================

    async def scrape_contacts(self, domain: str) -> OpenWebContactResult:
        """
        Extract contacts from a website domain.
        Cost: $0.002/query

        Args:
            domain: Website domain (e.g., "joesplumbing.com" or "https://joesplumbing.com")

        Returns:
            OpenWebContactResult with emails, phones, and social links
        """
        session = await self._get_session(self.WEBSITE_CONTACTS_HOST)
        url = f"https://{self.WEBSITE_CONTACTS_HOST}/scrape-contacts"

        # Normalize domain (remove protocol and www)
        if domain.startswith("http"):
            domain = urlparse(domain).netloc
        domain = domain.replace("www.", "").strip("/")

        payload = {"query": domain}

        try:
            async with session.post(url, json=payload) as response:
                if response.status == 401:
                    return OpenWebContactResult(
                        domain=domain,
                        error="Invalid API key"
                    )
                if response.status == 402:
                    return OpenWebContactResult(
                        domain=domain,
                        error="Insufficient credits"
                    )

                result = await response.json()

                return OpenWebContactResult(
                    domain=result.get("domain", domain),
                    emails=result.get("emails", []),
                    phone_numbers=result.get("phone_numbers", []),
                    linkedin=result.get("linkedin"),
                    facebook=result.get("facebook"),
                    twitter=result.get("twitter"),
                    instagram=result.get("instagram"),
                    youtube=result.get("youtube"),
                    tiktok=result.get("tiktok"),
                    github=result.get("github"),
                    pinterest=result.get("pinterest"),
                    snapchat=result.get("snapchat"),
                    raw_response=result
                )

        except Exception as e:
            return OpenWebContactResult(
                domain=domain,
                error=str(e)
            )

    # =========================================================================
    # Social Links Search API
    # =========================================================================

    async def search_social_links(
        self,
        name: str,
        platform: str = "linkedin"
    ) -> SocialLinksResult:
        """
        Find social media profiles for a person or entity.
        Cost: $0.002/query

        Args:
            name: Person or company name to search
            platform: Primary platform to search ("linkedin", "facebook", etc.)

        Returns:
            SocialLinksResult with URLs for each platform
        """
        session = await self._get_session(self.SOCIAL_LINKS_HOST)
        url = f"https://{self.SOCIAL_LINKS_HOST}/search-social-links"

        payload = {
            "query": name,
            "social_networks": platform
        }

        try:
            async with session.post(url, json=payload) as response:
                if response.status == 401:
                    return SocialLinksResult(
                        query=name,
                        error="Invalid API key"
                    )
                if response.status == 402:
                    return SocialLinksResult(
                        query=name,
                        error="Insufficient credits"
                    )

                result = await response.json()

                # Response format: {"linkedin": [...], "facebook": [...], etc.}
                return SocialLinksResult(
                    query=name,
                    linkedin_urls=result.get("linkedin", []),
                    facebook_urls=result.get("facebook", []),
                    twitter_urls=result.get("twitter", []),
                    instagram_urls=result.get("instagram", []),
                    github_urls=result.get("github", []),
                    youtube_urls=result.get("youtube", []),
                    raw_response=result
                )

        except Exception as e:
            return SocialLinksResult(
                query=name,
                error=str(e)
            )


# =========================================================================
# Convenience test functions
# =========================================================================

async def test_openweb_ninja(api_key: str | None = None):
    """Test OpenWeb Ninja API connection with all 3 endpoints"""
    import os
    api_key = api_key or os.environ.get("RAPIDAPI_KEY")

    if not api_key:
        print("Set RAPIDAPI_KEY environment variable")
        return None

    client = OpenWebNinjaClient(api_key)
    try:
        print("Testing OpenWeb Ninja APIs...")
        print()

        # Test 1: Local Business Data
        print("1. Local Business Data (Google Maps):")
        gmaps = await client.search_local_business("Joe's Plumbing", "Denver, CO")
        if gmaps.success:
            print(f"   Name: {gmaps.name}")
            print(f"   Owner: {gmaps.owner_name}")
            print(f"   Phone: {gmaps.phone}")
            print(f"   Rating: {gmaps.rating} ({gmaps.reviews_count} reviews)")
        else:
            print(f"   Error: {gmaps.error}")
        print()

        # Test 2: Website Contacts Scraper
        print("2. Website Contacts Scraper:")
        contacts = await client.scrape_contacts("microsoft.com")
        if contacts.success:
            print(f"   Emails found: {len(contacts.emails)}")
            if contacts.emails:
                print(f"   Primary: {contacts.primary_email}")
            print(f"   LinkedIn: {contacts.linkedin}")
            print(f"   Facebook: {contacts.facebook}")
        else:
            print(f"   Error: {contacts.error}")
        print()

        # Test 3: Social Links Search
        print("3. Social Links Search:")
        social = await client.search_social_links("Satya Nadella Microsoft")
        if social.success:
            print(f"   LinkedIn URLs found: {len(social.linkedin_urls)}")
            if social.primary_linkedin:
                print(f"   Primary: {social.primary_linkedin}")
        else:
            print(f"   Error: {social.error}")

        return {"gmaps": gmaps, "contacts": contacts, "social": social}

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_openweb_ninja())
