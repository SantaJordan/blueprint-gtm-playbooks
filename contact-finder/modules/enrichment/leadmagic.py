"""
LeadMagic API Client
https://api.leadmagic.io

Endpoint:
- POST /email-finder - Find work email from name + domain/company
"""

import aiohttp
from dataclasses import dataclass
from typing import Any


@dataclass
class LeadMagicEmailResult:
    email: str | None
    status: str  # valid, invalid, unknown
    is_catch_all: bool
    mx_record: bool
    mx_provider: str | None
    credits_consumed: int
    company_data: dict | None
    raw_response: dict


@dataclass
class LeadMagicProfileResult:
    """Result from profile-search endpoint (LinkedIn URL → profile data)"""
    success: bool
    full_name: str | None
    first_name: str | None
    last_name: str | None
    professional_title: str | None
    company_name: str | None
    work_experience: list[dict]
    education: list[dict]
    certifications: list[dict]
    location: str | None
    linkedin_url: str | None
    credits_consumed: int
    raw_response: dict
    error: str | None = None


@dataclass
class LeadMagicB2BProfileResult:
    """Result from b2b-profile endpoint (email → LinkedIn URL)"""
    success: bool
    linkedin_url: str | None
    first_name: str | None
    last_name: str | None
    full_name: str | None
    professional_title: str | None
    company_name: str | None
    credits_consumed: int
    raw_response: dict
    error: str | None = None


class LeadMagicClient:
    """LeadMagic API client for email finding"""

    BASE_URL = "https://api.leadmagic.io"

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"X-API-Key": self.api_key, "Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def find_email(
        self,
        first_name: str,
        last_name: str | None = None,
        domain: str | None = None,
        company_name: str | None = None
    ) -> LeadMagicEmailResult:
        """
        Find email address using name and company info
        Pay-if-found model - only charged if email is found

        Args:
            first_name: Person's first name (required)
            last_name: Person's last name (optional but recommended)
            domain: Company domain (optional)
            company_name: Company name (optional)

        Returns:
            LeadMagicEmailResult with email and validation data
        """
        session = await self._get_session()
        url = f"{self.BASE_URL}/email-finder"

        payload = {"first_name": first_name}

        if last_name:
            payload["last_name"] = last_name
        if domain:
            payload["domain"] = domain
        if company_name:
            payload["company_name"] = company_name

        try:
            async with session.post(url, json=payload) as response:
                if response.status == 400:
                    return LeadMagicEmailResult(
                        email=None,
                        status="invalid_request",
                        is_catch_all=False,
                        mx_record=False,
                        mx_provider=None,
                        credits_consumed=0,
                        company_data=None,
                        raw_response={"error": "Invalid request or missing parameters"}
                    )

                result = await response.json()

                # Extract company data if present
                company_data = None
                if "company" in result:
                    company_data = {
                        "name": result["company"].get("name"),
                        "industry": result["company"].get("industry"),
                        "size": result["company"].get("size"),
                        "linkedin_url": result["company"].get("linkedin_url"),
                        "facebook_url": result["company"].get("facebook_url"),
                        "twitter_url": result["company"].get("twitter_url"),
                    }

                return LeadMagicEmailResult(
                    email=result.get("email"),
                    status=result.get("status", "unknown"),
                    is_catch_all=result.get("is_domain_catch_all", False),
                    mx_record=result.get("mx_record", False),
                    mx_provider=result.get("mx_provider"),
                    credits_consumed=result.get("credits_consumed", 0),
                    company_data=company_data,
                    raw_response=result
                )

        except Exception as e:
            return LeadMagicEmailResult(
                email=None,
                status=f"error: {str(e)}",
                is_catch_all=False,
                mx_record=False,
                mx_provider=None,
                credits_consumed=0,
                company_data=None,
                raw_response={}
            )

    async def profile_search(self, linkedin_url: str) -> LeadMagicProfileResult:
        """
        Enrich a LinkedIn profile URL to get profile data
        POST /v1/people/profile-search - 1 credit

        Args:
            linkedin_url: LinkedIn profile URL (e.g., https://www.linkedin.com/in/username)

        Returns:
            LeadMagicProfileResult with name, title, company, work experience, education, etc.
        """
        session = await self._get_session()
        url = f"{self.BASE_URL}/v1/people/profile-search"
        payload = {"profile_url": linkedin_url}

        try:
            async with session.post(url, json=payload) as response:
                if response.status == 400:
                    return LeadMagicProfileResult(
                        success=False,
                        full_name=None,
                        first_name=None,
                        last_name=None,
                        professional_title=None,
                        company_name=None,
                        work_experience=[],
                        education=[],
                        certifications=[],
                        location=None,
                        linkedin_url=linkedin_url,
                        credits_consumed=0,
                        raw_response={"error": "Invalid request"},
                        error="Invalid request or URL"
                    )

                if response.status == 404:
                    return LeadMagicProfileResult(
                        success=False,
                        full_name=None,
                        first_name=None,
                        last_name=None,
                        professional_title=None,
                        company_name=None,
                        work_experience=[],
                        education=[],
                        certifications=[],
                        location=None,
                        linkedin_url=linkedin_url,
                        credits_consumed=0,
                        raw_response={"error": "Profile not found"},
                        error="Profile not found"
                    )

                result = await response.json()

                # Extract work experience
                work_experience = result.get("work_experience", []) or []

                # Get current company from first work experience
                company_name = None
                professional_title = None
                if work_experience and len(work_experience) > 0:
                    current_job = work_experience[0]
                    company_name = current_job.get("company_name")
                    professional_title = current_job.get("title")

                # Also check top-level fields
                if not company_name:
                    company_name = result.get("company_name")
                if not professional_title:
                    professional_title = result.get("professional_title") or result.get("title")

                return LeadMagicProfileResult(
                    success=True,
                    full_name=result.get("full_name"),
                    first_name=result.get("first_name"),
                    last_name=result.get("last_name"),
                    professional_title=professional_title,
                    company_name=company_name,
                    work_experience=work_experience,
                    education=result.get("education", []) or [],
                    certifications=result.get("certifications", []) or [],
                    location=result.get("location"),
                    linkedin_url=result.get("linkedin_url") or linkedin_url,
                    credits_consumed=result.get("credits_consumed", 1),
                    raw_response=result,
                    error=None
                )

        except Exception as e:
            return LeadMagicProfileResult(
                success=False,
                full_name=None,
                first_name=None,
                last_name=None,
                professional_title=None,
                company_name=None,
                work_experience=[],
                education=[],
                certifications=[],
                location=None,
                linkedin_url=linkedin_url,
                credits_consumed=0,
                raw_response={},
                error=str(e)
            )

    async def email_to_linkedin(self, email: str) -> "LeadMagicB2BProfileResult":
        """
        Convert work email to LinkedIn profile URL.

        POST /v1/people/b2b-profile
        Cost: 10 credits

        Args:
            email: Work email address

        Returns:
            LeadMagicB2BProfileResult with LinkedIn URL if found
        """
        session = await self._get_session()
        url = f"{self.BASE_URL}/v1/people/b2b-profile"
        payload = {"work_email": email}

        try:
            async with session.post(url, json=payload) as response:
                if response.status == 400:
                    return LeadMagicB2BProfileResult(
                        success=False,
                        linkedin_url=None,
                        first_name=None,
                        last_name=None,
                        full_name=None,
                        professional_title=None,
                        company_name=None,
                        credits_consumed=0,
                        raw_response={"error": "Invalid request"},
                        error="Invalid email or request"
                    )

                if response.status == 404:
                    return LeadMagicB2BProfileResult(
                        success=False,
                        linkedin_url=None,
                        first_name=None,
                        last_name=None,
                        full_name=None,
                        professional_title=None,
                        company_name=None,
                        credits_consumed=0,
                        raw_response={"error": "Profile not found"},
                        error="No LinkedIn profile found for this email"
                    )

                result = await response.json()

                # Extract profile URL
                profile_url = result.get("profile_url") or result.get("linkedin_url")

                # Build full name if parts available
                first_name = result.get("first_name")
                last_name = result.get("last_name")
                full_name = result.get("full_name")
                if not full_name and first_name:
                    full_name = f"{first_name} {last_name or ''}".strip()

                return LeadMagicB2BProfileResult(
                    success=bool(profile_url),
                    linkedin_url=profile_url,
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    professional_title=result.get("professional_title") or result.get("title"),
                    company_name=result.get("company_name") or result.get("company"),
                    credits_consumed=result.get("credits_consumed", 10),
                    raw_response=result,
                    error=None
                )

        except Exception as e:
            return LeadMagicB2BProfileResult(
                success=False,
                linkedin_url=None,
                first_name=None,
                last_name=None,
                full_name=None,
                professional_title=None,
                company_name=None,
                credits_consumed=0,
                raw_response={},
                error=str(e)
            )


def split_name(full_name: str) -> tuple[str, str | None]:
    """Split a full name into first and last name"""
    parts = full_name.strip().split()
    if len(parts) == 0:
        return "", None
    elif len(parts) == 1:
        return parts[0], None
    else:
        return parts[0], " ".join(parts[1:])


# Convenience function
async def test_leadmagic_api(api_key: str):
    """Test LeadMagic API connection"""
    client = LeadMagicClient(api_key)
    try:
        # Try a known test case
        result = await client.find_email(
            first_name="Bill",
            last_name="Gates",
            domain="microsoft.com"
        )
        print(f"LeadMagic API connected. Test result: {result.status}")
        return result.email is not None
    except Exception as e:
        print(f"LeadMagic API error: {e}")
        return False
    finally:
        await client.close()
