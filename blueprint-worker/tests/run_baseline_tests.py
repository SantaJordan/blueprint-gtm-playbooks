#!/usr/bin/env python3
"""
Run baseline tests on local playbooks to establish quality benchmarks.
"""

import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from quality_checker import PlaybookQualityChecker


def run_baseline_tests():
    """Run quality checks on all local playbooks."""

    # Load test companies
    test_data_path = Path(__file__).parent / "test_companies.json"
    with open(test_data_path) as f:
        test_data = json.load(f)

    base_path = Path(__file__).parent.parent.parent  # Blueprint-GTM-Skills root

    results = []
    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "avg_overall_score": 0,
        "avg_pqs_count": 0,
        "avg_pvp_count": 0,
        "avg_data_specificity": 0,
    }

    for company in test_data["companies"]:
        playbook_path = base_path / company["local_playbook"]

        if not playbook_path.exists():
            print(f"⚠️  Skipping {company['name']}: {playbook_path} not found")
            continue

        try:
            checker = PlaybookQualityChecker(str(playbook_path))
            score = checker.evaluate(source="local")

            # Check against thresholds
            thresholds = test_data["success_thresholds"]
            passed = (
                score.pqs_count >= thresholds["pqs_count"] and
                score.pvp_count >= thresholds["pvp_count"] and
                score.placeholder_count <= thresholds["placeholder_count"]
            )

            result = {
                "company": company["name"],
                "vertical": company["vertical"],
                "priority": company["priority"],
                "passed": passed,
                "score": score.to_dict(),
            }
            results.append(result)

            # Update summary
            summary["total"] += 1
            summary["passed"] += 1 if passed else 0
            summary["failed"] += 0 if passed else 1
            summary["avg_overall_score"] += score.overall_score
            summary["avg_pqs_count"] += score.pqs_count
            summary["avg_pvp_count"] += score.pvp_count
            summary["avg_data_specificity"] += score.data_source_specificity

            # Print result
            status = "✅" if passed else "❌"
            print(f"{status} {company['name']:30} | Score: {score.overall_score:5.1f} | PQS: {score.pqs_count} | PVP: {score.pvp_count} | Specificity: {score.data_source_specificity:.1f}")

        except Exception as e:
            print(f"❌ {company['name']}: Error - {e}")
            results.append({
                "company": company["name"],
                "error": str(e),
                "passed": False,
            })
            summary["total"] += 1
            summary["failed"] += 1

    # Calculate averages
    if summary["total"] > 0:
        summary["avg_overall_score"] /= summary["total"]
        summary["avg_pqs_count"] /= summary["total"]
        summary["avg_pvp_count"] /= summary["total"]
        summary["avg_data_specificity"] /= summary["total"]

    # Print summary
    print("\n" + "="*70)
    print("BASELINE SUMMARY")
    print("="*70)
    print(f"Total tested:        {summary['total']}")
    print(f"Passed:              {summary['passed']}")
    print(f"Failed:              {summary['failed']}")
    print(f"Avg Overall Score:   {summary['avg_overall_score']:.1f}/100")
    print(f"Avg PQS Count:       {summary['avg_pqs_count']:.1f}")
    print(f"Avg PVP Count:       {summary['avg_pvp_count']:.1f}")
    print(f"Avg Data Specificity: {summary['avg_data_specificity']:.1f}/10")

    # Save results
    output_path = Path(__file__).parent / "baseline_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "summary": summary,
            "results": results,
            "thresholds": test_data["success_thresholds"],
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return summary, results


if __name__ == "__main__":
    run_baseline_tests()
