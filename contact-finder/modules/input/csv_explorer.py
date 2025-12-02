"""
CSV Explorer - Dynamic field detection for any input CSV

Analyzes CSV structure without assumptions about column names,
maps to known field types, and creates a fetch plan for missing data.
"""

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


@dataclass
class FieldMapping:
    """Mapping of original column to normalized field type"""
    original_column: str
    field_type: str
    confidence: float  # 0-1, how confident in mapping
    sample_values: list[str] = field(default_factory=list)


@dataclass
class CSVAnalysis:
    """Result of CSV analysis"""
    file_path: str
    total_rows: int
    columns: list[str]

    # Field mappings
    field_mappings: dict[str, FieldMapping] = field(default_factory=dict)
    detected_fields: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)

    # Loaded companies (normalized)
    companies: list[dict] = field(default_factory=list)

    # Stats
    has_domain: float = 0.0  # % of rows with domain
    has_owner: float = 0.0   # % of rows with owner name
    has_address: float = 0.0 # % of rows with address
    has_phone: float = 0.0   # % of rows with phone


class CSVExplorer:
    """
    Dynamically analyze CSV structure and map to known field types.

    Doesn't assume any specific column names - uses pattern matching
    to detect what data is available.
    """

    # Field patterns - map normalized field type to possible column names
    FIELD_PATTERNS = {
        "company_name": [
            "name", "company", "business", "business_name", "company_name",
            "dba", "doing_business_as", "organization", "org", "title",
            "establishment", "store_name", "location_name"
        ],
        "domain": [
            "website", "url", "domain", "site", "web", "homepage",
            "website_url", "company_url", "site_url", "web_url"
        ],
        "address": [
            "address", "street", "location", "full_address", "street_address",
            "addr", "address_line", "address1"
        ],
        "city": [
            "city", "town", "municipality", "locality"
        ],
        "state": [
            "state", "province", "region", "state_province", "st"
        ],
        "zip": [
            "zip", "zipcode", "postal", "postal_code", "zip_code", "postcode"
        ],
        "country": [
            "country", "nation", "country_code"
        ],
        "phone": [
            "phone", "telephone", "tel", "contact_phone", "main_phone",
            "phone_number", "business_phone", "primary_phone"
        ],
        "owner": [
            "owner", "owner_name", "proprietor", "principal", "owner_full_name",
            "contact_name", "primary_contact"
        ],
        "owner_title": [
            "owner_title", "title", "position", "role"
        ],
        "email": [
            "email", "contact_email", "mail", "email_address", "e_mail"
        ],
        "vertical": [
            "category", "type", "vertical", "industry", "business_type",
            "sector", "classification", "niche"
        ],
        "linkedin_url": [
            "linkedin", "linkedin_url", "li_url", "linkedin_company_url"
        ],
        "facebook_url": [
            "facebook", "facebook_url", "fb", "fb_url"
        ],
        "rating": [
            "rating", "stars", "average_rating", "review_rating", "score"
        ],
        "reviews_count": [
            "reviews", "reviews_count", "review_count", "num_reviews", "total_reviews"
        ],
    }

    # Essential fields for SMB contact finding
    ESSENTIAL_FIELDS = ["company_name", "domain"]
    USEFUL_FIELDS = ["city", "state", "address", "phone", "vertical", "owner"]

    def __init__(self, sample_size: int = 100):
        self.sample_size = sample_size

    def _normalize_column_name(self, col: str) -> str:
        """Normalize column name for matching"""
        return re.sub(r'[^a-z0-9]', '', col.lower())

    def _detect_field_type(self, column: str, sample_values: list[str]) -> tuple[str | None, float]:
        """
        Detect field type from column name and sample values.

        Returns:
            (field_type, confidence) or (None, 0) if no match
        """
        normalized_col = self._normalize_column_name(column)

        # Try exact/partial column name matching first
        for field_type, patterns in self.FIELD_PATTERNS.items():
            for pattern in patterns:
                normalized_pattern = self._normalize_column_name(pattern)

                # Exact match
                if normalized_col == normalized_pattern:
                    return field_type, 1.0

                # Column contains pattern
                if normalized_pattern in normalized_col:
                    return field_type, 0.9

                # Pattern contains column (for short columns like "st" for state)
                if len(normalized_col) >= 2 and normalized_col in normalized_pattern:
                    return field_type, 0.7

        # Try value-based detection for common patterns
        non_empty_values = [v for v in sample_values if v and str(v).strip()]
        if non_empty_values:
            sample = non_empty_values[:10]

            # URL detection
            if all(self._looks_like_url(v) for v in sample):
                return "domain", 0.8

            # Email detection
            if all(self._looks_like_email(v) for v in sample):
                return "email", 0.9

            # Phone detection
            if all(self._looks_like_phone(v) for v in sample):
                return "phone", 0.8

            # ZIP code detection
            if all(self._looks_like_zip(v) for v in sample):
                return "zip", 0.8

            # State detection (2-letter codes)
            if all(len(str(v).strip()) == 2 and str(v).strip().isupper() for v in sample):
                return "state", 0.7

        return None, 0.0

    def _looks_like_url(self, value: str) -> bool:
        """Check if value looks like a URL"""
        v = str(value).strip().lower()
        return (
            v.startswith(('http://', 'https://', 'www.')) or
            ('.' in v and not '@' in v and len(v) > 5)
        )

    def _looks_like_email(self, value: str) -> bool:
        """Check if value looks like an email"""
        v = str(value).strip()
        return '@' in v and '.' in v.split('@')[-1]

    def _looks_like_phone(self, value: str) -> bool:
        """Check if value looks like a phone number"""
        v = re.sub(r'[^\d]', '', str(value))
        return len(v) >= 10 and len(v) <= 15

    def _looks_like_zip(self, value: str) -> bool:
        """Check if value looks like a ZIP code"""
        v = str(value).strip()
        return bool(re.match(r'^\d{5}(-\d{4})?$', v))

    def _extract_domain(self, value: str) -> str | None:
        """Extract domain from URL or return as-is if already a domain"""
        if not value:
            return None

        v = str(value).strip()

        # Already a domain?
        if not v.startswith('http') and '.' in v and '/' not in v:
            return v.lower().replace('www.', '')

        # Parse URL
        try:
            if not v.startswith('http'):
                v = 'https://' + v
            parsed = urlparse(v)
            domain = parsed.netloc.lower().replace('www.', '')
            return domain if domain else None
        except:
            return None

    def analyze(self, csv_path: str, limit: int | None = None) -> CSVAnalysis:
        """
        Analyze a CSV file and return structured analysis.

        Args:
            csv_path: Path to CSV file
            limit: Optional limit on rows to load

        Returns:
            CSVAnalysis with field mappings and loaded companies
        """
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV not found: {csv_path}")

        # Read CSV
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            # Try to detect delimiter
            sample = f.read(4096)
            f.seek(0)

            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
            except:
                dialect = csv.excel

            reader = csv.DictReader(f, dialect=dialect)
            columns = reader.fieldnames or []
            rows = list(reader)

        total_rows = len(rows)

        # Sample values for each column
        sample_values = {col: [] for col in columns}
        for row in rows[:self.sample_size]:
            for col in columns:
                val = row.get(col, '').strip()
                if val:
                    sample_values[col].append(val)

        # Detect field types
        field_mappings = {}
        detected_fields = []
        used_types = set()

        for col in columns:
            field_type, confidence = self._detect_field_type(col, sample_values[col])

            # Only use each type once (pick highest confidence)
            if field_type and field_type not in used_types:
                field_mappings[field_type] = FieldMapping(
                    original_column=col,
                    field_type=field_type,
                    confidence=confidence,
                    sample_values=sample_values[col][:5]
                )
                detected_fields.append(field_type)
                used_types.add(field_type)

        # Determine missing essential fields
        missing_fields = [f for f in self.ESSENTIAL_FIELDS if f not in detected_fields]

        # Load and normalize companies
        companies = []
        rows_to_load = rows[:limit] if limit else rows

        stats = {"domain": 0, "owner": 0, "address": 0, "phone": 0}

        for row in rows_to_load:
            company = {}

            # Map each detected field
            for field_type, mapping in field_mappings.items():
                value = row.get(mapping.original_column, '').strip()

                if field_type == "domain" and value:
                    value = self._extract_domain(value)

                if value:
                    company[field_type] = value

            # Track stats
            if company.get("domain"):
                stats["domain"] += 1
            if company.get("owner"):
                stats["owner"] += 1
            if company.get("address") or company.get("city"):
                stats["address"] += 1
            if company.get("phone"):
                stats["phone"] += 1

            # Only include if we have company name
            if company.get("company_name"):
                companies.append(company)

        num_companies = len(companies) or 1

        return CSVAnalysis(
            file_path=csv_path,
            total_rows=total_rows,
            columns=columns,
            field_mappings=field_mappings,
            detected_fields=detected_fields,
            missing_fields=missing_fields,
            companies=companies,
            has_domain=stats["domain"] / num_companies,
            has_owner=stats["owner"] / num_companies,
            has_address=stats["address"] / num_companies,
            has_phone=stats["phone"] / num_companies
        )

    def analyze_json(self, json_path: str, limit: int | None = None) -> CSVAnalysis:
        """
        Analyze a JSON file with same logic as CSV.

        Expects JSON to be an array of objects.
        """
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"JSON not found: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("JSON must be an array of objects")

        if not data:
            return CSVAnalysis(
                file_path=json_path,
                total_rows=0,
                columns=[],
                companies=[]
            )

        # Get columns from first row
        columns = list(data[0].keys())
        rows = data
        total_rows = len(rows)

        # Sample values for each column
        sample_values = {col: [] for col in columns}
        for row in rows[:self.sample_size]:
            for col in columns:
                val = str(row.get(col, '')).strip()
                if val:
                    sample_values[col].append(val)

        # Detect field types (same logic as CSV)
        field_mappings = {}
        detected_fields = []
        used_types = set()

        for col in columns:
            field_type, confidence = self._detect_field_type(col, sample_values[col])

            if field_type and field_type not in used_types:
                field_mappings[field_type] = FieldMapping(
                    original_column=col,
                    field_type=field_type,
                    confidence=confidence,
                    sample_values=sample_values[col][:5]
                )
                detected_fields.append(field_type)
                used_types.add(field_type)

        missing_fields = [f for f in self.ESSENTIAL_FIELDS if f not in detected_fields]

        # Load and normalize companies
        companies = []
        rows_to_load = rows[:limit] if limit else rows

        stats = {"domain": 0, "owner": 0, "address": 0, "phone": 0}

        for row in rows_to_load:
            company = {}

            for field_type, mapping in field_mappings.items():
                value = str(row.get(mapping.original_column, '')).strip()

                if field_type == "domain" and value:
                    value = self._extract_domain(value)

                if value:
                    company[field_type] = value

            if company.get("domain"):
                stats["domain"] += 1
            if company.get("owner"):
                stats["owner"] += 1
            if company.get("address") or company.get("city"):
                stats["address"] += 1
            if company.get("phone"):
                stats["phone"] += 1

            if company.get("company_name"):
                companies.append(company)

        num_companies = len(companies) or 1

        return CSVAnalysis(
            file_path=json_path,
            total_rows=total_rows,
            columns=columns,
            field_mappings=field_mappings,
            detected_fields=detected_fields,
            missing_fields=missing_fields,
            companies=companies,
            has_domain=stats["domain"] / num_companies,
            has_owner=stats["owner"] / num_companies,
            has_address=stats["address"] / num_companies,
            has_phone=stats["phone"] / num_companies
        )

    def print_analysis(self, analysis: CSVAnalysis):
        """Print a summary of the analysis"""
        print(f"\n{'='*60}")
        print(f"CSV Analysis: {analysis.file_path}")
        print(f"{'='*60}")
        print(f"Total rows: {analysis.total_rows}")
        print(f"Companies loaded: {len(analysis.companies)}")
        print()

        print("Detected Fields:")
        for field_type, mapping in analysis.field_mappings.items():
            print(f"  {field_type:15} <- '{mapping.original_column}' (conf: {mapping.confidence:.1%})")
            if mapping.sample_values:
                print(f"                   Sample: {mapping.sample_values[:2]}")

        print()
        print("Data Coverage:")
        print(f"  Domain:  {analysis.has_domain:.1%}")
        print(f"  Owner:   {analysis.has_owner:.1%}")
        print(f"  Address: {analysis.has_address:.1%}")
        print(f"  Phone:   {analysis.has_phone:.1%}")

        if analysis.missing_fields:
            print()
            print(f"Missing Essential Fields: {analysis.missing_fields}")
            print("These will be filled using Serper queries")

        print(f"{'='*60}\n")


# CLI test
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python csv_explorer.py <csv_file>")
        sys.exit(1)

    explorer = CSVExplorer()
    analysis = explorer.analyze(sys.argv[1], limit=100)
    explorer.print_analysis(analysis)
