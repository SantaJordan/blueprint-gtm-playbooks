#!/usr/bin/env python3
"""
Compare cloud-generated playbooks against local baselines.

Usage:
  python run_cloud_comparison.py --quick    # Test 3 companies
  python run_cloud_comparison.py --full     # Test all 15 companies
"""

import json
import sys
import time
import argparse
import asyncio
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from quality_checker import PlaybookQualityChecker, compare_playbooks


# Config
BLUEPRINT_API_URL = "https://blueprint-trigger-api.vercel.app"
GITHUB_PAGES_BASE = "https://SantaJordan.github.io/blueprint-gtm-playbooks"
POLL_INTERVAL = 30  # seconds
MAX_WAIT_TIME = 1800  # 30 minutes


def trigger_job(company_url: str) -> dict:
    """Trigger a Blueprint job for a company URL."""
    import urllib.request
    import json

    data = json.dumps({"url": company_url}).encode('utf-8')
    req = Request(
        f"{BLUEPRINT_API_URL}/api/queue-job",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except URLError as e:
        return {"error": str(e)}


def poll_job_status(job_id: str) -> dict:
    """Poll job status until complete or timeout."""
    # For now, just check if playbook exists at GitHub Pages
    # This is a simplified version - full version would check Supabase
    return {"status": "unknown", "playbook_url": None}


def fetch_playbook(url: str) -> str:
    """Fetch playbook HTML from URL."""
    try:
        with urlopen(url, timeout=60) as response:
            return response.read().decode('utf-8')
    except URLError as e:
        return None


def run_comparison(companies: list, base_path: Path) -> dict:
    """Run comparison for a list of companies."""
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "comparisons": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
        }
    }

    for company in companies:
        print(f"\n{'='*60}")
        print(f"Testing: {company['name']}")
        print(f"{'='*60}")

        # Get local baseline
        local_path = base_path / company["local_playbook"]
        if not local_path.exists():
            print(f"⚠️  Local baseline not found: {local_path}")
            continue

        # Check if cloud playbook exists
        domain = company["url"].replace("https://", "").replace("http://", "").replace("/", "")
        cloud_url = f"{GITHUB_PAGES_BASE}/blueprint-gtm-playbook-{domain}.html"

        print(f"Checking cloud playbook: {cloud_url}")

        cloud_html = fetch_playbook(cloud_url)
        if not cloud_html:
            print(f"⚠️  Cloud playbook not available (may need to trigger job)")

            # For now, skip if cloud not available
            results["comparisons"].append({
                "company": company["name"],
                "status": "cloud_not_available",
                "pass": False,
                "issues": ["Cloud playbook not found at GitHub Pages"],
            })
            results["summary"]["total"] += 1
            results["summary"]["failed"] += 1
            continue

        # Save cloud HTML temporarily
        temp_cloud_path = Path("/tmp") / f"cloud_{domain}.html"
        temp_cloud_path.write_text(cloud_html)

        # Compare
        try:
            comparison = compare_playbooks(str(local_path), str(temp_cloud_path))
            comparison["company"] = company["name"]
            comparison["cloud_url"] = cloud_url

            results["comparisons"].append(comparison)
            results["summary"]["total"] += 1
            if comparison["pass"]:
                results["summary"]["passed"] += 1
                print(f"✅ PASS - Score: {comparison['cloud']['overall_score']:.1f} (baseline: {comparison['local']['overall_score']:.1f})")
            else:
                results["summary"]["failed"] += 1
                print(f"❌ FAIL - Score: {comparison['cloud']['overall_score']:.1f} (baseline: {comparison['local']['overall_score']:.1f})")
                print(f"   Issues: {comparison['issues']}")

        except Exception as e:
            print(f"❌ Error comparing: {e}")
            results["comparisons"].append({
                "company": company["name"],
                "status": "error",
                "error": str(e),
                "pass": False,
            })
            results["summary"]["total"] += 1
            results["summary"]["failed"] += 1

        finally:
            # Cleanup
            if temp_cloud_path.exists():
                temp_cloud_path.unlink()

    return results


def main():
    parser = argparse.ArgumentParser(description="Compare cloud vs local playbooks")
    parser.add_argument("--quick", action="store_true", help="Quick test (3 companies)")
    parser.add_argument("--full", action="store_true", help="Full test (all companies)")
    args = parser.parse_args()

    # Load test data
    test_data_path = Path(__file__).parent / "test_companies.json"
    with open(test_data_path) as f:
        test_data = json.load(f)

    base_path = Path(__file__).parent.parent.parent  # Blueprint-GTM-Skills root

    # Select companies to test
    if args.quick:
        quick_names = test_data["quick_test_set"]
        companies = [c for c in test_data["companies"] if c["name"] in quick_names]
    else:
        companies = test_data["companies"]

    print(f"Testing {len(companies)} companies...")

    # Run comparison
    results = run_comparison(companies, base_path)

    # Print summary
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"Total tested:  {results['summary']['total']}")
    print(f"Passed:        {results['summary']['passed']}")
    print(f"Failed:        {results['summary']['failed']}")

    # Save results
    output_path = Path(__file__).parent / "comparison_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    # Exit with error if any failed
    if results["summary"]["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
