"""
Synthesis: Extended Thinking for Segment Generation

Uses Claude's native extended thinking API to generate pain segment hypotheses
that combine available data sources with deep reasoning.
"""
from typing import Dict, List
import re

from tools.claude_retry import call_claude_with_retry

# Extended thinking budget tiers
THINKING_BUDGET_STANDARD = 8000   # Standard synthesis (2-5 data sources)
THINKING_BUDGET_COMPLEX = 16000  # Complex synthesis (6+ data sources)


class Synthesis:
    """Synthesis: Generate pain segments using extended thinking."""

    # Removed SYSTEM_PROMPT - extended thinking doesn't use system prompts

    def __init__(self, claude_client):
        self.claude = claude_client

    async def generate_segments(
        self,
        company_context: Dict,
        data_landscape: Dict,
        product_fit: Dict
    ) -> Dict:
        """
        Use extended thinking to generate pain segments.

        Args:
            company_context: Output from Wave 1
            data_landscape: Output from Wave 2
            product_fit: Output from Wave 0.5

        Returns:
            {
                "segments": [
                    {
                        "name": str,
                        "description": str,
                        "data_sources": [str],
                        "fields": [str],
                        "confidence": str,
                        "texada_check": {...},
                        "message_type": str
                    }
                ],
                "thinking": str,
                "success": bool
            }
        """
        # Count data sources to determine thinking budget
        source_count = sum(
            len(sources) for sources in data_landscape.values()
            if isinstance(sources, list)
        )
        thinking_budget = THINKING_BUDGET_COMPLEX if source_count > 5 else THINKING_BUDGET_STANDARD
        print(f"[Synthesis] {source_count} data sources detected, using {thinking_budget} token thinking budget")

        # Build comprehensive prompt for extended thinking
        prompt = f"""You are generating pain segment hypotheses for Blueprint GTM outreach.

COMPANY CONTEXT:
Company: {company_context.get('company_name', 'Unknown')}
Offering: {company_context.get('offering', 'Unknown')}
ICP: {company_context.get('icp', 'Unknown')}
Target Persona: {company_context.get('persona_title', 'Unknown')} - {company_context.get('persona', '')}

PRODUCT FIT ANALYSIS:
Core Problem Solved: {product_fit.get('core_problem', 'Unknown')}
Valid Pain Domains: {', '.join(product_fit.get('valid_domains', []))}
Invalid Pain Domains: {', '.join(product_fit.get('invalid_domains', []))}

DATA LANDSCAPE (Available Sources):
{self._format_data_landscape(data_landscape)}

TASK: Generate 2-4 pain segment hypotheses using ONLY the data sources listed above.

CRITICAL REQUIREMENTS:
1. Each segment MUST combine 2-3 data sources for non-obvious synthesis
2. Use specific field names from the data sources (not generic placeholders)
3. Validate against Texada Test:
   - HYPER-SPECIFIC: Uses actual field names, dates, record numbers (NOT "recent", "many", "several")
   - FACTUALLY GROUNDED: Every claim traces to specific database field, NO assumptions
   - NON-OBVIOUS: Insight the persona doesn't already have access to
4. Classify as PQS (pure government data mirror, 90%+ data) or PVP (hybrid value delivery, 60-75%)
5. Ensure segment connects to product's VALID pain domains (not invalid ones!)

OUTPUT FORMAT (exactly as shown):

SEGMENT 1:
- Name: [descriptive segment name]
- Description: [what painful situation this captures and why it matters]
- Data Sources: [source1 + source2 + source3]
- Fields: [specific field names to extract from each source]
- Confidence: [HIGH 90%+ / MEDIUM 60-75% / LOW 50-70%]
- Texada: [PASS/FAIL] Hyper-specific, [PASS/FAIL] Factually Grounded, [PASS/FAIL] Non-obvious
- Message Type: [PQS or PVP]

SEGMENT 2:
...

SEGMENT 3:
..."""

        response = await call_claude_with_retry(
            self.claude,
            model="claude-sonnet-4-5-20250929",  # Sonnet 4.5 supports extended thinking
            max_tokens=16000,  # Higher for extended thinking response
            messages=[{"role": "user", "content": prompt}],
            thinking_budget=thinking_budget
        )

        # Extract text and thinking from response
        raw_text = ""
        thinking_text = ""
        for block in response.content:
            if hasattr(block, 'type'):
                if block.type == "thinking":
                    thinking_text = getattr(block, 'thinking', '')
                elif block.type == "text":
                    raw_text = getattr(block, 'text', '')
            elif hasattr(block, 'text'):
                raw_text = block.text

        print(f"[Synthesis] Extended thinking used {len(thinking_text)} chars of reasoning")
        segments = self._parse_segments(raw_text)

        return {
            "segments": segments,
            "thinking": thinking_text,  # Store actual thinking for debugging
            "raw_output": raw_text,
            "success": len(segments) > 0
        }

    def _parse_segments(self, text: str) -> List[Dict]:
        """Parse segment definitions from thinking output."""
        segments = []

        # Find SEGMENT blocks
        segment_pattern = r'SEGMENT\s*\d+[:\s]+(.+?)(?=SEGMENT\s*\d+|$)'
        matches = re.findall(segment_pattern, text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            segment = {
                "name": "",
                "description": "",
                "data_sources": [],
                "fields": [],
                "confidence": "MEDIUM",
                "texada_check": {
                    "hyper_specific": False,
                    "factually_grounded": False,
                    "non_obvious": False
                },
                "message_type": "PQS"
            }

            # Parse fields
            name_match = re.search(r'Name[:\s]+(.+?)(?=\n-|\n[A-Z]|$)', match)
            if name_match:
                segment["name"] = name_match.group(1).strip()

            desc_match = re.search(r'Description[:\s]+(.+?)(?=\n-|\n[A-Z]|$)', match, re.DOTALL)
            if desc_match:
                segment["description"] = desc_match.group(1).strip()

            sources_match = re.search(r'Data Sources?[:\s]+(.+?)(?=\n-|\nFields|$)', match, re.DOTALL)
            if sources_match:
                sources_text = sources_match.group(1)
                segment["data_sources"] = [s.strip() for s in re.split(r'[+,\[\]]', sources_text) if s.strip()]

            fields_match = re.search(r'Fields?[:\s]+(.+?)(?=\n-|\nConfidence|$)', match, re.DOTALL)
            if fields_match:
                fields_text = fields_match.group(1)
                segment["fields"] = [f.strip() for f in re.split(r'[,\[\]]', fields_text) if f.strip()]

            conf_match = re.search(r'Confidence[:\s]+(HIGH|MEDIUM|LOW)', match, re.IGNORECASE)
            if conf_match:
                segment["confidence"] = conf_match.group(1).upper()

            type_match = re.search(r'Message Type[:\s]+(PQS|PVP)', match, re.IGNORECASE)
            if type_match:
                segment["message_type"] = type_match.group(1).upper()

            # Check Texada criteria
            texada_match = re.search(r'Texada[:\s]+(.+?)(?=\n-|\nMessage|$)', match, re.DOTALL)
            if texada_match:
                texada_text = texada_match.group(1).lower()
                segment["texada_check"]["hyper_specific"] = "pass" in texada_text.split("hyper")[0] if "hyper" in texada_text else False
                segment["texada_check"]["factually_grounded"] = "pass" in texada_text
                segment["texada_check"]["non_obvious"] = "pass" in texada_text

            if segment["name"]:
                segments.append(segment)

        return segments

    def _format_data_landscape(self, data_landscape: Dict) -> str:
        """Format data landscape for prompt."""
        lines = []

        for category, sources in data_landscape.items():
            if isinstance(sources, list) and sources:
                lines.append(f"\n{category.upper()}:")
                for source in sources:
                    if isinstance(source, dict):
                        name = source.get('name', 'Unknown')
                        feasibility = source.get('feasibility', 'UNKNOWN')
                        fields = source.get('fields', [])
                        lines.append(f"  - {name} ({feasibility} feasibility)")
                        if fields:
                            lines.append(f"    Fields: {', '.join(fields[:5])}")

        return "\n".join(lines) if lines else "Limited data sources available"
