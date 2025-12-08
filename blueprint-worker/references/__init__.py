"""
Reference data for Blueprint GTM worker.

Contains pre-scored verticals, niche conversions, and database field catalogs.
"""

from .data_moat_verticals import (
    TIER_1_VERTICALS,
    NICHE_CONVERSIONS,
    get_vertical_score,
    convert_to_niche
)

from .common_databases import (
    DATABASE_CATALOG,
    get_database_fields,
    get_database_url
)
