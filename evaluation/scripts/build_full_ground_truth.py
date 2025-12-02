#!/usr/bin/env python3
"""
Phase 2: Build Full Ground Truth Dataset

This script:
1. Loads all 1011 companies from existing ground truth
2. Enriches with Ocean.io (domains, LinkedIn URLs, employee counts, industries)
3. Classifies companies by size bucket and industry
4. Identifies Tier 1 candidates (hard cases, vertical SaaS SMBs)
5. Assigns cal/dev/validation/blind splits
6. Exports final ground truth datasets

Usage:
    python evaluation/scripts/build_full_ground_truth.py

Budget estimate: ~$150 for Ocean.io enrichment (1000 companies × $0.15)
"""

import asyncio
import aiohttp
import pandas as pd
import yaml
import sys
import random
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evaluation.harness.cache import EvaluationCache

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EnrichedCompany:
    """Company with enriched data"""
    # Original data
    name: str
    city: str | None = None
    state: str | None = None
    phone: str | None = None
    context: str | None = None

    # Ground truth domain
    expected_domain: str | None = None

    # Ocean.io enrichment
    ocean_domain: str | None = None
    linkedin_company_url: str | None = None
    employee_count: int | None = None
    ocean_industry: str | None = None
    revenue: str | None = None
    year_founded: int | None = None

    # Derived fields
    industry: str = "Unknown"
    size_bucket: str = "unknown"

    # Tier and status
    domain_tier: str = "silver"  # gold or silver
    verification_status: str = "pending"
    domain_match: bool = False  # Does Ocean domain match expected?
    notes: str = ""

    # Split assignment
    split: str = ""  # cal_dev, validation, blind


def classify_industry(context: str | None, ocean_industry: str | None) -> str:
    """Classify company into industry bucket"""
    # Prioritize Ocean.io industry if available
    if ocean_industry:
        oi = ocean_industry.lower()
        if any(x in oi for x in ["software", "saas", "technology", "computer"]):
            return "Vertical SaaS"
        if any(x in oi for x in ["healthcare", "medical", "hospital", "dental", "veterinary"]):
            return "Healthcare"
        if any(x in oi for x in ["restaurant", "food", "hospitality", "hotel"]):
            return "Restaurants/Hospitality"
        if any(x in oi for x in ["construction", "hvac", "plumbing", "electrical", "contractor"]):
            return "Local Services"
        if any(x in oi for x in ["consulting", "professional", "legal", "accounting", "law"]):
            return "Professional Services"
        if any(x in oi for x in ["manufacturing", "industrial", "wholesale"]):
            return "Manufacturing/B2B"

    # Fall back to context from test data
    if context:
        ctx = context.lower()
        if any(x in ctx for x in ["software", "saas", "tech", "platform"]):
            return "Vertical SaaS"
        if any(x in ctx for x in ["healthcare", "medical", "hospital", "dental", "vet"]):
            return "Healthcare"
        if any(x in ctx for x in ["restaurant", "food", "cafe", "bar"]):
            return "Restaurants/Hospitality"
        if any(x in ctx for x in ["hvac", "plumbing", "contractor", "electrician"]):
            return "Local Services"
        if any(x in ctx for x in ["consulting", "professional", "legal", "accounting"]):
            return "Professional Services"
        if any(x in ctx for x in ["manufacturing", "industrial", "wholesale"]):
            return "Manufacturing/B2B"

    return "Other"


def classify_size_bucket(employee_count: int | None) -> str:
    """Classify employee count into size bucket"""
    if employee_count is None:
        return "unknown"
    if employee_count <= 10:
        return "1-10"
    if employee_count <= 50:
        return "11-50"
    if employee_count <= 200:
        return "51-200"
    return "200+"


def domains_match(d1: str | None, d2: str | None) -> bool:
    """Check if two domains match (normalizing)"""
    if not d1 or not d2:
        return False
    d1 = str(d1).lower().replace("www.", "").rstrip("/").strip()
    d2 = str(d2).lower().replace("www.", "").rstrip("/").strip()
    return d1 == d2


class OceanClient:
    """Ocean.io API client - Updated to match API docs"""

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = "https://api.ocean.io/v2"

    async def enrich_company(
        self,
        company_name: str,
        domain: str = None,
        city: str = None,
        state: str = None,
        country_code: str = "us"
    ) -> dict:
        """
        Enrich company data via Ocean.io API
        Endpoint: POST /v2/enrich/company
        Auth: X-Api-Token header

        Best results when domain is provided.
        """
        url = f"{self.base_url}/enrich/company"

        headers = {
            'X-Api-Token': self.api_key,
            'Content-Type': 'application/json'
        }

        # Build company object - domain gives best results
        company_obj = {}

        if domain:
            company_obj['domain'] = domain
        else:
            # Fall back to name-based lookup (may get 404 without enough context)
            company_obj['name'] = company_name

        payload = {'company': company_obj}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"data": data}
                    elif response.status == 201:
                        data = await response.json()
                        return {"data": data}
                    elif response.status == 404:
                        return {}
                    elif response.status == 401:
                        logger.error("Ocean API auth failed")
                        return {}
                    elif response.status == 402:
                        logger.error("Ocean API: Insufficient credits")
                        return {}
                    else:
                        return {}
        except Exception as e:
            logger.debug(f"Ocean API error for {company_name}: {e}")
            return {}


class GroundTruthBuilder:
    """Builds full ground truth dataset"""

    def __init__(self, config_path: str = "./evaluation/config.yaml"):
        # Load config
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.ocean_key = self.config.get("api_keys", {}).get("ocean")
        self.cache = EvaluationCache("./evaluation/data/cache.db")

        self.companies: list[EnrichedCompany] = []

        # Ocean.io client
        self._ocean_client = None

    async def _get_ocean_client(self):
        """Get or create Ocean.io client"""
        if self._ocean_client is None and self.ocean_key:
            self._ocean_client = OceanClient(self.ocean_key)
        return self._ocean_client

    def load_source_data(
        self,
        test_companies_path: str,
        ground_truth_path: str
    ) -> int:
        """Load and merge source data"""
        df_companies = pd.read_csv(test_companies_path)
        df_truth = pd.read_csv(ground_truth_path)

        # Merge
        df_merged = df_companies.merge(df_truth, on="name", how="inner")

        logger.info(f"Loaded {len(df_merged)} companies with ground truth")

        # Create EnrichedCompany objects
        for _, row in df_merged.iterrows():
            company = EnrichedCompany(
                name=row["name"],
                city=row.get("city"),
                phone=row.get("phone"),
                context=row.get("context"),
                expected_domain=row.get("expected_domain"),
            )
            # Also classify industry from context
            company.industry = classify_industry(company.context, None)
            self.companies.append(company)

        return len(self.companies)

    async def enrich_with_ocean(
        self,
        max_concurrent: int = 5,
        skip_cache: bool = False
    ):
        """Enrich all companies with Ocean.io data"""
        if not self.ocean_key:
            logger.warning("No Ocean.io API key - using existing ground truth only")
            # Mark all as verified with expected domain
            for c in self.companies:
                if c.expected_domain:
                    c.verification_status = "verified"
            return

        semaphore = asyncio.Semaphore(max_concurrent)
        total = len(self.companies)

        async def enrich_one(idx: int, company: EnrichedCompany):
            async with semaphore:
                await self._enrich_company(company, skip_cache)
                if (idx + 1) % 50 == 0:
                    logger.info(f"Enriched {idx + 1}/{total} companies")

        tasks = [enrich_one(i, c) for i, c in enumerate(self.companies)]
        await asyncio.gather(*tasks)

        # Summary
        enriched = sum(1 for c in self.companies if c.ocean_domain)
        matched = sum(1 for c in self.companies if c.domain_match)
        logger.info(f"Enrichment complete: {enriched}/{total} enriched, {matched} domain matches")

    async def _enrich_company(self, company: EnrichedCompany, skip_cache: bool):
        """Enrich a single company with Ocean.io using expected domain"""
        # Use domain as cache key since that's what we're querying by
        cache_key = company.expected_domain or f"{company.name}:{company.city or ''}"

        # Check cache first
        if not skip_cache:
            cached = self.cache.get("ocean", cache_key)
            if cached:
                self._apply_ocean_data(company, cached)
                return

        try:
            client = await self._get_ocean_client()
            if not client:
                if company.expected_domain:
                    company.verification_status = "verified"
                return

            # Use expected_domain for best results from Ocean.io
            result = await client.enrich_company(
                company.name,
                domain=company.expected_domain,
                city=company.city,
                state=company.state
            )

            data = result.get("data", {})
            if not data:
                # No Ocean data, but we still have our ground truth domain
                if company.expected_domain:
                    company.verification_status = "verified"
                return

            # Extract enrichment data matching Ocean.io response format
            medias = data.get("medias", {})
            linkedin = medias.get("linkedin", {})
            industries = data.get("industries", [])

            enrichment = {
                "domain": data.get("domain"),
                "linkedin_url": linkedin.get("url"),
                "employee_count": data.get("employeeCountOcean") or data.get("employeeCountLinkedin"),
                "industry": industries[0] if industries else data.get("linkedinIndustry"),
                "revenue": data.get("revenue"),
                "year_founded": data.get("yearFounded"),
            }

            # Cache the enrichment data
            self.cache.set("ocean", cache_key, response=enrichment)

            # Apply enrichment
            self._apply_ocean_data(company, enrichment)

        except Exception as e:
            logger.debug(f"Ocean.io error for {company.name}: {e}")
            company.notes = f"Ocean error: {str(e)}"
            # Fall back to verified with expected domain
            if company.expected_domain:
                company.verification_status = "verified"

    def _apply_ocean_data(self, company: EnrichedCompany, data: dict):
        """Apply Ocean.io data to company - handles both raw API and cached formats"""
        company.ocean_domain = data.get("domain")

        # LinkedIn URL - handle both formats:
        # Raw API: medias.linkedin.url
        # Cached: linkedin_url
        if "linkedin_url" in data:
            company.linkedin_company_url = data.get("linkedin_url")
        else:
            medias = data.get("medias", {})
            linkedin = medias.get("linkedin", {})
            company.linkedin_company_url = linkedin.get("url")

        # Employee count - handle both formats:
        # Raw API: employeeCountOcean or employeeCountLinkedin
        # Cached: employee_count
        if "employee_count" in data:
            company.employee_count = data.get("employee_count")
        else:
            company.employee_count = data.get("employeeCountOcean") or data.get("employeeCountLinkedin")

        # Industry - handle both formats:
        # Raw API: industries[] or linkedinIndustry
        # Cached: industry
        if "industry" in data:
            company.ocean_industry = data.get("industry")
        else:
            industries = data.get("industries", [])
            company.ocean_industry = industries[0] if industries else data.get("linkedinIndustry")

        company.revenue = data.get("revenue")
        company.year_founded = data.get("yearFounded")

        # Derive industry and size
        company.industry = classify_industry(company.context, company.ocean_industry)
        company.size_bucket = classify_size_bucket(company.employee_count)

        # Check domain match
        if company.expected_domain and company.ocean_domain:
            company.domain_match = domains_match(company.expected_domain, company.ocean_domain)

            if company.domain_match:
                # Multiple sources agree -> Gold tier
                company.domain_tier = "gold"
                company.verification_status = "verified"
            else:
                # Conflict - but still usable
                company.verification_status = "verified"
                company.domain_tier = "silver"
                company.notes = f"Ocean domain differs: {company.ocean_domain}"
        elif company.expected_domain:
            company.verification_status = "verified"
            company.domain_tier = "silver"
        else:
            company.verification_status = "pending"

    def finalize_without_enrichment(self):
        """
        Finalize ground truth using only existing data (no API calls).
        Used when Ocean.io API is not available or to save costs.
        """
        for c in self.companies:
            if c.expected_domain:
                c.verification_status = "verified"
                c.domain_tier = "silver"
            # Industry already classified from context in load_source_data

        verified = sum(1 for c in self.companies if c.verification_status == "verified")
        logger.info(f"Finalized {verified}/{len(self.companies)} companies without enrichment")

    def identify_tier1_candidates(self) -> list[EnrichedCompany]:
        """
        Identify Tier 1 (Gold) candidates:
        1. Domain conflicts (Ocean ≠ expected)
        2. Vertical SaaS + SMB (hardest cases)
        3. Random sample for validation
        """
        tier1 = []

        # 1. All companies with Ocean match become Gold
        matched = [c for c in self.companies if c.domain_match]
        for c in matched:
            c.domain_tier = "gold"
        tier1.extend(matched)
        logger.info(f"Tier 1 - Ocean matches: {len(matched)}")

        # 2. Vertical SaaS SMBs (1-50 employees) - mark as gold for harder validation
        vsaas_smb = [
            c for c in self.companies
            if c.industry == "Vertical SaaS"
            and c.size_bucket in ("1-10", "11-50", "unknown")
            and c.verification_status == "verified"
            and c not in tier1
        ]
        # Take up to 100
        for c in vsaas_smb[:100]:
            c.domain_tier = "gold"
        tier1.extend(vsaas_smb[:100])
        logger.info(f"Tier 1 - Vertical SaaS SMB: {min(len(vsaas_smb), 100)}")

        # 3. Random sample from verified (for validation)
        verified = [
            c for c in self.companies
            if c.verification_status == "verified"
            and c not in tier1
        ]
        random.seed(42)
        random_sample = random.sample(verified, min(50, len(verified)))
        for c in random_sample:
            c.domain_tier = "gold"
        tier1.extend(random_sample)
        logger.info(f"Tier 1 - Random sample: {len(random_sample)}")

        logger.info(f"Total Tier 1 candidates: {len(tier1)}")
        return tier1

    def assign_splits(self, seed: int = 42):
        """Assign companies to cal/dev/validation/blind splits"""
        random.seed(seed)

        verified = [c for c in self.companies if c.verification_status == "verified"]

        if not verified:
            logger.warning("No verified companies to assign splits")
            return {"cal_dev": 0, "validation": 0, "blind": 0, "gold_in_blind": 0}

        random.shuffle(verified)

        n = len(verified)
        n_cal = int(n * 0.60)
        n_val = int(n * 0.20)

        # Assign splits
        for i, c in enumerate(verified):
            if i < n_cal:
                c.split = "cal_dev"
            elif i < n_cal + n_val:
                c.split = "validation"
            else:
                c.split = "blind"

        # Ensure blind set has enough gold companies
        blind = [c for c in verified if c.split == "blind"]
        gold_in_blind = sum(1 for c in blind if c.domain_tier == "gold")

        logger.info(f"Split assignments:")
        logger.info(f"  CAL/DEV: {n_cal}")
        logger.info(f"  VALIDATION: {n_val}")
        logger.info(f"  BLIND: {len(blind)} ({gold_in_blind} gold)")

        return {
            "cal_dev": n_cal,
            "validation": n_val,
            "blind": len(blind),
            "gold_in_blind": gold_in_blind
        }

    def export_ground_truth(self, output_dir: str = "./evaluation/data"):
        """Export all ground truth datasets"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrames
        verified = [c for c in self.companies if c.verification_status == "verified"]

        if not verified:
            logger.warning("No verified companies to export")
            return pd.DataFrame()

        # Main ground truth
        data = []
        for c in verified:
            data.append({
                "name": c.name,
                "city": c.city,
                "phone": c.phone,
                "expected_domain": c.expected_domain,
                "linkedin_company_url": c.linkedin_company_url,
                "industry": c.industry,
                "size_bucket": c.size_bucket,
                "employee_count": c.employee_count,
                "domain_tier": c.domain_tier,
                "split": c.split,
            })

        df_truth = pd.DataFrame(data)

        # Save main truth
        df_truth.to_parquet(output_path / "companies_truth.parquet", index=False)
        df_truth.to_csv(output_path / "companies_truth.csv", index=False)
        logger.info(f"Saved {len(df_truth)} companies to companies_truth.parquet")

        # Save split assignments
        splits_data = {
            "created": datetime.now().isoformat(),
            "seed": 42,
            "counts": {
                "cal_dev": len(df_truth[df_truth["split"] == "cal_dev"]),
                "validation": len(df_truth[df_truth["split"] == "validation"]),
                "blind": len(df_truth[df_truth["split"] == "blind"]),
            },
            "assignments": df_truth.set_index("name")["split"].to_dict()
        }
        with open(output_path / "splits.yaml", "w") as f:
            yaml.dump(splits_data, f, default_flow_style=False)
        logger.info(f"Saved split assignments to splits.yaml")

        # Export by split for convenience
        for split_name in ["cal_dev", "validation", "blind"]:
            df_split = df_truth[df_truth["split"] == split_name]
            if len(df_split) > 0:
                df_split.to_parquet(output_path / f"companies_{split_name}.parquet", index=False)

        return df_truth

    def generate_summary_report(self, output_path: str = "./evaluation/data/ground_truth_summary.md"):
        """Generate summary report"""
        verified = [c for c in self.companies if c.verification_status == "verified"]

        if not verified:
            logger.warning("No verified companies for report")
            return

        # Industry breakdown
        industry_counts = {}
        for c in verified:
            industry_counts[c.industry] = industry_counts.get(c.industry, 0) + 1

        # Size breakdown
        size_counts = {}
        for c in verified:
            size_counts[c.size_bucket] = size_counts.get(c.size_bucket, 0) + 1

        # Tier breakdown
        gold = sum(1 for c in verified if c.domain_tier == "gold")
        silver = sum(1 for c in verified if c.domain_tier == "silver")

        # Split breakdown
        split_counts = {}
        for c in verified:
            if c.split:
                split_counts[c.split] = split_counts.get(c.split, 0) + 1

        report = f"""# Ground Truth Summary Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

| Metric | Count |
|--------|-------|
| Total Companies | {len(self.companies)} |
| Verified | {len(verified)} |
| With Ocean.io Enrichment | {sum(1 for c in verified if c.ocean_domain)} |

## Tier Breakdown

| Tier | Count | % |
|------|-------|---|
| Gold | {gold} | {gold/len(verified)*100:.1f}% |
| Silver | {silver} | {silver/len(verified)*100:.1f}% |

## Industry Breakdown

| Industry | Count | % |
|----------|-------|---|
"""
        for industry, count in sorted(industry_counts.items(), key=lambda x: -x[1]):
            report += f"| {industry} | {count} | {count/len(verified)*100:.1f}% |\n"

        report += """
## Size Bucket Breakdown

| Size | Count | % |
|------|-------|---|
"""
        for size in ["1-10", "11-50", "51-200", "200+", "unknown"]:
            count = size_counts.get(size, 0)
            if count > 0:
                report += f"| {size} | {count} | {count/len(verified)*100:.1f}% |\n"

        report += """
## Split Breakdown

| Split | Count | Gold | % Gold |
|-------|-------|------|--------|
"""
        for split_name in ["cal_dev", "validation", "blind"]:
            count = split_counts.get(split_name, 0)
            if count > 0:
                split_gold = sum(1 for c in verified if c.split == split_name and c.domain_tier == "gold")
                pct_gold = split_gold / count * 100 if count > 0 else 0
                report += f"| {split_name} | {count} | {split_gold} | {pct_gold:.1f}% |\n"

        report += """
## Files Generated

- `companies_truth.parquet` - Full ground truth dataset
- `companies_truth.csv` - CSV version
- `splits.yaml` - Split assignments
- `companies_cal_dev.parquet` - CAL/DEV split only
- `companies_validation.parquet` - Validation split only
- `companies_blind.parquet` - Blind test split only
"""

        with open(output_path, "w") as f:
            f.write(report)

        logger.info(f"Generated summary report: {output_path}")
        print(report)


async def main():
    """Run full ground truth building"""
    print("\n" + "=" * 60)
    print("PHASE 2: FULL GROUND TRUTH BUILDING")
    print("=" * 60 + "\n")

    builder = GroundTruthBuilder()

    # Step 1: Load source data
    print("Step 1: Loading source data...")
    base_path = Path(__file__).parent.parent.parent
    n = builder.load_source_data(
        test_companies_path=base_path / "domain-resolver/test/test_companies_large.csv",
        ground_truth_path=base_path / "domain-resolver/test/ground_truth_large.csv"
    )
    print(f"  Loaded {n} companies\n")

    # Step 2: Enrich with Ocean.io (or finalize without if no API key)
    print("Step 2: Enriching with Ocean.io...")
    if builder.ocean_key:
        print("  (This uses cached responses where available)")
        await builder.enrich_with_ocean(max_concurrent=5)
    else:
        print("  (No Ocean API key - using existing ground truth)")
        builder.finalize_without_enrichment()
    print()

    # Step 3: Identify Tier 1 candidates
    print("Step 3: Identifying Tier 1 (Gold) candidates...")
    tier1 = builder.identify_tier1_candidates()
    print()

    # Step 4: Assign splits
    print("Step 4: Assigning data splits...")
    splits = builder.assign_splits()
    print()

    # Step 5: Export
    print("Step 5: Exporting ground truth datasets...")
    df_truth = builder.export_ground_truth()
    print()

    # Step 6: Generate report
    print("Step 6: Generating summary report...")
    builder.generate_summary_report()

    print("\n" + "=" * 60)
    print("PHASE 2 COMPLETE")
    print("=" * 60)

    # Cache stats
    stats = builder.cache.stats()
    print(f"\nCache stats: {stats['total_entries']} entries, {stats['db_size_mb']:.2f} MB")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
