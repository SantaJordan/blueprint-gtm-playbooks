"""
Database field catalog for Blueprint GTM.

Contains field names, URLs, and feasibility ratings for common government
and public data sources used in outreach.
"""

from typing import Dict, List, Optional


# Database catalog with field definitions
# Feasibility: HIGH = direct API, MEDIUM = scraping required, LOW = manual lookup
DATABASE_CATALOG = {
    # CMS (Centers for Medicare & Medicaid)
    "cms_care_compare": {
        "name": "CMS Care Compare",
        "url": "https://data.cms.gov/provider-data/",
        "api_available": True,
        "feasibility": "HIGH",
        "update_frequency": "Monthly",
        "fields": {
            "federal_provider_number": "Unique facility ID (6 chars)",
            "provider_name": "Facility legal name",
            "provider_address": "Street address",
            "provider_city": "City",
            "provider_state": "State (2-letter)",
            "provider_zip_code": "ZIP code",
            "overall_rating": "Star rating 1-5",
            "health_inspection_rating": "Health inspection star rating",
            "staffing_rating": "Staffing star rating",
            "quality_rating": "Quality measure star rating",
            "total_weighted_health_survey_score": "Aggregate health score",
            "number_of_facility_reported_incidents": "Incident count",
            "number_of_substantiated_complaints": "Complaint count",
            "deficiency_count": "Total deficiencies cited"
        },
        "example_query": "Nursing homes with < 3 star rating in {state}",
        "join_fields": ["federal_provider_number", "provider_name"]
    },

    "cms_pecos": {
        "name": "CMS PECOS (Provider Enrollment)",
        "url": "https://data.cms.gov/provider-characteristics/",
        "api_available": True,
        "feasibility": "HIGH",
        "update_frequency": "Monthly",
        "fields": {
            "npi": "National Provider Identifier",
            "pac_id": "Provider Associate Level Control ID",
            "enrollment_id": "Medicare enrollment ID",
            "provider_type": "Provider classification",
            "enrollment_date": "Date enrolled in Medicare",
            "revalidation_due_date": "Next revalidation deadline",
            "state": "Practice state"
        }
    },

    # EPA (Environmental Protection Agency)
    "epa_echo": {
        "name": "EPA ECHO (Enforcement & Compliance)",
        "url": "https://echo.epa.gov/",
        "api_available": True,
        "feasibility": "HIGH",
        "update_frequency": "Weekly",
        "fields": {
            "registry_id": "EPA facility registry ID",
            "fac_name": "Facility name",
            "fac_street": "Street address",
            "fac_city": "City",
            "fac_state": "State",
            "fac_zip": "ZIP code",
            "fac_naics": "NAICS industry code",
            "caa_evaluation_count": "Clean Air Act evaluations",
            "cwa_inspection_count": "Clean Water Act inspections",
            "rcra_evaluation_count": "RCRA evaluations",
            "tri_reporter": "TRI reporting facility (Y/N)",
            "qtrs_in_nc": "Quarters in non-compliance",
            "dfr_url": "Detailed Facility Report URL"
        },
        "example_query": "Facilities with > 4 quarters non-compliance in {city}"
    },

    "epa_tri": {
        "name": "EPA TRI (Toxics Release Inventory)",
        "url": "https://www.epa.gov/toxics-release-inventory-tri-program",
        "api_available": True,
        "feasibility": "HIGH",
        "update_frequency": "Annual",
        "fields": {
            "trifd": "TRI Facility ID",
            "facility_name": "Facility name",
            "chemical": "Chemical name",
            "cas_number": "CAS registry number",
            "total_releases": "Total pounds released",
            "onsite_release_total": "Onsite release total",
            "offsite_release_total": "Offsite release total",
            "reporting_year": "Report year"
        }
    },

    # OSHA (Occupational Safety & Health)
    "osha_inspections": {
        "name": "OSHA Inspection Data",
        "url": "https://www.osha.gov/ords/imis/inspection_detail",
        "api_available": True,
        "feasibility": "HIGH",
        "update_frequency": "Weekly",
        "fields": {
            "activity_nr": "Inspection activity number",
            "reporting_id": "Establishment ID",
            "estab_name": "Establishment name",
            "site_address": "Site address",
            "site_city": "City",
            "site_state": "State",
            "site_zip": "ZIP code",
            "naics_code": "NAICS code",
            "open_date": "Inspection open date",
            "close_case_date": "Case close date",
            "case_type": "Inspection type (Complaint, Referral, etc.)",
            "safety_hlth": "Safety or Health focus",
            "total_initial_penalty": "Initial penalty amount",
            "total_current_penalty": "Current penalty amount"
        },
        "example_query": "Inspections with penalty > $10,000 in {industry}"
    },

    # FMCSA (Federal Motor Carrier Safety)
    "fmcsa_safer": {
        "name": "FMCSA SAFER System",
        "url": "https://safer.fmcsa.dot.gov/",
        "api_available": True,
        "feasibility": "HIGH",
        "update_frequency": "Daily",
        "fields": {
            "dot_number": "DOT Number",
            "legal_name": "Legal name",
            "dba_name": "DBA name",
            "physical_address": "Physical address",
            "phone": "Phone number",
            "mcs_150_mileage_year": "MCS-150 mileage",
            "power_units": "Number of power units",
            "drivers": "Number of drivers",
            "carrier_operation": "Operation type",
            "oos_date": "Out of Service date",
            "oos_reason": "OOS reason",
            "safety_rating": "Safety rating",
            "safety_rating_date": "Rating date",
            "basic_percentile_vehicle": "BASIC score - vehicle",
            "basic_percentile_driver": "BASIC score - driver",
            "basic_percentile_hos": "BASIC score - HOS",
            "basic_percentile_drugs": "BASIC score - drugs/alcohol"
        },
        "example_query": "Carriers with safety rating downgrade in past 90 days"
    },

    # FDA (Food & Drug Administration)
    "fda_inspections": {
        "name": "FDA Inspection Database",
        "url": "https://www.fda.gov/inspections-compliance-enforcement",
        "api_available": False,
        "feasibility": "MEDIUM",
        "update_frequency": "Monthly",
        "fields": {
            "fei_number": "FDA Establishment Identifier",
            "legal_name": "Legal name",
            "inspection_date": "Inspection date",
            "inspection_type": "Inspection classification",
            "form_483_issued": "483 issued (Y/N)",
            "warning_letter": "Warning letter issued",
            "observations_count": "Number of 483 observations"
        }
    },

    "fda_warning_letters": {
        "name": "FDA Warning Letters Database",
        "url": "https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/compliance-actions-and-activities/warning-letters",
        "api_available": False,
        "feasibility": "MEDIUM",
        "update_frequency": "Weekly",
        "fields": {
            "company_name": "Company name",
            "subject": "Warning letter subject",
            "issue_date": "Issue date",
            "response_due_date": "Response deadline",
            "letter_url": "Full letter URL",
            "violations_cited": "Violation types cited"
        }
    },

    # NIPR (National Insurance Producer Registry)
    "nipr": {
        "name": "NIPR (Insurance Licensing)",
        "url": "https://www.nipr.com/",
        "api_available": True,
        "feasibility": "MEDIUM",
        "update_frequency": "Daily",
        "fields": {
            "npn": "National Producer Number",
            "agent_name": "Agent/agency name",
            "license_state": "State of license",
            "license_type": "License type",
            "license_status": "Active/Inactive",
            "expiration_date": "License expiration date",
            "appointment_count": "Number of carrier appointments",
            "ce_credits_required": "CE credits required",
            "ce_credits_completed": "CE credits completed"
        },
        "example_query": "Agents with licenses expiring in next 60 days"
    },

    # State-level restaurant inspections (generic template)
    "restaurant_inspections": {
        "name": "State/Local Restaurant Inspections",
        "url": "Varies by jurisdiction",
        "api_available": False,
        "feasibility": "MEDIUM",
        "update_frequency": "Weekly-Monthly",
        "fields": {
            "establishment_id": "Local establishment ID",
            "establishment_name": "Restaurant name",
            "address": "Street address",
            "inspection_date": "Date of inspection",
            "inspection_score": "Numeric score (varies by jurisdiction)",
            "grade": "Letter grade (A/B/C/F)",
            "critical_violations": "Number of critical violations",
            "noncritical_violations": "Number of non-critical violations",
            "permit_status": "Permit status",
            "permit_expiration": "Permit expiration date"
        },
        "regional_sources": {
            "new_york": "NYC Open Data - Restaurant Inspection Results",
            "los_angeles": "LA County Environmental Health",
            "florida": "FL DBPR Inspection Reports",
            "texas": "TX DSHS Food Establishment Inspections"
        }
    },

    # G2 Reviews (for tech/SaaS)
    "g2_reviews": {
        "name": "G2 Product Reviews",
        "url": "https://www.g2.com/",
        "api_available": False,
        "feasibility": "MEDIUM",
        "update_frequency": "Continuous",
        "fields": {
            "product_name": "Product being reviewed",
            "company_name": "Reviewer's company",
            "review_date": "Review date",
            "star_rating": "Overall star rating",
            "review_text": "Review content",
            "pros": "What user likes",
            "cons": "What user dislikes",
            "switching_from": "Previous solution",
            "industry": "Reviewer's industry",
            "company_size": "Company size bucket"
        },
        "example_query": "Companies switching from {competitor} in past 6 months"
    }
}


def get_database_fields(database_name: str) -> List[str]:
    """Get list of available fields for a database."""
    db_key = database_name.lower().replace(" ", "_").replace("-", "_")

    if db_key in DATABASE_CATALOG:
        return list(DATABASE_CATALOG[db_key].get("fields", {}).keys())

    # Partial match
    for key, data in DATABASE_CATALOG.items():
        if key in db_key or db_key in key:
            return list(data.get("fields", {}).keys())

    return []


def get_database_url(database_name: str) -> Optional[str]:
    """Get URL for a database."""
    db_key = database_name.lower().replace(" ", "_").replace("-", "_")

    if db_key in DATABASE_CATALOG:
        return DATABASE_CATALOG[db_key].get("url")

    # Partial match
    for key, data in DATABASE_CATALOG.items():
        if key in db_key or db_key in key:
            return data.get("url")

    return None


def get_database_info(database_name: str) -> Optional[Dict]:
    """Get full info for a database."""
    db_key = database_name.lower().replace(" ", "_").replace("-", "_")

    if db_key in DATABASE_CATALOG:
        return DATABASE_CATALOG[db_key]

    # Partial match
    for key, data in DATABASE_CATALOG.items():
        if key in db_key or db_key in key:
            return data

    return None


def get_high_feasibility_databases() -> List[str]:
    """Get list of databases with HIGH feasibility (direct API access)."""
    return [
        name for name, data in DATABASE_CATALOG.items()
        if data.get("feasibility") == "HIGH"
    ]
