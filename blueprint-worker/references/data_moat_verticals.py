"""
Pre-scored verticals and niche conversions for rapid qualification.

These scores are based on the Blueprint GTM methodology:
- Higher scores = stronger data moats (harder to replicate)
- Regulatory verticals score highest due to public, structured data
"""

from typing import Dict, List, Optional, Tuple


# Pre-scored verticals (out of 40 points)
# Scoring criteria:
# - 10pts: Public database availability
# - 10pts: Structured data (APIs, machine-readable)
# - 10pts: Company-specific identifiers
# - 10pts: Temporal signals (deadlines, expirations, cycles)
TIER_1_VERTICALS = {
    # Healthcare / Regulatory (35-40 points)
    "nursing_homes": {
        "score": 38,
        "databases": ["CMS Care Compare", "State Health Dept Surveys"],
        "signals": ["deficiency citations", "staffing levels", "quality scores"],
        "niche": "Skilled Nursing Facilities"
    },
    "trucking": {
        "score": 40,
        "databases": ["FMCSA SAFER", "DOT Crash Data"],
        "signals": ["safety violations", "out-of-service orders", "crash history"],
        "niche": "Commercial Motor Carriers"
    },
    "pharmacies": {
        "score": 36,
        "databases": ["State Board of Pharmacy", "DEA Registrations"],
        "signals": ["license expirations", "disciplinary actions", "registration status"],
        "niche": "Licensed Pharmacies"
    },
    "medical_practices": {
        "score": 35,
        "databases": ["State Medical Boards", "CMS PECOS"],
        "signals": ["license renewals", "Medicare enrollment", "specialty certifications"],
        "niche": "Physician Practices"
    },

    # Environmental / Industrial (30-37 points)
    "manufacturing_epa": {
        "score": 37,
        "databases": ["EPA ECHO", "TRI Database"],
        "signals": ["permit violations", "inspection failures", "emission reports"],
        "niche": "EPA-Regulated Manufacturers"
    },
    "construction_osha": {
        "score": 34,
        "databases": ["OSHA Inspections", "OSHA Citations"],
        "signals": ["safety citations", "penalty amounts", "repeat violations"],
        "niche": "Construction Companies (OSHA-tracked)"
    },
    "food_manufacturing": {
        "score": 35,
        "databases": ["FDA Inspections", "FDA Warning Letters"],
        "signals": ["483 observations", "warning letters", "recall notices"],
        "niche": "FDA-Regulated Food Manufacturers"
    },

    # Food Service / Hospitality (25-32 points)
    "restaurants": {
        "score": 32,
        "databases": ["Local Health Dept", "Yelp/Google Reviews"],
        "signals": ["inspection scores", "critical violations", "review sentiment"],
        "niche": "Full-Service Restaurants"
    },
    "hotels": {
        "score": 28,
        "databases": ["Local Fire Dept", "Health Inspections", "TripAdvisor"],
        "signals": ["fire safety violations", "health scores", "guest complaints"],
        "niche": "Hospitality Properties"
    },

    # Financial / Insurance (20-28 points)
    "insurance_agencies": {
        "score": 30,
        "databases": ["NIPR", "State Insurance Dept"],
        "signals": ["license expirations", "appointments", "continuing education"],
        "niche": "Licensed Insurance Agencies"
    },
    "mortgage_lenders": {
        "score": 26,
        "databases": ["NMLS", "CFPB Complaints"],
        "signals": ["license status", "consumer complaints", "branch locations"],
        "niche": "Mortgage Lending Companies"
    },

    # Low data moat (< 20 points)
    "generic_saas": {
        "score": 12,
        "databases": ["LinkedIn", "Crunchbase"],
        "signals": ["funding rounds", "job postings", "company size"],
        "niche": None  # Cannot convert - too generic
    },
    "generic_b2b": {
        "score": 10,
        "databases": ["LinkedIn", "Company Website"],
        "signals": ["growth signals", "hiring patterns"],
        "niche": None  # Cannot convert - too generic
    }
}


# Niche conversion mappings
# Maps generic verticals to specific regulated niches
NICHE_CONVERSIONS = {
    # Generic -> Specific regulated niche
    "healthcare": ["nursing_homes", "medical_practices", "pharmacies"],
    "transportation": ["trucking"],
    "manufacturing": ["manufacturing_epa", "food_manufacturing"],
    "construction": ["construction_osha"],
    "food_service": ["restaurants", "food_manufacturing"],
    "hospitality": ["hotels", "restaurants"],
    "financial_services": ["insurance_agencies", "mortgage_lenders"],

    # Already specific - no conversion needed
    "skilled_nursing": ["nursing_homes"],
    "trucking": ["trucking"],
    "pharmacy": ["pharmacies"],
    "restaurants": ["restaurants"],
}


def get_vertical_score(vertical: str) -> int:
    """Get the data moat score for a vertical (0-40)."""
    vertical_lower = vertical.lower().replace(" ", "_").replace("-", "_")

    # Direct match
    if vertical_lower in TIER_1_VERTICALS:
        return TIER_1_VERTICALS[vertical_lower]["score"]

    # Partial match
    for key, data in TIER_1_VERTICALS.items():
        if key in vertical_lower or vertical_lower in key:
            return data["score"]

    # Unknown vertical - assume low score
    return 15


def convert_to_niche(generic_vertical: str) -> List[str]:
    """
    Convert a generic vertical to specific regulated niches.

    Returns list of niche names that have strong data moats.
    """
    vertical_lower = generic_vertical.lower().replace(" ", "_").replace("-", "_")

    # Check conversions
    if vertical_lower in NICHE_CONVERSIONS:
        return NICHE_CONVERSIONS[vertical_lower]

    # Check if already a specific niche
    for niche_list in NICHE_CONVERSIONS.values():
        if vertical_lower in niche_list:
            return [vertical_lower]

    return []  # No conversion available


def get_vertical_info(vertical: str) -> Optional[Dict]:
    """Get full info for a vertical including databases and signals."""
    vertical_lower = vertical.lower().replace(" ", "_").replace("-", "_")

    if vertical_lower in TIER_1_VERTICALS:
        return TIER_1_VERTICALS[vertical_lower]

    # Partial match
    for key, data in TIER_1_VERTICALS.items():
        if key in vertical_lower or vertical_lower in key:
            return data

    return None
