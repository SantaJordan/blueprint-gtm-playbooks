#!/usr/bin/env python3
"""
Prepare SMB Sample from Archive 4.zip

Extracts 7 SMB vertical CSVs, filters for companies with websites,
and creates a stratified sample for pipeline testing.

Usage:
    python -m evaluation.scripts.prepare_smb_sample \
        --archive "Archive 4.zip" \
        --sample-per-vertical 200 \
        --output evaluation/data/smb_sample_1400.json
"""

import argparse
import csv
import json
import random
import re
import sys
import tempfile
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class SMBCompany:
    """A company from the Archive 4 data"""
    company_name: str
    domain: str
    vertical: str
    address: str | None = None
    phone: str | None = None
    place_id: str | None = None
    rating: float | None = None
    reviews: int | None = None


def extract_domain(website: str | None) -> str | None:
    """Extract clean domain from website URL"""
    if not website:
        return None

    website = website.strip()
    if not website:
        return None

    # Add scheme if missing
    if not website.startswith(('http://', 'https://')):
        website = 'https://' + website

    try:
        parsed = urlparse(website)
        domain = parsed.netloc or parsed.path.split('/')[0]

        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]

        # Basic validation
        if '.' not in domain or len(domain) < 4:
            return None

        return domain.lower()
    except Exception:
        return None


def clean_vertical_name(filename: str) -> str:
    """Convert filename to clean vertical name"""
    # Remove -overview.csv suffix
    name = re.sub(r'-overview\.csv$', '', filename, flags=re.IGNORECASE)
    name = re.sub(r'\. Over View\.csv$', '', name, flags=re.IGNORECASE)
    # Clean up
    name = name.strip().lower().replace(' ', '_').replace('&', 'and')
    # Remove special chars
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name


def load_companies_from_csv(
    csv_content: str,
    vertical: str,
    max_per_vertical: int | None = None
) -> list[SMBCompany]:
    """Load companies from CSV content, filtering for those with websites"""
    companies = []

    # Parse CSV
    reader = csv.DictReader(csv_content.splitlines())

    for row in reader:
        # Get website and extract domain
        website = row.get('website', '').strip()
        domain = extract_domain(website)

        if not domain:
            continue  # Skip companies without websites

        # Get company name
        name = row.get('name', '').strip()
        if not name:
            continue

        # Parse rating
        rating = None
        try:
            rating = float(row.get('rating', ''))
        except (ValueError, TypeError):
            pass

        # Parse reviews
        reviews = None
        try:
            reviews = int(row.get('reviews', ''))
        except (ValueError, TypeError):
            pass

        companies.append(SMBCompany(
            company_name=name,
            domain=domain,
            vertical=vertical,
            address=row.get('address', '').strip() or None,
            phone=row.get('phone', '').strip() or None,
            place_id=row.get('place_id', '').strip() or None,
            rating=rating,
            reviews=reviews,
        ))

    # Random sample if needed
    if max_per_vertical and len(companies) > max_per_vertical:
        companies = random.sample(companies, max_per_vertical)

    return companies


def process_archive(
    archive_path: str,
    sample_per_vertical: int,
    seed: int = 42
) -> dict[str, list[SMBCompany]]:
    """Process Archive 4.zip and extract samples from each vertical"""
    random.seed(seed)

    results = {}

    with zipfile.ZipFile(archive_path, 'r') as zf:
        # List all CSV files (excluding __MACOSX)
        csv_files = [
            name for name in zf.namelist()
            if name.endswith('.csv') and not name.startswith('__MACOSX')
        ]

        print(f"Found {len(csv_files)} CSV files in archive")

        for csv_file in csv_files:
            vertical = clean_vertical_name(Path(csv_file).name)
            print(f"\nProcessing: {csv_file}")
            print(f"  Vertical: {vertical}")

            # Read CSV content
            with zf.open(csv_file) as f:
                content = f.read().decode('utf-8', errors='ignore')

            # Load and sample companies
            companies = load_companies_from_csv(
                content,
                vertical,
                max_per_vertical=sample_per_vertical
            )

            print(f"  Companies with websites: {len(companies)}")
            results[vertical] = companies

    return results


def main():
    parser = argparse.ArgumentParser(description="Prepare SMB sample from Archive 4.zip")
    parser.add_argument(
        "--archive",
        required=True,
        help="Path to Archive 4.zip"
    )
    parser.add_argument(
        "--sample-per-vertical",
        type=int,
        default=200,
        help="Number of companies to sample per vertical (default: 200)"
    )
    parser.add_argument(
        "--output",
        default="evaluation/data/smb_sample_1400.json",
        help="Output JSON file path"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )

    args = parser.parse_args()

    # Verify archive exists
    if not Path(args.archive).exists():
        print(f"Error: Archive not found: {args.archive}")
        sys.exit(1)

    print(f"Processing archive: {args.archive}")
    print(f"Sample per vertical: {args.sample_per_vertical}")
    print(f"Random seed: {args.seed}")

    # Process archive
    by_vertical = process_archive(
        args.archive,
        sample_per_vertical=args.sample_per_vertical,
        seed=args.seed
    )

    # Flatten and shuffle
    all_companies = []
    for vertical, companies in by_vertical.items():
        all_companies.extend(companies)

    random.shuffle(all_companies)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for vertical, companies in sorted(by_vertical.items()):
        print(f"  {vertical}: {len(companies)} companies")

    print(f"\nTotal companies: {len(all_companies)}")

    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save JSON
    output_data = [asdict(c) for c in all_companies]
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nSaved to: {output_path}")

    # Also save summary CSV
    csv_path = output_path.with_suffix('.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'company_name', 'domain', 'vertical', 'address', 'phone'
        ])
        writer.writeheader()
        for company in all_companies:
            writer.writerow({
                'company_name': company.company_name,
                'domain': company.domain,
                'vertical': company.vertical,
                'address': company.address or '',
                'phone': company.phone or '',
            })
    print(f"Saved CSV: {csv_path}")


if __name__ == "__main__":
    main()
