"""
Wave 2.5: Situation-Based Fallback

Triggers when all vertical niches fail Criterion 5 (Product-Solution Alignment).
Generates TIMING-based plays that connect DATA → SITUATION → PAIN → PRODUCT.

For horizontal products that serve any business without vertical-specific data moats.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import re

from tools.claude_retry import call_claude_with_retry


class NoFitTier(Enum):
    """Tiers for no-fit response handling."""
    HONEST_REJECTION = 1  # No viable segments at all
    SITUATION_FALLBACK = 2  # Timing plays available
    PIVOT_SUGGESTION = 3  # Recommend repositioning


@dataclass
class NoFitResponse:
    """Response when no segments pass validation."""
    tier: NoFitTier
    should_abort: bool
    message: str
    pivot_suggestions: List[str]
    fallback_segments: List[Dict]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "tier": self.tier.name,
            "tier_value": self.tier.value,
            "should_abort": self.should_abort,
            "message": self.message,
            "pivot_suggestions": self.pivot_suggestions,
            "fallback_segments": self.fallback_segments
        }


class Wave25SituationFallback:
    """Wave 2.5: Situation-based segment generation fallback."""

    # Situation categories with detection patterns
    SITUATION_CATEGORIES = {
        "time_pressure": {
            "name": "Time Pressure",
            "description": "External event creating time-bound urgency",
            "examples": [
                "Conference/trade show in [N] weeks",
                "Product launch date approaching",
                "Office move scheduled",
                "Merger announcement with rebrand deadline",
                "Regulatory deadline"
            ]
        },
        "scale_pressure": {
            "name": "Scale Pressure",
            "description": "Rapid growth creating gaps",
            "examples": [
                "10+ new hires per month",
                "3x customer growth in 6 months",
                "Expanding to new locations",
                "Post-funding rapid scaling",
                "Seasonal volume spikes"
            ]
        },
        "change_pressure": {
            "name": "Change Pressure",
            "description": "Transitions making old solutions obsolete",
            "examples": [
                "Company rebrand (name, logo, colors)",
                "Office relocation (address change)",
                "Post-M&A integration",
                "Leadership change (new C-suite)",
                "Market pivot (new positioning)"
            ]
        }
    }

    def __init__(self, claude_client, web_search):
        self.claude = claude_client
        self.web_search = web_search

    async def execute(self, company_context: Dict, product_fit: Dict) -> Dict:
        """
        Generate situation-based segments when niche conversion fails.

        Args:
            company_context: Output from Wave 1
            product_fit: Output from Wave 0.5

        Returns:
            {
                "situation_segments": [
                    {
                        "name": str,
                        "category": str,
                        "trigger_event": str,
                        "detection_method": str,
                        "data_sources": [{"source": str, "method": str, "confidence": str}],
                        "pain_hypothesis": str,
                        "product_fit_score": int,
                        "texada_pass": bool,
                        "message_type": str,
                        "confidence_level": int,
                        "verdict": str
                    }
                ],
                "fallback_used": bool,
                "no_fit_warning": Optional[str]
            }
        """
        core_problem = product_fit.get("core_problem", "")
        product_type = product_fit.get("product_type", "")
        urgency_triggers = product_fit.get("urgency_triggers", [])
        valid_domains = product_fit.get("valid_domains", [])

        # Generate situation segments for each pressure category
        segments = []

        for category_key, category_info in self.SITUATION_CATEGORIES.items():
            category_segments = await self._generate_category_segments(
                category_key,
                category_info,
                product_fit,
                company_context
            )
            segments.extend(category_segments)

        # Score and filter segments
        scored_segments = []
        for segment in segments:
            scored = await self._score_segment(segment, product_fit)
            if scored["product_fit_score"] >= 5:
                scored_segments.append(scored)

        # Sort by product fit score and confidence
        scored_segments.sort(
            key=lambda x: (x["product_fit_score"], x["confidence_level"]),
            reverse=True
        )

        # Take top 3 segments
        top_segments = scored_segments[:3]

        # Determine no-fit response based on segment availability
        no_fit_response = self._determine_no_fit_response(top_segments, product_fit)

        return {
            "situation_segments": top_segments,
            "fallback_used": True,
            "no_fit_response": no_fit_response.to_dict() if no_fit_response else None,
            "should_abort": no_fit_response.should_abort if no_fit_response else False,
            "no_fit_warning": no_fit_response.message if no_fit_response and no_fit_response.should_abort else None
        }

    async def _generate_category_segments(
        self,
        category_key: str,
        category_info: Dict,
        product_fit: Dict,
        company_context: Dict
    ) -> List[Dict]:
        """Generate situation segments for a category."""
        prompt = f"""Generate situation-based segments for this product in the {category_info['name']} category.

PRODUCT INFORMATION:
- Core Problem Solved: {product_fit.get('core_problem', 'Unknown')}
- Product Type: {product_fit.get('product_type', 'Unknown')}
- Urgency Triggers: {', '.join(product_fit.get('urgency_triggers', []))}
- Valid Pain Domains: {', '.join(product_fit.get('valid_domains', []))}

CATEGORY: {category_info['name']}
Description: {category_info['description']}
Example situations: {', '.join(category_info['examples'])}

Generate 2 specific situation-based segments that:
1. Create genuine urgency for this product
2. Can be detected using external data
3. Make the product the DIRECT solution

For each segment, provide:
SEGMENT_NAME: [Descriptive name]
TRIGGER_EVENT: [What creates the urgency - be specific]
DETECTION_METHOD: [How we know this situation exists externally]
DATA_SOURCE_1: [Source name] | [API/Method] | [HIGH/MEDIUM/LOW confidence]
DATA_SOURCE_2: [Source name] | [API/Method] | [HIGH/MEDIUM/LOW confidence]
PAIN_HYPOTHESIS: [Why they need the product NOW, not later]
---
[Repeat for second segment]"""

        response = await call_claude_with_retry(
            self.claude,
            model="claude-sonnet-4-5-20250929",  # Sonnet 4.5 for faster situation gen
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_segments(response.content[0].text, category_key)

    def _parse_segments(self, text: str, category: str) -> List[Dict]:
        """Parse Claude's segment response."""
        segments = []

        # Split by separator
        segment_blocks = text.split("---")

        for block in segment_blocks:
            if not block.strip():
                continue

            segment = {
                "name": "",
                "category": category,
                "trigger_event": "",
                "detection_method": "",
                "data_sources": [],
                "pain_hypothesis": ""
            }

            # Extract fields
            patterns = {
                "name": r"SEGMENT_NAME:\s*(.+?)(?=\n|$)",
                "trigger_event": r"TRIGGER_EVENT:\s*(.+?)(?=\n[A-Z_]+:|$)",
                "detection_method": r"DETECTION_METHOD:\s*(.+?)(?=\n[A-Z_]+:|$)",
                "pain_hypothesis": r"PAIN_HYPOTHESIS:\s*(.+?)(?=\n[A-Z_]+:|$|---)"
            }

            for key, pattern in patterns.items():
                match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
                if match:
                    segment[key] = match.group(1).strip()

            # Extract data sources
            source_pattern = r"DATA_SOURCE_\d:\s*(.+?)\|(.+?)\|(.+?)(?=\n|$)"
            for match in re.finditer(source_pattern, block, re.IGNORECASE):
                segment["data_sources"].append({
                    "source": match.group(1).strip(),
                    "method": match.group(2).strip(),
                    "confidence": match.group(3).strip().upper()
                })

            if segment["name"]:
                segments.append(segment)

        return segments

    async def _score_segment(self, segment: Dict, product_fit: Dict) -> Dict:
        """Score a situation segment for product fit and Texada test."""
        prompt = f"""Score this situation segment for product fit.

PRODUCT:
- Core Problem: {product_fit.get('core_problem', 'Unknown')}
- Product Type: {product_fit.get('product_type', 'Unknown')}
- Valid Pain Domains: {', '.join(product_fit.get('valid_domains', []))}

SEGMENT:
- Name: {segment['name']}
- Trigger: {segment['trigger_event']}
- Detection: {segment['detection_method']}
- Pain Hypothesis: {segment['pain_hypothesis']}

ANSWER THESE QUESTIONS:

1. PRODUCT_FIT_SCORE (0-10):
Does this situation create genuine need for THIS product?
Is the product the DIRECT solution?
Would buying the product resolve the immediate problem?
10 = Product is the obvious, direct solution
5 = Product helps but isn't the primary solution
0 = No real connection

2. TEXADA_TEST:
- HYPER_SPECIFIC: Can we identify specific companies in this situation? (YES/NO)
- FACTUALLY_GROUNDED: Is the situation externally observable? (YES/NO)
- NON_OBVIOUS: Do they know they're in this situation AND its implications? (YES/NO)

3. MESSAGE_TYPE: PQS or Situational_PVP

4. CONFIDENCE_LEVEL: (0-100) How confident can we be in detecting this situation?

5. VERDICT: PROCEED, REVISE, or REJECT

Format:
PRODUCT_FIT_SCORE: [0-10]
HYPER_SPECIFIC: [YES/NO]
FACTUALLY_GROUNDED: [YES/NO]
NON_OBVIOUS: [YES/NO]
MESSAGE_TYPE: [PQS/Situational_PVP]
CONFIDENCE_LEVEL: [0-100]
VERDICT: [PROCEED/REVISE/REJECT]"""

        response = await call_claude_with_retry(
            self.claude,
            model="claude-haiku-4-5-20251001",  # Haiku for simple scoring
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_score_response(segment, response.content[0].text)

    def _parse_score_response(self, segment: Dict, text: str) -> Dict:
        """Parse scoring response and merge with segment."""
        scored = segment.copy()

        # Extract product fit score
        match = re.search(r"PRODUCT_FIT_SCORE:\s*(\d+)", text, re.IGNORECASE)
        scored["product_fit_score"] = int(match.group(1)) if match else 0

        # Extract Texada test results
        texada_checks = ["HYPER_SPECIFIC", "FACTUALLY_GROUNDED", "NON_OBVIOUS"]
        texada_results = []
        for check in texada_checks:
            match = re.search(rf"{check}:\s*(YES|NO)", text, re.IGNORECASE)
            if match:
                texada_results.append(match.group(1).upper() == "YES")
        scored["texada_pass"] = all(texada_results) if texada_results else False

        # Extract message type
        match = re.search(r"MESSAGE_TYPE:\s*(PQS|Situational_PVP)", text, re.IGNORECASE)
        scored["message_type"] = match.group(1) if match else "PQS"

        # Extract confidence level
        match = re.search(r"CONFIDENCE_LEVEL:\s*(\d+)", text, re.IGNORECASE)
        scored["confidence_level"] = int(match.group(1)) if match else 50

        # Extract verdict
        match = re.search(r"VERDICT:\s*(PROCEED|REVISE|REJECT)", text, re.IGNORECASE)
        scored["verdict"] = match.group(1).upper() if match else "REJECT"

        return scored

    def _determine_no_fit_response(
        self,
        segments: List[Dict],
        product_fit: Dict
    ) -> Optional[NoFitResponse]:
        """
        Determine the appropriate no-fit response based on segment availability.

        Tiers:
        - HONEST_REJECTION: No viable segments, abort recommended
        - SITUATION_FALLBACK: Timing plays available, continue
        - PIVOT_SUGGESTION: Few low-quality segments, suggest repositioning
        """
        product_type = product_fit.get('product_type', 'Unknown')
        core_problem = product_fit.get('core_problem', 'Unknown')

        # Tier 2: Situation fallback successful - segments available
        if segments and len(segments) >= 2:
            avg_score = sum(s.get("product_fit_score", 0) for s in segments) / len(segments)
            if avg_score >= 6:
                return None  # Good segments, no warning needed

            # Low-quality segments available
            return NoFitResponse(
                tier=NoFitTier.SITUATION_FALLBACK,
                should_abort=False,
                message=f"Situation-based segments generated with avg score {avg_score:.1f}/10",
                pivot_suggestions=[
                    "Consider targeting companies during specific events (trade shows, funding rounds)",
                    "Focus on change-driven triggers (rebrands, office moves, M&A)",
                    "Target seasonal spikes in relevant industries"
                ],
                fallback_segments=segments
            )

        # Tier 3: Few/weak segments - suggest pivot
        if segments and len(segments) == 1:
            return NoFitResponse(
                tier=NoFitTier.PIVOT_SUGGESTION,
                should_abort=False,
                message=f"Only 1 viable situation segment found for {product_type}. Consider repositioning.",
                pivot_suggestions=[
                    f"Reframe {core_problem} around time-sensitive events",
                    "Target companies post-funding for scale pressure plays",
                    "Focus on rebrand/relocation triggers for change pressure",
                    "Consider if product has vertical-specific applications worth exploring"
                ],
                fallback_segments=segments
            )

        # Tier 1: No viable segments - honest rejection
        return NoFitResponse(
            tier=NoFitTier.HONEST_REJECTION,
            should_abort=True,
            message=self._generate_no_fit_message(product_fit),
            pivot_suggestions=[
                "Internal Data Only: If sender has 100+ customers, can create benchmark PVPs",
                "PQS-Only Approach: Use competitive intelligence for pain identification",
                "Manual Targeting: This use case may require manual prospect identification",
                "Consider if product fits the data-driven Blueprint methodology"
            ],
            fallback_segments=[]
        )

    def _generate_no_fit_message(self, product_fit: Dict) -> str:
        """Generate detailed message for honest rejection tier."""
        return f"""⚠️ BLUEPRINT COMPATIBILITY WARNING

No situation-based segments passed product-fit validation.

Product: {product_fit.get('product_type', 'Unknown')}
Core Problem: {product_fit.get('core_problem', 'Unknown')}

ASSESSMENT:
This product may not be well-suited for the Blueprint GTM methodology, which requires:
1. Externally detectable pain signals (government databases, public records)
2. Time-sensitive urgency triggers (deadlines, violations, events)
3. Direct product-to-pain connection (product solves the specific pain)

RECOMMENDATION:
The product may be better suited for traditional outbound approaches or
internal-data-driven campaigns using existing customer patterns."""

    def should_trigger(self, niche_results: Dict) -> bool:
        """Check if situation fallback should be triggered."""
        if niche_results.get("fallback_needed", False):
            return True

        qualified_niches = niche_results.get("qualified_niches", [])
        if not qualified_niches:
            return True

        # All niches failed product-fit
        all_failed = all(
            n.get("score", {}).get("product_solution_alignment", 0) < 5
            for n in qualified_niches
        )
        return all_failed
