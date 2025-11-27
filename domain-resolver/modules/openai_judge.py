"""
OpenAI GPT-4o-mini Judge for domain validation
Replaces local Ollama with cloud-based validation for better accuracy
"""
import json
import logging
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

try:
    from openai import AsyncOpenAI
except ImportError:
    raise ImportError("Please install openai: pip install openai")


class OpenAIJudge:
    """GPT-4o-mini validation for domain matching"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", timeout: int = 30):
        """
        Initialize OpenAI client

        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4o-mini)
            timeout: Request timeout in seconds
        """
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)
        self.model = model
        self.timeout = timeout

    async def judge_match(self, company_data: Dict[str, Any],
                         url: str, webpage_text: str) -> Dict[str, Any]:
        """
        Use GPT-4o-mini to judge if webpage matches company

        Args:
            company_data: Dict with name, city, phone, address, etc.
            url: Candidate URL
            webpage_text: Extracted webpage text (full content - GPT-4o-mini has 128K context)

        Returns:
            {
                'match': bool,
                'confidence': int,  # 0-100
                'evidence': str,
                'reasoning': str,
                'phone_found': bool,
                'address_found': bool,
                'name_found': bool,
                'is_parent_company': bool,
                'is_directory_site': bool,
                'is_government_oversight_site': bool,
                'is_government_portal': bool,
                'needs_deep_link': bool,
                'suggested_deep_link_search': str
            }
        """
        # Build structured prompt with full content
        prompt = self._build_prompt(company_data, url, webpage_text)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a domain validation expert. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for consistent output
                max_tokens=500
            )

            llm_response = response.choices[0].message.content

            # Parse JSON response
            parsed = self._parse_llm_response(llm_response)

            # Log token usage for cost tracking
            if response.usage:
                logger.debug(f"OpenAI tokens - input: {response.usage.prompt_tokens}, "
                           f"output: {response.usage.completion_tokens}")

            logger.debug(f"OpenAI judgment for {url}: match={parsed.get('match')}, "
                        f"confidence={parsed.get('confidence')}")

            return parsed

        except Exception as e:
            logger.error(f"OpenAI API error for {company_data.get('name')}: {e}")
            return self._fallback_response(str(e))

    def _build_prompt(self, company_data: Dict[str, Any], url: str, text: str) -> str:
        """Build structured prompt for LLM with full website content"""

        company_name = company_data.get('name', 'Unknown')
        city = company_data.get('city', '')
        phone = company_data.get('phone', '')
        address = company_data.get('address', '')
        context = company_data.get('context', '')

        prompt = f"""You are validating if a website belongs to a specific company or facility.

**COMPANY INFORMATION:**
- Name: {company_name}
- City: {city if city else 'Unknown'}
- Phone: {phone if phone else 'Unknown'}
- Address: {address if address else 'Unknown'}
- Context: {context if context else 'N/A'}

**CANDIDATE WEBSITE URL:** {url}

**FULL WEBSITE CONTENT:**
{text}

**VALIDATION TASK:**
Determine if this website is the OFFICIAL website for the specified company/facility.

**CRITICAL: Base your decision ONLY on evidence observed in the website content above.**

**RED FLAGS - Instant Rejection:**

1. **Government Oversight/Registry Sites** - ALWAYS REJECT:
   - Sites ending in .gov that provide oversight, funding, or registry services
   - Common patterns: hrsa.gov, hhs.gov, cms.gov, medicare.gov, state health dept sites
   - Look for: "Find a Health Center", "Grantee Directory", "Provider Lookup"
   - These LIST organizations but are NOT the organization's own website

2. **Directory/Listing Sites** - REJECT:
   - Sites like Medicare.gov, US News, Caring.com that list/rank multiple facilities
   - Pattern: "Search facilities", "View all locations", "Browse by state"

3. **Parent Company Sites** - FLAG but may match:
   - Corporate sites managing multiple locations
   - Look for: "Our Locations", "Find a Facility", multiple addresses listed

4. **Healthcare Associations** - REJECT:
   - Industry organizations (AHCA, LeadingAge, etc.) vs actual facilities

5. **State/County Government Portals** - CHECK for deep links:
   - If URL is just root domain without specific path → needs_deep_link=true

**VALIDATION SIGNALS (check each):**
1. **Phone number match** - Does the website show the company's phone number (exact or last 4-7 digits)?
2. **Single Location** - Does the site represent ONE facility or MULTIPLE facilities?
3. **Address/City match** - Does the website mention THIS specific city/address?
4. **Company name match** - Does the site prominently display THIS company name as its OWN identity?
5. **Ownership signal** - "Welcome to [Company]" (ownership) vs "Information about [Company]" (listing)
6. **Context match** - Does the content align with the company's industry?

**Return ONLY valid JSON:**
{{
  "match": true or false,
  "confidence": 0-100,
  "evidence": "specific quotes/evidence from website content supporting your decision",
  "phone_found": true or false,
  "address_found": true or false,
  "name_found": true or false,
  "is_parent_company": true or false,
  "is_directory_site": true or false,
  "is_government_oversight_site": true or false,
  "is_government_portal": true or false,
  "needs_deep_link": true or false,
  "suggested_deep_link_search": "search query if needs_deep_link is true, else empty string"
}}

**Confidence Guidelines:**
- 90-100: Phone + address + name all match, single location, clear ownership
- 70-89: Strong match but missing one signal (e.g., no phone but name + address match)
- 50-69: Partial match, some uncertainty (parent company with matching subsidiary)
- 30-49: Weak match, significant uncertainty
- 0-29: No match or directory/government site"""

        return prompt

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""

        try:
            # Try direct JSON parse
            parsed = json.loads(response_text)

            # Validate and normalize required fields
            return {
                'match': bool(parsed.get('match', False)),
                'confidence': int(parsed.get('confidence', 0)),
                'evidence': str(parsed.get('evidence', '')),
                'reasoning': str(parsed.get('evidence', '')),  # Alias for compatibility
                'phone_found': bool(parsed.get('phone_found', False)),
                'address_found': bool(parsed.get('address_found', False)),
                'name_found': bool(parsed.get('name_found', False)),
                'is_parent_company': bool(parsed.get('is_parent_company', False)),
                'is_directory_site': bool(parsed.get('is_directory_site', False)),
                'is_government_oversight_site': bool(parsed.get('is_government_oversight_site', False)),
                'is_government_portal': bool(parsed.get('is_government_portal', False)),
                'needs_deep_link': bool(parsed.get('needs_deep_link', False)),
                'suggested_deep_link_search': str(parsed.get('suggested_deep_link_search', ''))
            }

        except json.JSONDecodeError:
            logger.warning(f"Failed to parse OpenAI JSON response: {response_text[:200]}")
            # Fallback: try to extract values using regex
            return self._extract_with_regex(response_text)

    def _extract_with_regex(self, text: str) -> Dict[str, Any]:
        """Extract values from malformed JSON using regex as fallback"""

        # Try to find match: true/false
        match_search = re.search(r'"match"\s*:\s*(true|false)', text, re.IGNORECASE)
        match = match_search.group(1).lower() == 'true' if match_search else False

        # Try to find confidence: 0-100
        confidence_search = re.search(r'"confidence"\s*:\s*(\d+)', text)
        confidence = int(confidence_search.group(1)) if confidence_search else 50

        # Try to find evidence
        evidence_search = re.search(r'"evidence"\s*:\s*"([^"]+)"', text)
        evidence = evidence_search.group(1) if evidence_search else "Unable to parse LLM response"

        # Try to find boolean fields
        def extract_bool(field_name: str) -> bool:
            search = re.search(rf'"{field_name}"\s*:\s*(true|false)', text, re.IGNORECASE)
            return search.group(1).lower() == 'true' if search else False

        return {
            'match': match,
            'confidence': min(max(confidence, 0), 100),
            'evidence': evidence,
            'reasoning': evidence,
            'phone_found': extract_bool('phone_found'),
            'address_found': extract_bool('address_found'),
            'name_found': extract_bool('name_found'),
            'is_parent_company': extract_bool('is_parent_company'),
            'is_directory_site': extract_bool('is_directory_site'),
            'is_government_oversight_site': extract_bool('is_government_oversight_site'),
            'is_government_portal': extract_bool('is_government_portal'),
            'needs_deep_link': extract_bool('needs_deep_link'),
            'suggested_deep_link_search': ''
        }

    def _fallback_response(self, error_msg: str = '') -> Dict[str, Any]:
        """Return fallback response on error"""
        return {
            'match': False,
            'confidence': 0,
            'evidence': f'OpenAI API call failed: {error_msg}' if error_msg else 'OpenAI API call failed',
            'reasoning': 'OpenAI unavailable or error',
            'phone_found': False,
            'address_found': False,
            'name_found': False,
            'is_parent_company': False,
            'is_directory_site': False,
            'is_government_oversight_site': False,
            'is_government_portal': False,
            'needs_deep_link': False,
            'suggested_deep_link_search': ''
        }


async def verify_with_openai(company_data: Dict[str, Any], url: str,
                             webpage_text: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to verify a domain match using OpenAI GPT-4o-mini

    Args:
        company_data: Company information
        url: Candidate URL
        webpage_text: Full webpage text content
        config: Configuration dict

    Returns:
        OpenAI judgment result
    """
    llm_config = config.get('llm', {})

    judge = OpenAIJudge(
        api_key=llm_config.get('openai_api_key', ''),
        model=llm_config.get('model', 'gpt-4o-mini'),
        timeout=llm_config.get('timeout', 30)
    )

    return await judge.judge_match(company_data, url, webpage_text)
