"""
Wave 2: Multi-Modal Data Landscape Scan

Executes parallel searches across 4 data categories:
- Government/Regulatory
- Competitive Intelligence
- Velocity Signals
- Tech/Operational
"""
import asyncio
from typing import Dict, List
import re


class Wave2DataLandscape:
    """Wave 2: Map available data sources for the target niche."""

    # Search templates by category - SPECIFIC API and field discovery
    GOVERNMENT_SEARCHES = [
        "site:data.cms.gov {industry} provider data API fields",
        "site:osha.gov {industry} inspection data download CSV",
        "site:epa.gov ECHO database {industry} violation records API",
        "{industry} state licensing board public lookup API",
        "site:sam.gov {industry} federal contracts API documentation",
        "site:usaspending.gov {industry} NAICS award data API",
        "{industry} permit database bulk download field schema",
        "FDA {industry} inspection database API 483 warning letters",
        "{industry} Medicare provider enrollment data CMS PECOS",
    ]

    COMPETITIVE_SEARCHES = [
        "site:g2.com API {industry} product reviews data export",
        "site:capterra.com {industry} reviews data feed",
        "site:trustradius.com {industry} vendor comparison API",
        "{industry} market share data API firmographics",
        "{industry} pricing intelligence API competitor tracking",
    ]

    VELOCITY_SEARCHES = [
        "Google Places API review_count rating fields documentation",
        "Yelp Fusion API {industry} business reviews endpoint",
        "{industry} job posting API Indeed Greenhouse Lever",
        "LinkedIn job postings API {industry} hiring signals",
        "Crunchbase API {industry} funding rounds headcount",
    ]

    TECH_SEARCHES = [
        "BuiltWith API technology lookup {industry} pricing",
        "Wappalyzer API tech stack detection fields",
        "SimilarWeb API {industry} website traffic data",
        "site:hunter.io API email pattern company domain",
        "{industry} technographics data Apollo ZoomInfo API",
    ]

    def __init__(self, claude_client, web_search):
        self.claude = claude_client
        self.web_search = web_search

    async def execute(self, niche: Dict, company_context: Dict) -> Dict:
        """
        Execute Wave 2 data landscape scan.

        Args:
            niche: Qualified niche from Wave 1.5
            company_context: Context from Wave 1

        Returns:
            {
                "government": [
                    {
                        "name": str,
                        "url": str,
                        "fields": [str],
                        "feasibility": "HIGH" | "MEDIUM" | "LOW",
                        "update_frequency": str,
                        "cost": str
                    }
                ],
                "competitive": [...],
                "velocity": [...],
                "tech": [...]
            }
        """
        industry = niche.get("niche", company_context.get("industries_served", ["business"])[0] if company_context.get("industries_served") else "business")

        # Build all search queries
        all_searches = []
        search_categories = []

        for template in self.GOVERNMENT_SEARCHES:
            all_searches.append(template.format(industry=industry))
            search_categories.append("government")

        for template in self.COMPETITIVE_SEARCHES:
            all_searches.append(template.format(industry=industry))
            search_categories.append("competitive")

        for template in self.VELOCITY_SEARCHES:
            all_searches.append(template.format(industry=industry))
            search_categories.append("velocity")

        for template in self.TECH_SEARCHES:
            all_searches.append(template.format(industry=industry))
            search_categories.append("tech")

        # Execute all searches in parallel
        search_results = await self.web_search.search_parallel(all_searches)

        # Group results by category
        categorized_results = {
            "government": [],
            "competitive": [],
            "velocity": [],
            "tech": []
        }

        for i, result in enumerate(search_results):
            if result.get("success"):
                category = search_categories[i]
                categorized_results[category].append({
                    "query": all_searches[i],
                    "results": result.get("organic", [])[:5]
                })

        # Use Claude to evaluate and extract data sources
        data_landscape = await self._evaluate_sources(categorized_results, industry)

        return data_landscape

    async def _evaluate_sources(self, categorized_results: Dict, industry: str) -> Dict:
        """Use Claude to evaluate discovered data sources."""

        prompt = f"""Analyze these search results to identify SPECIFIC, ACTIONABLE data sources for {industry}.

SEARCH RESULTS BY CATEGORY:

GOVERNMENT/REGULATORY:
{self._format_category_results(categorized_results.get('government', []))}

COMPETITIVE INTELLIGENCE:
{self._format_category_results(categorized_results.get('competitive', []))}

VELOCITY SIGNALS:
{self._format_category_results(categorized_results.get('velocity', []))}

TECH/OPERATIONAL:
{self._format_category_results(categorized_results.get('tech', []))}

=== REQUIREMENTS ===

For each category, identify 2-4 data sources with EXACT technical details.

MANDATORY FOR EACH SOURCE:
1. EXACT database/API name (not "government databases")
2. ACTUAL URL (not "official website")
3. SPECIFIC field names (not "company information")
4. REALISTIC feasibility rating with justification

=== OUTPUT FORMAT ===

GOVERNMENT SOURCES:
1. NAME: [Exact database name, e.g., "CMS Provider Enrollment and Certification System (PECOS)"]
   URL: [Actual API/download URL, e.g., "https://data.cms.gov/provider-data/api/"]
   FIELDS: [Specific field names, e.g., "provider_npi, enrollment_date, specialty_code, sanctions_history"]
   FEASIBILITY: HIGH/MEDIUM/LOW
   FEASIBILITY_REASON: [Why this rating - e.g., "Free bulk download, updated monthly, documented schema"]
   FREQUENCY: [daily/weekly/monthly/quarterly]
   COST: [free/$X per 1000 calls/subscription $X/mo]
   TEXADA_VALUE: [What non-obvious insight can we extract?]

COMPETITIVE SOURCES:
1. NAME: [e.g., "G2 Product Reviews API"]
   URL: [e.g., "https://data.g2.com/api/v2/"]
   FIELDS: [e.g., "product_id, review_score, review_date, competitor_comparison, switching_reason"]
   FEASIBILITY: HIGH/MEDIUM/LOW
   FEASIBILITY_REASON: [justification]
   FREQUENCY: [update frequency]
   COST: [pricing]
   TEXADA_VALUE: [non-obvious insight]

VELOCITY SOURCES:
1. NAME: [e.g., "Google Places API"]
   URL: [e.g., "https://maps.googleapis.com/maps/api/place/"]
   FIELDS: [e.g., "place_id, rating, user_ratings_total, reviews[].time, reviews[].rating"]
   FEASIBILITY: HIGH/MEDIUM/LOW
   FEASIBILITY_REASON: [justification]
   FREQUENCY: [update frequency]
   COST: [pricing - e.g., "$0.017 per request"]
   TEXADA_VALUE: [e.g., "Review velocity = (reviews_this_month - reviews_last_month) indicates growth/decline"]

TECH SOURCES:
1. NAME: [e.g., "BuiltWith Technology Lookup API"]
   URL: [e.g., "https://api.builtwith.com/v21/api.json"]
   FIELDS: [e.g., "technologies[].name, technologies[].category, first_detected, last_detected"]
   FEASIBILITY: HIGH/MEDIUM/LOW
   FEASIBILITY_REASON: [justification]
   FREQUENCY: [update frequency]
   COST: [pricing]
   TEXADA_VALUE: [e.g., "Competitor tech stack changes indicate switching intent"]

=== FEASIBILITY DEFINITIONS ===
- HIGH: Free/cheap API, documented fields, daily/weekly updates, bulk access
- MEDIUM: Paid API ($50-500/mo), sparse docs, manual enrichment needed
- LOW: Enterprise pricing (>$1000/mo), no API, legal restrictions, stale data

=== QUALITY CHECK ===
REJECT sources that:
- Have no documented API or bulk download
- Require manual data entry
- Have update frequency >90 days
- Cost >$1000/month for basic access"""

        response = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_data_sources(response.content[0].text)

    def _parse_data_sources(self, text: str) -> Dict:
        """Parse Claude's response into structured data sources."""
        result = {
            "government": [],
            "competitive": [],
            "velocity": [],
            "tech": []
        }

        # Split by category
        category_patterns = {
            "government": r"GOVERNMENT SOURCES?:(.+?)(?=COMPETITIVE|VELOCITY|TECH|$)",
            "competitive": r"COMPETITIVE SOURCES?:(.+?)(?=GOVERNMENT|VELOCITY|TECH|$)",
            "velocity": r"VELOCITY SOURCES?:(.+?)(?=GOVERNMENT|COMPETITIVE|TECH|$)",
            "tech": r"TECH SOURCES?:(.+?)(?=GOVERNMENT|COMPETITIVE|VELOCITY|$)",
        }

        for category, pattern in category_patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                section = match.group(1)
                sources = self._parse_sources_section(section)
                result[category] = sources

        return result

    def _parse_sources_section(self, section: str) -> List[Dict]:
        """Parse individual sources from a section."""
        sources = []

        # Split by numbered items
        items = re.split(r'\n\d+\.', section)

        for item in items:
            if not item.strip():
                continue

            source = {
                "name": "",
                "url": "",
                "fields": [],
                "feasibility": "MEDIUM",
                "feasibility_reason": "",
                "update_frequency": "unknown",
                "cost": "unknown",
                "texada_value": ""
            }

            # Parse fields
            name_match = re.search(r"NAME:\s*(.+?)(?=\n|$)", item)
            if name_match:
                source["name"] = name_match.group(1).strip()

            url_match = re.search(r"URL:\s*(.+?)(?=\n|$)", item)
            if url_match:
                source["url"] = url_match.group(1).strip()

            fields_match = re.search(r"FIELDS?:\s*(.+?)(?=\n|$)", item)
            if fields_match:
                fields_text = fields_match.group(1)
                source["fields"] = [f.strip() for f in re.split(r'[,\[\]]', fields_text) if f.strip()]

            feasibility_match = re.search(r"FEASIBILITY:\s*(HIGH|MEDIUM|LOW)", item, re.IGNORECASE)
            if feasibility_match:
                source["feasibility"] = feasibility_match.group(1).upper()

            feasibility_reason_match = re.search(r"FEASIBILITY_REASON:\s*(.+?)(?=\n|$)", item)
            if feasibility_reason_match:
                source["feasibility_reason"] = feasibility_reason_match.group(1).strip()

            frequency_match = re.search(r"FREQUENCY:\s*(.+?)(?=\n|$)", item)
            if frequency_match:
                source["update_frequency"] = frequency_match.group(1).strip()

            cost_match = re.search(r"COST:\s*(.+?)(?=\n|$)", item)
            if cost_match:
                source["cost"] = cost_match.group(1).strip()

            texada_match = re.search(r"TEXADA_VALUE:\s*(.+?)(?=\n|$)", item)
            if texada_match:
                source["texada_value"] = texada_match.group(1).strip()

            if source["name"]:
                sources.append(source)

        return sources

    def _format_category_results(self, results: List[Dict]) -> str:
        """Format search results for a category."""
        lines = []
        for r in results:
            lines.append(f"Query: {r.get('query', 'Unknown')}")
            for item in r.get("results", []):
                lines.append(f"  - {item.get('title', '')}")
                lines.append(f"    {item.get('snippet', '')}")
        return "\n".join(lines) if lines else "No results found"
