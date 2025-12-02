#!/usr/bin/env python3
"""
Validate the evaluation pipeline works end-to-end.

This script:
1. Tests metrics calculation with synthetic results
2. Tests cache operations
3. Validates the Blitz evaluator structure
"""

import pandas as pd
import asyncio
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evaluation.harness.metrics import calculate_domain_metrics, MetricsResult
from evaluation.harness.cache import EvaluationCache


def test_metrics():
    """Test metrics calculation with synthetic data"""
    print("=" * 50)
    print("Testing Metrics Calculation")
    print("=" * 50)

    # Create synthetic results (simulate domain resolver output)
    results_data = [
        {"company_name": "Acme Corp", "domain": "acme.com", "confidence": 95, "source": "serper"},
        {"company_name": "Beta Inc", "domain": "beta.io", "confidence": 85, "source": "ocean"},
        {"company_name": "Gamma LLC", "domain": "wrong.com", "confidence": 75, "source": "serper"},  # Wrong
        {"company_name": "Delta Co", "domain": None, "confidence": 0, "source": None},  # Missing
        {"company_name": "Epsilon Ltd", "domain": "epsilon.com", "confidence": 92, "source": "ocean"},
    ]
    df_results = pd.DataFrame(results_data)

    # Create ground truth
    truth_data = [
        {"name": "Acme Corp", "expected_domain": "acme.com", "industry": "Tech", "tier": "gold"},
        {"name": "Beta Inc", "expected_domain": "beta.io", "industry": "Tech", "tier": "silver"},
        {"name": "Gamma LLC", "expected_domain": "gamma.com", "industry": "Finance", "tier": "silver"},  # Result is wrong
        {"name": "Delta Co", "expected_domain": "delta.org", "industry": "Healthcare", "tier": "gold"},  # Missing in results
        {"name": "Epsilon Ltd", "expected_domain": "epsilon.com", "industry": "Tech", "tier": "gold"},
    ]
    df_truth = pd.DataFrame(truth_data)

    # Calculate metrics
    metrics = calculate_domain_metrics(df_results, df_truth)

    print(f"\nResults:")
    print(f"  Total: {metrics.total}")
    print(f"  True Positives: {metrics.true_positives}")
    print(f"  False Positives: {metrics.false_positives}")
    print(f"  False Negatives: {metrics.false_negatives}")
    print(f"  Accuracy: {metrics.accuracy*100:.1f}%")
    print(f"  Precision: {metrics.precision*100:.1f}%")
    print(f"  Recall: {metrics.recall*100:.1f}%")
    print(f"  F1 Score: {metrics.f1_score*100:.1f}%")
    print(f"  Coverage: {metrics.coverage*100:.1f}%")

    # Validate expected values
    assert metrics.total == 5, f"Expected 5 companies, got {metrics.total}"
    assert metrics.true_positives == 3, f"Expected 3 TPs (Acme, Beta, Epsilon), got {metrics.true_positives}"
    assert metrics.false_positives == 1, f"Expected 1 FP (Gamma), got {metrics.false_positives}"
    assert metrics.false_negatives == 1, f"Expected 1 FN (Delta), got {metrics.false_negatives}"

    print("\n✓ Metrics calculation working correctly")
    return True


def test_cache():
    """Test cache operations"""
    print("\n" + "=" * 50)
    print("Testing Cache Operations")
    print("=" * 50)

    cache = EvaluationCache("./evaluation/data/test_cache.db")

    # Test set/get
    cache.set("test_api", "key1", response={"data": "value1"})
    result = cache.get("test_api", "key1")
    assert result == {"data": "value1"}, f"Cache get failed: {result}"
    print("  ✓ Basic set/get works")

    # Test cache miss
    result = cache.get("test_api", "nonexistent")
    assert result is None, "Expected None for cache miss"
    print("  ✓ Cache miss returns None")

    # Test stats
    stats = cache.stats()
    assert stats["total_entries"] >= 1
    print(f"  ✓ Stats: {stats['total_entries']} entries")

    # Cleanup
    cache.clear_all()
    Path("./evaluation/data/test_cache.db").unlink(missing_ok=True)

    print("\n✓ Cache operations working correctly")
    return True


def test_pilot_data():
    """Test loading pilot data"""
    print("\n" + "=" * 50)
    print("Testing Pilot Data")
    print("=" * 50)

    pilot_path = Path("./evaluation/data/pilot_truth.parquet")

    if not pilot_path.exists():
        print("  ⚠ Pilot data not found - run create_pilot.py first")
        return False

    df = pd.read_parquet(pilot_path)
    print(f"  Loaded {len(df)} companies")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Industries: {df['industry'].value_counts().to_dict()}")

    # Validate structure
    required_cols = ["name", "expected_domain", "industry"]
    missing = [c for c in required_cols if c not in df.columns]
    assert not missing, f"Missing required columns: {missing}"

    print("\n✓ Pilot data structure is valid")
    return True


def main():
    """Run all validation tests"""
    print("\n" + "=" * 60)
    print("EVALUATION FRAMEWORK VALIDATION")
    print("=" * 60)

    tests = [
        ("Metrics", test_metrics),
        ("Cache", test_cache),
        ("Pilot Data", test_pilot_data),
    ]

    results = {}
    for name, test_fn in tests:
        try:
            results[name] = test_fn()
        except Exception as e:
            print(f"\n✗ {name} test failed: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("All validations passed! Pipeline is ready.")
    else:
        print("Some validations failed. Please fix before proceeding.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
