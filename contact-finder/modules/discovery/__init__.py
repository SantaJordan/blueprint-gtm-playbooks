"""
Discovery modules for finding company and contact information
"""

from .linkedin_company import LinkedInCompanyDiscovery, CompanyLinkedInResult
from .contact_search import ContactSearchEngine, ContactCandidate
from .openweb_ninja import (
    OpenWebNinjaClient,
    LocalBusinessResult,
    OpenWebContactResult,
    SocialLinksResult,
)

__all__ = [
    "LinkedInCompanyDiscovery",
    "CompanyLinkedInResult",
    "ContactSearchEngine",
    "ContactCandidate",
    # OpenWeb Ninja
    "OpenWebNinjaClient",
    "LocalBusinessResult",
    "OpenWebContactResult",
    "SocialLinksResult",
]
