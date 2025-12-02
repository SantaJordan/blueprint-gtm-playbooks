"""
Metrics calculation for domain resolver and contact finder evaluation.

Extracted and extended from domain-resolver/test/compare_apis.py
"""

import pandas as pd
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricsResult:
    """Container for evaluation metrics"""
    total: int = 0
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    true_negatives: int = 0
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    coverage: float = 0.0

    # Confidence calibration
    high_conf_accuracy: float = 0.0
    high_conf_count: int = 0
    medium_conf_accuracy: float = 0.0
    medium_conf_count: int = 0
    low_conf_accuracy: float = 0.0
    low_conf_count: int = 0

    # Expected Calibration Error
    calibration_ece: float = 0.0

    # Stratified breakdowns
    by_source: dict = field(default_factory=dict)
    by_industry: dict = field(default_factory=dict)
    by_size_bucket: dict = field(default_factory=dict)
    by_persona: dict = field(default_factory=dict)
    by_tier: dict = field(default_factory=dict)

    # Raw data for analysis
    merged_data: pd.DataFrame = field(default_factory=pd.DataFrame)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding DataFrame"""
        return {
            k: v for k, v in self.__dict__.items()
            if not isinstance(v, pd.DataFrame)
        }


def calculate_domain_metrics(
    df_results: pd.DataFrame,
    df_truth: pd.DataFrame,
    join_on: tuple[str, str] = ("company_name", "name")
) -> MetricsResult:
    """
    Calculate domain resolution accuracy metrics.

    Args:
        df_results: Results DataFrame with columns: company_name, domain, confidence, source
        df_truth: Ground truth DataFrame with columns: name, expected_domain, industry, size_bucket, tier
        join_on: Tuple of (result_col, truth_col) to join on

    Returns:
        MetricsResult with accuracy metrics and breakdowns
    """
    result_col, truth_col = join_on

    merged = df_results.merge(
        df_truth,
        left_on=result_col,
        right_on=truth_col,
        how='inner',
        suffixes=('_result', '_truth')
    )

    total = len(merged)
    if total == 0:
        return MetricsResult()

    # Core correctness flags
    merged['correct'] = merged.apply(
        lambda row: _domains_match(row.get('domain'), row.get('expected_domain')),
        axis=1
    )

    merged['false_positive'] = merged.apply(
        lambda row: (pd.notna(row.get('domain')) and
                    not _domains_match(row.get('domain'), row.get('expected_domain'))),
        axis=1
    )

    merged['false_negative'] = merged.apply(
        lambda row: (pd.isna(row.get('domain')) and pd.notna(row.get('expected_domain'))),
        axis=1
    )

    merged['true_negative'] = merged.apply(
        lambda row: (pd.isna(row.get('domain')) and pd.isna(row.get('expected_domain'))),
        axis=1
    )

    # Aggregate counts
    tp = merged['correct'].sum()
    fp = merged['false_positive'].sum()
    fn = merged['false_negative'].sum()
    tn = merged['true_negative'].sum()

    # Core metrics
    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    coverage = (tp + fp) / total

    # Confidence calibration
    conf_col = 'confidence' if 'confidence' in merged.columns else None
    high_conf_acc, high_conf_n = _conf_band_accuracy(merged, conf_col, 85, 100)
    med_conf_acc, med_conf_n = _conf_band_accuracy(merged, conf_col, 70, 85)
    low_conf_acc, low_conf_n = _conf_band_accuracy(merged, conf_col, 0, 70)

    # Expected Calibration Error
    ece = _calculate_ece(merged, conf_col) if conf_col else 0.0

    # Stratified breakdowns
    by_source = _breakdown_by_column(merged, 'source')
    by_industry = _breakdown_by_column(merged, 'industry')
    by_size = _breakdown_by_column(merged, 'size_bucket')
    by_tier = _breakdown_by_column(merged, 'tier')

    return MetricsResult(
        total=total,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        true_negatives=tn,
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1,
        coverage=coverage,
        high_conf_accuracy=high_conf_acc,
        high_conf_count=high_conf_n,
        medium_conf_accuracy=med_conf_acc,
        medium_conf_count=med_conf_n,
        low_conf_accuracy=low_conf_acc,
        low_conf_count=low_conf_n,
        calibration_ece=ece,
        by_source=by_source,
        by_industry=by_industry,
        by_size_bucket=by_size,
        by_tier=by_tier,
        merged_data=merged
    )


def calculate_contact_metrics(
    df_results: pd.DataFrame,
    df_truth: pd.DataFrame,
    join_on: str = "company_name"
) -> MetricsResult:
    """
    Calculate contact finder accuracy metrics.

    Args:
        df_results: Results with columns: company_name, contacts (list), personas_found
        df_truth: Ground truth with columns: company_name, expected_contacts (list), persona_type

    Returns:
        MetricsResult with contact accuracy metrics
    """
    merged = df_results.merge(
        df_truth,
        on=join_on,
        how='inner',
        suffixes=('_result', '_truth')
    )

    total = len(merged)
    if total == 0:
        return MetricsResult()

    # For contacts, we check:
    # - Persona recall: did we find at least 1 person with matching title?
    # - Person precision: is the contact the right individual?
    # - Email accuracy: does email match or validate?

    merged['persona_found'] = merged.apply(_check_persona_found, axis=1)
    merged['person_correct'] = merged.apply(_check_person_match, axis=1)
    merged['email_correct'] = merged.apply(_check_email_match, axis=1)

    persona_recall = merged['persona_found'].sum() / total
    person_precision = merged['person_correct'].sum() / merged['persona_found'].sum() if merged['persona_found'].sum() > 0 else 0.0
    email_accuracy = merged['email_correct'].sum() / merged['person_correct'].sum() if merged['person_correct'].sum() > 0 else 0.0

    # Stratified
    by_persona = _breakdown_by_column(merged, 'persona_type', correct_col='persona_found')
    by_industry = _breakdown_by_column(merged, 'industry', correct_col='persona_found')
    by_size = _breakdown_by_column(merged, 'size_bucket', correct_col='persona_found')

    return MetricsResult(
        total=total,
        true_positives=int(merged['persona_found'].sum()),
        accuracy=persona_recall,  # Using accuracy field for persona recall
        precision=person_precision,
        recall=email_accuracy,  # Using recall field for email accuracy
        by_persona=by_persona,
        by_industry=by_industry,
        by_size_bucket=by_size,
        merged_data=merged
    )


def calculate_e2e_metrics(
    df_results: pd.DataFrame,
    df_truth: pd.DataFrame,
    join_on: str = "company_name"
) -> dict:
    """
    Calculate end-to-end pipeline metrics.

    Error attribution:
    - domain_wrong: Domain resolver returned incorrect domain
    - domain_missing: No domain found
    - contact_not_found: Correct domain but no contacts
    - wrong_persona: Contact found but wrong title
    - wrong_person: Right persona but wrong individual
    - email_invalid: Correct person but email invalid
    - success: All stages correct

    Returns:
        Dict with e2e success rate and error attribution breakdown
    """
    merged = df_results.merge(
        df_truth,
        on=join_on,
        how='inner'
    )

    total = len(merged)
    if total == 0:
        return {"total": 0, "error": "No matching companies"}

    # Attribute errors
    error_counts = {
        "domain_wrong": 0,
        "domain_missing": 0,
        "contact_not_found": 0,
        "wrong_persona": 0,
        "wrong_person": 0,
        "email_invalid": 0,
        "success": 0
    }

    for _, row in merged.iterrows():
        stage = _attribute_failure_stage(row)
        error_counts[stage] += 1

    success_rate = error_counts["success"] / total

    # Cost metrics
    total_cost = merged['total_cost'].sum() if 'total_cost' in merged.columns else 0
    cost_per_success = total_cost / error_counts["success"] if error_counts["success"] > 0 else float('inf')

    return {
        "total": total,
        "success_count": error_counts["success"],
        "success_rate": success_rate,
        "error_attribution": error_counts,
        "error_rates": {k: v / total for k, v in error_counts.items()},
        "total_cost": total_cost,
        "cost_per_success": cost_per_success,
        "merged_data": merged
    }


# Helper functions

def _domains_match(d1: str | None, d2: str | None) -> bool:
    """Check if two domains match (normalizing www, trailing slashes)"""
    if pd.isna(d1) or pd.isna(d2):
        return False
    d1 = str(d1).lower().replace("www.", "").rstrip("/").strip()
    d2 = str(d2).lower().replace("www.", "").rstrip("/").strip()
    return d1 == d2


def _conf_band_accuracy(df: pd.DataFrame, conf_col: str | None, low: float, high: float) -> tuple[float, int]:
    """Calculate accuracy for a confidence band"""
    if conf_col is None or conf_col not in df.columns:
        return 0.0, 0

    mask = (df[conf_col] >= low) & (df[conf_col] < high)
    band_df = df[mask]
    n = len(band_df)
    if n == 0:
        return 0.0, 0

    acc = band_df['correct'].sum() / n
    return acc, n


def _calculate_ece(df: pd.DataFrame, conf_col: str, n_bins: int = 10) -> float:
    """Calculate Expected Calibration Error"""
    if conf_col not in df.columns:
        return 0.0

    df = df.dropna(subset=[conf_col])
    if len(df) == 0:
        return 0.0

    bins = pd.cut(df[conf_col], bins=n_bins, labels=False)
    ece = 0.0
    total = len(df)

    for bin_idx in range(n_bins):
        bin_mask = bins == bin_idx
        bin_df = df[bin_mask]
        if len(bin_df) == 0:
            continue

        avg_conf = bin_df[conf_col].mean() / 100  # Normalize to 0-1
        avg_acc = bin_df['correct'].mean()
        weight = len(bin_df) / total

        ece += weight * abs(avg_conf - avg_acc)

    return ece


def _breakdown_by_column(df: pd.DataFrame, col: str, correct_col: str = 'correct') -> dict:
    """Generate accuracy breakdown by a categorical column"""
    if col not in df.columns:
        return {}

    breakdown = {}
    for val in df[col].dropna().unique():
        subset = df[df[col] == val]
        n = len(subset)
        correct = subset[correct_col].sum() if correct_col in subset.columns else 0
        breakdown[str(val)] = {
            "count": n,
            "correct": int(correct),
            "accuracy": correct / n if n > 0 else 0.0
        }

    return breakdown


def _check_persona_found(row) -> bool:
    """Check if at least one contact matches target persona"""
    contacts = row.get('contacts', [])
    target_persona = row.get('persona_type', '')

    if not contacts or not target_persona:
        return False

    # Define title patterns per persona
    persona_patterns = {
        'owner_operator': ['owner', 'founder', 'ceo', 'president', 'principal', 'managing partner'],
        'vp_marketing': ['vp marketing', 'head of marketing', 'cmo', 'director marketing', 'vp of marketing'],
        'vp_sales': ['vp sales', 'head of sales', 'cro', 'director sales', 'vp of sales']
    }

    patterns = persona_patterns.get(target_persona, [])

    for contact in contacts:
        title = (contact.get('title') or '').lower()
        if any(p in title for p in patterns):
            return True

    return False


def _check_person_match(row) -> bool:
    """Check if found contact matches expected person"""
    contacts = row.get('contacts', [])
    expected = row.get('expected_contacts', [])

    if not contacts or not expected:
        return False

    # Match by LinkedIn URL or name
    for contact in contacts:
        for exp in expected:
            if _person_matches(contact, exp):
                return True

    return False


def _person_matches(contact: dict, expected: dict) -> bool:
    """Check if two contact records match"""
    # Match by LinkedIn URL (most reliable)
    c_li = (contact.get('linkedin_url') or '').lower().rstrip('/')
    e_li = (expected.get('linkedin_url') or '').lower().rstrip('/')
    if c_li and e_li and c_li == e_li:
        return True

    # Match by name (fuzzy)
    c_name = (contact.get('name') or '').lower()
    e_name = (expected.get('name') or '').lower()
    if c_name and e_name:
        # Simple containment check
        if c_name in e_name or e_name in c_name:
            return True

    return False


def _check_email_match(row) -> bool:
    """Check if email matches ground truth"""
    contacts = row.get('contacts', [])
    expected = row.get('expected_contacts', [])

    if not contacts or not expected:
        return False

    contact_emails = {(c.get('email') or '').lower() for c in contacts}
    expected_emails = {(e.get('email') or '').lower() for e in expected}

    return bool(contact_emails & expected_emails)


def _attribute_failure_stage(row) -> str:
    """Determine which stage caused the failure"""
    domain_correct = row.get('domain_correct', False)
    domain_found = pd.notna(row.get('domain'))
    contacts_found = len(row.get('contacts', [])) > 0
    persona_found = row.get('persona_found', False)
    person_correct = row.get('person_correct', False)
    email_correct = row.get('email_correct', False)

    if not domain_found:
        return "domain_missing"
    if not domain_correct:
        return "domain_wrong"
    if not contacts_found:
        return "contact_not_found"
    if not persona_found:
        return "wrong_persona"
    if not person_correct:
        return "wrong_person"
    if not email_correct:
        return "email_invalid"

    return "success"
