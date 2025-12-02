"""
Multi-Source Contact Finder

Combines multiple sources with LLM confidence scoring:
1. Serper OSINT - Fast, cheap, most current
2. Blitz waterfall-icp - High-quality structured data
3. LLM reconciliation - Confidence scoring when sources disagree

Based on evaluation results:
- Blitz: 91.1% person match rate
- Serper: 100% on recent exec changes
- LeadMagic: 8.9% (excluded - too stale and expensive)
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional
import asyncio
import json

from .serper_osint import SerperOsint, OsintResult
from ..enrichment.blitz import BlitzClient

logger = logging.getLogger(__name__)


@dataclass
class SourceCandidate:
    """A candidate from one source"""
    source: str  # "serper", "blitz", "leadmagic"
    name: str | None
    title: str | None
    linkedin_url: str | None
    email: str | None
    phone: str | None
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)


@dataclass
class MultiSourceResult:
    """Combined result from all sources"""
    # Best candidate after reconciliation
    name: str | None = None
    title: str | None = None
    linkedin_url: str | None = None
    email: str | None = None
    phone: str | None = None

    # Confidence and reasoning
    confidence: float = 0.0
    confidence_reason: str = ""

    # Source details
    sources_queried: list[str] = field(default_factory=list)
    candidates: list[SourceCandidate] = field(default_factory=list)
    sources_agree: bool = False
    evidence: list[str] = field(default_factory=list)

    # Cost tracking
    cost_usd: float = 0.0
    cost_breakdown: dict = field(default_factory=dict)


class MultiSourceFinder:
    """
    Multi-source contact finder with LLM reconciliation.

    Waterfall:
    1. Serper OSINT ($0.001) - Find who's in the role
    2. Blitz ICP ($0.50-4) - Get structured contact data
    3. LLM reconciliation - Score confidence

    Skipped providers (based on eval):
    - LeadMagic: 8.9% match, stale data, expensive
    - Scrapin: 35.4% match (use Blitz instead at 91%)
    """

    def __init__(
        self,
        serper_api_key: str | None = None,
        blitz_api_key: str | None = None,
        openai_api_key: str | None = None
    ):
        self.serper = SerperOsint(serper_api_key) if serper_api_key or os.environ.get("SERPER_API_KEY") else None
        self.blitz = BlitzClient(blitz_api_key) if blitz_api_key or os.environ.get("BLITZ_API_KEY") else None
        self.openai_key = openai_api_key or os.environ.get("OPENAI_API_KEY")

    async def _get_serper_candidate(
        self,
        company_domain: str,
        target_title: str,
        company_name: str | None = None
    ) -> SourceCandidate | None:
        """Get candidate from Serper OSINT"""
        if not self.serper:
            return None

        try:
            result = await self.serper.find_executive(
                company_domain=company_domain,
                target_title=target_title,
                company_name=company_name
            )

            if result.best_match and result.best_match.name:
                return SourceCandidate(
                    source="serper",
                    name=result.best_match.name,
                    title=result.best_match.title or target_title,
                    linkedin_url=result.best_match.linkedin_url,
                    email=None,  # Serper doesn't provide email
                    phone=None,
                    confidence=result.best_match.confidence / 100,
                    evidence=[
                        f"Found via Google Search: '{result.search_query}'",
                        f"Source: {result.best_match.source_type} - {result.best_match.source_url}",
                        f"Snippet: {result.best_match.snippet[:100]}..." if result.best_match.snippet else ""
                    ]
                )
        except Exception as e:
            logger.error(f"Serper search failed: {e}")

        return None

    async def _get_blitz_candidate(
        self,
        linkedin_company_url: str | None,
        target_titles: list[str]
    ) -> SourceCandidate | None:
        """Get candidate from Blitz"""
        if not self.blitz or not linkedin_company_url:
            return None

        try:
            contacts = await self.blitz.waterfall_icp(
                linkedin_company_url=linkedin_company_url,
                titles=target_titles,
                max_results=1
            )

            if contacts:
                c = contacts[0]
                return SourceCandidate(
                    source="blitz",
                    name=c.name,
                    title=c.title,
                    linkedin_url=c.linkedin_url,
                    email=c.email,
                    phone=c.phone,
                    confidence=0.91,  # Based on eval: 91.1% match rate
                    evidence=[
                        f"Blitz waterfall-icp returned {len(contacts)} contact(s)",
                        f"Title searched: {target_titles[0] if target_titles else 'any'}"
                    ]
                )
        except Exception as e:
            logger.error(f"Blitz lookup failed: {e}")

        return None

    def _names_match(self, name1: str | None, name2: str | None) -> bool:
        """Check if two names match (fuzzy)"""
        if not name1 or not name2:
            return False

        n1 = name1.lower().strip()
        n2 = name2.lower().strip()

        # Exact match
        if n1 == n2:
            return True

        # One contains the other
        if n1 in n2 or n2 in n1:
            return True

        # First and last name match
        p1 = n1.split()
        p2 = n2.split()
        if len(p1) >= 2 and len(p2) >= 2:
            if p1[0] == p2[0] and p1[-1] == p2[-1]:
                return True

        return False

    async def _llm_reconcile(
        self,
        candidates: list[SourceCandidate],
        company_name: str,
        target_title: str
    ) -> tuple[SourceCandidate, str]:
        """
        Use LLM to reconcile conflicting candidates.

        Returns:
            Tuple of (best_candidate, reasoning)
        """
        if not self.openai_key or len(candidates) < 2:
            # No LLM or only one candidate - return highest confidence
            best = max(candidates, key=lambda x: x.confidence)
            return best, "Single source or no LLM available"

        import aiohttp

        prompt = f"""You are evaluating candidates for the {target_title} role at {company_name}.

Candidates from different sources:
{json.dumps([{
    "source": c.source,
    "name": c.name,
    "title": c.title,
    "linkedin_url": c.linkedin_url,
    "evidence": c.evidence
} for c in candidates], indent=2)}

Which candidate is most likely the CURRENT {target_title}?

Consider:
1. Serper (Google Search) finds recent news - good for detecting recent changes
2. Blitz uses LinkedIn data - may lag 1-4 weeks behind job changes
3. If a news source mentions a recent appointment, that's likely the current person

Return JSON:
{{
    "best_candidate_index": 0,  // Index of best candidate (0-based)
    "confidence": 0.85,  // 0.0-1.0
    "reasoning": "Brief explanation"
}}"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result = json.loads(data["choices"][0]["message"]["content"])
                        idx = result.get("best_candidate_index", 0)
                        idx = min(idx, len(candidates) - 1)
                        candidates[idx].confidence = result.get("confidence", candidates[idx].confidence)
                        return candidates[idx], result.get("reasoning", "LLM selection")

        except Exception as e:
            logger.error(f"LLM reconciliation failed: {e}")

        # Fallback: prefer Serper for recency
        for c in candidates:
            if c.source == "serper":
                return c, "Fallback: preferring Serper for recency"

        return candidates[0], "Fallback: first candidate"

    async def find_contact(
        self,
        company_domain: str,
        target_title: str,
        company_name: str | None = None,
        linkedin_company_url: str | None = None,
        use_llm_reconciliation: bool = True
    ) -> MultiSourceResult:
        """
        Find a contact using multiple sources.

        Args:
            company_domain: Company domain (e.g., "kohls.com")
            target_title: Target title (e.g., "CEO")
            company_name: Optional company name
            linkedin_company_url: Optional LinkedIn company URL for Blitz
            use_llm_reconciliation: Use LLM to reconcile conflicting sources

        Returns:
            MultiSourceResult with best candidate and confidence
        """
        result = MultiSourceResult()
        company_name = company_name or company_domain.split('.')[0].title()

        # Map titles for Blitz
        title_variants = {
            "CEO": ["CEO", "Chief Executive Officer", "President", "Founder", "Owner"],
            "CFO": ["CFO", "Chief Financial Officer", "VP Finance", "Finance Director"],
            "CMO": ["CMO", "Chief Marketing Officer", "VP Marketing", "Head of Marketing"],
            "CTO": ["CTO", "Chief Technology Officer", "VP Engineering", "Head of Engineering"],
            "VP Sales": ["VP Sales", "Head of Sales", "CRO", "Chief Revenue Officer", "Sales Director"],
            "VP Marketing": ["VP Marketing", "Head of Marketing", "CMO", "Marketing Director"],
        }
        target_titles = title_variants.get(target_title, [target_title])

        # Query sources in parallel
        tasks = []

        if self.serper:
            tasks.append(self._get_serper_candidate(company_domain, target_title, company_name))
            result.sources_queried.append("serper")
            result.cost_usd += 0.001
            result.cost_breakdown["serper"] = 0.001

        if self.blitz and linkedin_company_url:
            tasks.append(self._get_blitz_candidate(linkedin_company_url, target_titles))
            result.sources_queried.append("blitz")
            result.cost_usd += 0.50  # Estimate
            result.cost_breakdown["blitz"] = 0.50

        if tasks:
            candidates = await asyncio.gather(*tasks)
            result.candidates = [c for c in candidates if c is not None]

        if not result.candidates:
            result.confidence_reason = "No candidates found from any source"
            return result

        # Check if sources agree
        if len(result.candidates) >= 2:
            names = [c.name for c in result.candidates if c.name]
            result.sources_agree = len(set(n.lower().strip() for n in names)) == 1

        # Reconcile candidates
        if len(result.candidates) == 1:
            best = result.candidates[0]
            result.confidence_reason = f"Single source: {best.source}"
        elif result.sources_agree:
            # All sources agree - high confidence
            best = max(result.candidates, key=lambda x: x.confidence)
            best.confidence = min(best.confidence + 0.1, 0.98)
            result.confidence_reason = f"All {len(result.candidates)} sources agree"
        elif use_llm_reconciliation:
            # Sources disagree - use LLM
            best, reason = await self._llm_reconcile(result.candidates, company_name, target_title)
            result.confidence_reason = f"LLM reconciliation: {reason}"
            result.cost_usd += 0.001  # GPT-4o-mini cost
            result.cost_breakdown["llm"] = 0.001
        else:
            # Prefer Serper for recency
            serper_candidates = [c for c in result.candidates if c.source == "serper"]
            best = serper_candidates[0] if serper_candidates else result.candidates[0]
            result.confidence_reason = "Preferring Serper for recency (no LLM)"

        # Fill result
        result.name = best.name
        result.title = best.title
        result.linkedin_url = best.linkedin_url
        result.email = best.email
        result.phone = best.phone
        result.confidence = best.confidence
        result.evidence = best.evidence

        # Merge evidence from all candidates
        for c in result.candidates:
            if c != best:
                result.evidence.append(f"Alt from {c.source}: {c.name} ({c.title})")

        return result


# Test function
async def test_multi_source():
    """Test multi-source finder"""
    finder = MultiSourceFinder()

    # Test: Find CEO of Kohl's (recent change - Michael Bender appointed Nov 2025)
    print("=" * 60)
    print("Test: Find CEO of Kohl's (recent change)")
    print("=" * 60)

    result = await finder.find_contact(
        company_domain="kohls.com",
        target_title="CEO",
        company_name="Kohl's"
    )

    print(f"Name: {result.name}")
    print(f"Title: {result.title}")
    print(f"LinkedIn: {result.linkedin_url}")
    print(f"Email: {result.email}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Sources agree: {result.sources_agree}")
    print(f"Reason: {result.confidence_reason}")
    print(f"Cost: ${result.cost_usd:.4f}")
    print(f"Evidence:")
    for e in result.evidence:
        print(f"  - {e}")

    return result


if __name__ == "__main__":
    asyncio.run(test_multi_source())
