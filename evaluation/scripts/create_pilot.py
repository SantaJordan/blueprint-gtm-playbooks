#!/usr/bin/env python3
"""
Create pilot ground truth set from existing domain resolver test data.

Takes 200 companies from the existing ground_truth_large.csv and test_companies_large.csv
to create a pilot dataset for the evaluation framework.
"""

import pandas as pd
from pathlib import Path
import random


def create_pilot(
    test_companies_path: str,
    ground_truth_path: str,
    output_dir: str,
    pilot_size: int = 200,
    seed: int = 42
):
    """Create pilot ground truth from existing data"""

    # Load existing data
    df_companies = pd.read_csv(test_companies_path)
    df_truth = pd.read_csv(ground_truth_path)

    print(f"Loaded {len(df_companies)} companies from test data")
    print(f"Loaded {len(df_truth)} ground truth entries")

    # Merge to get complete records
    df_merged = df_companies.merge(
        df_truth,
        on="name",
        how="inner"
    )

    print(f"Merged: {len(df_merged)} companies with ground truth")

    # Sample pilot set
    random.seed(seed)
    if len(df_merged) > pilot_size:
        indices = random.sample(range(len(df_merged)), pilot_size)
        df_pilot = df_merged.iloc[indices].copy()
    else:
        df_pilot = df_merged.copy()

    print(f"Pilot set: {len(df_pilot)} companies")

    # Extract industry from context if available
    def extract_industry(context):
        if pd.isna(context):
            return "Unknown"
        context = str(context)
        if "Healthcare" in context:
            return "Healthcare"
        if "Restaurant" in context or "Food" in context:
            return "Restaurants/Hospitality"
        if "HVAC" in context or "Plumbing" in context or "Contractor" in context:
            return "Local Services"
        if "Software" in context or "SaaS" in context or "Tech" in context:
            return "Vertical SaaS"
        if "Professional" in context or "Consulting" in context:
            return "Professional Services"
        if "Manufacturing" in context:
            return "Manufacturing/B2B"
        return "Other"

    df_pilot["industry"] = df_pilot["context"].apply(extract_industry)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save companies file (input format)
    companies_out = df_pilot[["name", "city", "phone", "industry"]].copy()
    companies_out.to_csv(output_path / "pilot_companies.csv", index=False)
    print(f"Saved: {output_path / 'pilot_companies.csv'}")

    # Save ground truth file
    truth_out = df_pilot[["name", "expected_domain", "city", "industry"]].copy()
    truth_out["domain_tier"] = "silver"  # All from existing data
    truth_out["size_bucket"] = "unknown"  # Not available in source
    truth_out.to_csv(output_path / "pilot_truth.csv", index=False)
    truth_out.to_parquet(output_path / "pilot_truth.parquet", index=False)
    print(f"Saved: {output_path / 'pilot_truth.parquet'}")

    # Print industry breakdown
    print("\nIndustry breakdown:")
    print(df_pilot["industry"].value_counts())

    return df_pilot


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.parent

    create_pilot(
        test_companies_path=base_path / "domain-resolver/test/test_companies_large.csv",
        ground_truth_path=base_path / "domain-resolver/test/ground_truth_large.csv",
        output_dir=base_path / "evaluation/data",
        pilot_size=200
    )
