#!/usr/bin/env python3
"""
SMB Pipeline Comparative Test Script

Compares LLM validation vs rule-based validation against ground truth.
Uses the 49-company ground truth dataset for evaluation.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field

# Add contact-finder to path
project_root = Path(__file__).parent.parent.parent
contact_finder_path = project_root / "contact-finder"
sys.path.insert(0, str(contact_finder_path))

from modules.pipeline.smb_pipeline import SMBContactPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result for a single company evaluation"""
    company_name: str
    domain: str
    vertical: str

    # Ground truth
    gt_owner_name: str | None
    gt_has_owner: bool

    # Pipeline results
    found_name: str | None
    found_valid: bool
    found_confidence: float

    # Match evaluation
    is_match: bool = False
    match_type: str = ""  # exact, partial, wrong, none

    # Metadata
    llm_validation: bool = False
    sources: list = field(default_factory=list)


def normalize_name(name: str | None) -> str:
    """Normalize name for comparison"""
    if not name:
        return ""
    return name.lower().strip().replace("  ", " ")


def names_match(found: str | None, expected: str | None) -> tuple[bool, str]:
    """Check if names match, return (is_match, match_type)"""
    if not found and not expected:
        return True, "both_none"
    if not found:
        return False, "none"
    if not expected:
        return True, "no_gt"  # No ground truth, can't evaluate

    found_norm = normalize_name(found)
    expected_norm = normalize_name(expected)

    if found_norm == expected_norm:
        return True, "exact"

    # Check partial matches (last name or first name)
    found_parts = found_norm.split()
    expected_parts = expected_norm.split()

    if any(fp in expected_parts for fp in found_parts):
        return True, "partial"

    # Check if one is substring of other
    if found_norm in expected_norm or expected_norm in found_norm:
        return True, "partial"

    return False, "wrong"


async def run_pipeline_on_ground_truth(
    ground_truth: list[dict],
    use_llm: bool,
    concurrency: int = 5
) -> list[EvaluationResult]:
    """Run pipeline on ground truth companies"""

    results = []
    mode = "LLM" if use_llm else "Rule-based"
    logger.info(f"Running {mode} validation on {len(ground_truth)} companies...")

    # Create temp input file for pipeline
    temp_input = []
    for gt in ground_truth:
        temp_input.append({
            "company_name": gt["company_name"],
            "domain": gt["domain"],
            "vertical": gt["vertical"]
        })

    temp_file = f"/tmp/smb_gt_test_{datetime.now().strftime('%H%M%S')}.json"
    with open(temp_file, 'w') as f:
        json.dump(temp_input, f)

    # Run pipeline
    pipeline = SMBContactPipeline(
        concurrency=concurrency,
        use_llm_validation=use_llm,
        min_validation_score=50
    )

    try:
        pipeline_result = await pipeline.run(
            input_file=temp_file,
            limit=len(ground_truth)
        )

        # Map results to ground truth
        for gt, company_result in zip(ground_truth, pipeline_result.results):
            gt_owner = gt["ground_truth"].get("owner_name")
            gt_has_owner = gt_owner is not None

            # Find best validated contact
            best_contact = None
            best_confidence = 0

            for contact in company_result.contacts:
                if contact.validation and contact.validation.is_valid:
                    if contact.validation.confidence > best_confidence:
                        best_contact = contact
                        best_confidence = contact.validation.confidence

            # If no valid contact, take highest confidence unvalidated
            if not best_contact and company_result.contacts:
                for contact in company_result.contacts:
                    if contact.validation and contact.validation.confidence > best_confidence:
                        best_contact = contact
                        best_confidence = contact.validation.confidence

            found_name = best_contact.name if best_contact else None
            found_valid = best_contact.validation.is_valid if best_contact and best_contact.validation else False
            found_confidence = best_confidence
            sources = best_contact.sources if best_contact else []

            # Check match
            is_match, match_type = names_match(found_name, gt_owner)

            eval_result = EvaluationResult(
                company_name=gt["company_name"],
                domain=gt["domain"],
                vertical=gt["vertical"],
                gt_owner_name=gt_owner,
                gt_has_owner=gt_has_owner,
                found_name=found_name,
                found_valid=found_valid,
                found_confidence=found_confidence,
                is_match=is_match,
                match_type=match_type,
                llm_validation=use_llm,
                sources=sources
            )
            results.append(eval_result)

        # Log LLM validation count
        if use_llm:
            logger.info(f"LLM validations performed: {pipeline._llm_validations}")

    finally:
        await pipeline.close()
        os.unlink(temp_file)

    return results


def calculate_metrics(results: list[EvaluationResult]) -> dict:
    """Calculate precision, recall, accuracy metrics"""

    # Filter to only companies with ground truth owners
    with_gt = [r for r in results if r.gt_has_owner]
    without_gt = [r for r in results if not r.gt_has_owner]

    # True Positives: Found correct owner AND marked valid
    tp = sum(1 for r in with_gt if r.is_match and r.found_valid)

    # False Positives: Found wrong owner AND marked valid
    fp = sum(1 for r in with_gt if not r.is_match and r.found_valid and r.match_type == "wrong")

    # False Negatives: Didn't find valid owner when one exists
    fn = sum(1 for r in with_gt if not r.found_valid)

    # True Negatives: Correctly didn't validate when no GT owner
    tn = sum(1 for r in without_gt if not r.found_valid)

    # Metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    # Match rate: correct matches / companies with GT
    match_rate = sum(1 for r in with_gt if r.is_match) / len(with_gt) if with_gt else 0

    # Validation rate: valid / total
    validation_rate = sum(1 for r in results if r.found_valid) / len(results) if results else 0

    # Match type breakdown
    match_types = {}
    for r in with_gt:
        mt = r.match_type
        match_types[mt] = match_types.get(mt, 0) + 1

    return {
        "total": len(results),
        "with_ground_truth": len(with_gt),
        "without_ground_truth": len(without_gt),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "match_rate": match_rate,
        "validation_rate": validation_rate,
        "match_types": match_types
    }


def print_comparison(llm_metrics: dict, rule_metrics: dict):
    """Print side-by-side comparison"""

    print("\n" + "=" * 70)
    print("COMPARATIVE RESULTS: LLM vs Rule-based Validation")
    print("=" * 70)

    print(f"\n{'Metric':<25} {'LLM':>15} {'Rule-based':>15} {'Delta':>12}")
    print("-" * 70)

    metrics = [
        ("Precision", "precision", True),
        ("Recall", "recall", True),
        ("F1 Score", "f1_score", True),
        ("Match Rate", "match_rate", True),
        ("Validation Rate", "validation_rate", False),
        ("True Positives", "true_positives", True),
        ("False Positives", "false_positives", False),
        ("False Negatives", "false_negatives", False),
    ]

    for label, key, higher_is_better in metrics:
        llm_val = llm_metrics[key]
        rule_val = rule_metrics[key]

        if isinstance(llm_val, float):
            llm_str = f"{llm_val:.1%}"
            rule_str = f"{rule_val:.1%}"
            delta = llm_val - rule_val
            delta_str = f"+{delta:.1%}" if delta > 0 else f"{delta:.1%}"
        else:
            llm_str = str(llm_val)
            rule_str = str(rule_val)
            delta = llm_val - rule_val
            delta_str = f"+{delta}" if delta > 0 else str(delta)

        # Color indication (better = green direction)
        if delta > 0:
            winner = "LLM" if higher_is_better else "Rule"
        elif delta < 0:
            winner = "Rule" if higher_is_better else "LLM"
        else:
            winner = "tie"

        print(f"{label:<25} {llm_str:>15} {rule_str:>15} {delta_str:>12}")

    print("-" * 70)

    # Match type breakdown
    print("\nMatch Type Breakdown (companies with ground truth):")
    print(f"{'Type':<15} {'LLM':>10} {'Rule-based':>12}")
    print("-" * 40)

    all_types = set(llm_metrics["match_types"].keys()) | set(rule_metrics["match_types"].keys())
    for mt in sorted(all_types):
        llm_count = llm_metrics["match_types"].get(mt, 0)
        rule_count = rule_metrics["match_types"].get(mt, 0)
        print(f"{mt:<15} {llm_count:>10} {rule_count:>12}")

    print("=" * 70 + "\n")


def print_vertical_breakdown(results: list[EvaluationResult], mode: str):
    """Print per-vertical metrics"""

    verticals = {}
    for r in results:
        v = r.vertical or "unknown"
        if v not in verticals:
            verticals[v] = []
        verticals[v].append(r)

    print(f"\nPer-Vertical Breakdown ({mode}):")
    print(f"{'Vertical':<30} {'Total':>6} {'Match':>6} {'Valid':>6} {'Rate':>8}")
    print("-" * 60)

    for v in sorted(verticals.keys()):
        vr = verticals[v]
        with_gt = [r for r in vr if r.gt_has_owner]
        matches = sum(1 for r in with_gt if r.is_match)
        valid = sum(1 for r in vr if r.found_valid)
        rate = matches / len(with_gt) if with_gt else 0

        print(f"{v:<30} {len(vr):>6} {matches:>6} {valid:>6} {rate:>7.0%}")

    print("-" * 60)


async def main():
    parser = argparse.ArgumentParser(
        description="Compare LLM vs Rule-based validation on SMB ground truth"
    )
    parser.add_argument(
        "--ground-truth", "-g",
        default="evaluation/data/smb_ground_truth.json",
        help="Path to ground truth JSON file"
    )
    parser.add_argument(
        "--concurrency", "-c",
        type=int,
        default=5,
        help="Concurrent processing (default: 5)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to save detailed results (JSON)"
    )
    parser.add_argument(
        "--llm-only",
        action="store_true",
        help="Only run LLM validation (skip rule-based)"
    )
    parser.add_argument(
        "--rule-only",
        action="store_true",
        help="Only run rule-based validation (skip LLM)"
    )

    args = parser.parse_args()

    # Load ground truth
    gt_path = Path(args.ground_truth)
    if not gt_path.is_absolute():
        gt_path = project_root / gt_path

    with open(gt_path) as f:
        ground_truth = json.load(f)

    logger.info(f"Loaded {len(ground_truth)} companies from ground truth")

    # Count companies with owners
    with_owners = sum(1 for gt in ground_truth if gt["ground_truth"].get("owner_name"))
    logger.info(f"Companies with known owners: {with_owners}")

    # Check API keys
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))
    has_rapidapi = bool(os.environ.get("RAPIDAPI_KEY"))
    has_serper = bool(os.environ.get("SERPER_API_KEY"))

    logger.info(f"API Keys: OPENAI={'SET' if has_openai else 'NOT SET'}, "
                f"RAPIDAPI={'SET' if has_rapidapi else 'NOT SET'}, "
                f"SERPER={'SET' if has_serper else 'NOT SET'}")

    if not has_openai and not args.rule_only:
        logger.warning("OPENAI_API_KEY not set - LLM validation will use rule-based fallback")

    # Run tests
    llm_results = None
    rule_results = None

    if not args.rule_only:
        llm_results = await run_pipeline_on_ground_truth(
            ground_truth, use_llm=True, concurrency=args.concurrency
        )

    if not args.llm_only:
        rule_results = await run_pipeline_on_ground_truth(
            ground_truth, use_llm=False, concurrency=args.concurrency
        )

    # Calculate metrics
    llm_metrics = calculate_metrics(llm_results) if llm_results else None
    rule_metrics = calculate_metrics(rule_results) if rule_results else None

    # Print results
    if llm_metrics and rule_metrics:
        print_comparison(llm_metrics, rule_metrics)
        print_vertical_breakdown(llm_results, "LLM")
        print_vertical_breakdown(rule_results, "Rule-based")
    elif llm_metrics:
        print("\nLLM Validation Results:")
        print(json.dumps(llm_metrics, indent=2))
        print_vertical_breakdown(llm_results, "LLM")
    elif rule_metrics:
        print("\nRule-based Validation Results:")
        print(json.dumps(rule_metrics, indent=2))
        print_vertical_breakdown(rule_results, "Rule-based")

    # Save detailed results
    if args.output:
        output_data = {
            "metadata": {
                "ground_truth_file": str(gt_path),
                "timestamp": datetime.now().isoformat(),
                "concurrency": args.concurrency
            },
            "llm_metrics": llm_metrics,
            "rule_metrics": rule_metrics,
            "llm_results": [
                {
                    "company_name": r.company_name,
                    "domain": r.domain,
                    "vertical": r.vertical,
                    "gt_owner": r.gt_owner_name,
                    "found_name": r.found_name,
                    "found_valid": r.found_valid,
                    "confidence": r.found_confidence,
                    "is_match": r.is_match,
                    "match_type": r.match_type,
                    "sources": r.sources
                }
                for r in (llm_results or [])
            ],
            "rule_results": [
                {
                    "company_name": r.company_name,
                    "domain": r.domain,
                    "vertical": r.vertical,
                    "gt_owner": r.gt_owner_name,
                    "found_name": r.found_name,
                    "found_valid": r.found_valid,
                    "confidence": r.found_confidence,
                    "is_match": r.is_match,
                    "match_type": r.match_type,
                    "sources": r.sources
                }
                for r in (rule_results or [])
            ]
        }

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"Detailed results saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
