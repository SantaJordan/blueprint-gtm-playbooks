#!/usr/bin/env python3
"""
SMB Contact Pipeline V2 Test Script

Test the new data-driven pipeline on SMB companies.
Uses:
- Dynamic CSV/JSON exploration
- Serper for data filling and OSINT
- ZenRows for website scraping
- Schema.org extraction
- Simple rule-based validation (no LLM)
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add contact-finder to path (hyphenated directory name)
project_root = Path(__file__).parent.parent.parent
contact_finder_path = project_root / "contact-finder"
sys.path.insert(0, str(contact_finder_path))

from modules.pipeline.smb_pipeline import (
    SMBContactPipeline,
    print_pipeline_result
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_test(
    input_file: str,
    output_file: str | None,
    limit: int,
    concurrency: int,
    skip_stages: list[str]
):
    """Run the SMB V2 pipeline test"""

    logger.info(f"="*60)
    logger.info(f"SMB Contact Pipeline V2 Test")
    logger.info(f"="*60)
    logger.info(f"Input: {input_file}")
    logger.info(f"Limit: {limit} companies")
    logger.info(f"Concurrency: {concurrency}")
    logger.info(f"Skip stages: {skip_stages or 'none'}")
    logger.info(f"="*60)

    # Check API keys
    api_keys = {
        "SERPER_API_KEY": os.environ.get("SERPER_API_KEY"),
        "LEADMAGIC_API_KEY": os.environ.get("LEADMAGIC_API_KEY"),
        "ZENROWS_API_KEY": os.environ.get("ZENROWS_API_KEY")
    }

    logger.info("API Keys:")
    for key, value in api_keys.items():
        status = "SET" if value else "NOT SET"
        logger.info(f"  {key}: {status}")

    # Initialize pipeline
    pipeline = SMBContactPipeline(
        concurrency=concurrency,
        min_validation_score=50
    )

    try:
        # Run pipeline
        result = await pipeline.run(
            input_file=input_file,
            limit=limit,
            skip_stages=skip_stages
        )

        # Print results
        print_pipeline_result(result)

        # Save results
        if output_file:
            output_data = {
                "metadata": {
                    "input_file": input_file,
                    "limit": limit,
                    "concurrency": concurrency,
                    "skip_stages": skip_stages,
                    "timestamp": datetime.now().isoformat()
                },
                "summary": {
                    "total_companies": result.total_companies,
                    "companies_processed": result.companies_processed,
                    "contacts_found": result.contacts_found,
                    "contacts_validated": result.contacts_validated,
                    "serper_queries": result.serper_queries,
                    "leadmagic_credits": result.leadmagic_credits,
                    "zenrows_requests": result.zenrows_requests,
                    "estimated_cost": result.total_cost
                },
                "stage_stats": result.stage_stats,
                "results": [
                    {
                        "company_name": r.company_name,
                        "domain": r.domain,
                        "vertical": r.vertical,
                        "stages_completed": r.stages_completed,
                        "errors": r.errors,
                        "processing_time_ms": r.processing_time_ms,
                        "contacts": [
                            {
                                "name": c.name,
                                "email": c.email,
                                "phone": c.phone,
                                "title": c.title,
                                "linkedin_url": c.linkedin_url,
                                "sources": c.sources,
                                "is_valid": c.validation.is_valid if c.validation else False,
                                "confidence": c.validation.confidence if c.validation else 0,
                                "validation_reasons": c.validation.reasons if c.validation else []
                            }
                            for c in r.contacts
                        ]
                    }
                    for r in result.results
                ]
            }

            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            logger.info(f"Results saved to: {output_file}")

        # Print success metrics
        if result.companies_processed > 0:
            find_rate = result.contacts_found / result.companies_processed * 100
            validate_rate = result.contacts_validated / result.companies_processed * 100

            print(f"\n{'='*60}")
            print("SUCCESS METRICS")
            print(f"{'='*60}")
            print(f"Companies Processed: {result.companies_processed}/{result.total_companies}")
            print(f"Contacts Found:      {result.contacts_found} ({find_rate:.1f}%)")
            print(f"Contacts Validated:  {result.contacts_validated} ({validate_rate:.1f}%)")
            print(f"Estimated Cost:      ${result.total_cost:.2f}")
            print(f"{'='*60}\n")

    finally:
        await pipeline.close()


def main():
    parser = argparse.ArgumentParser(
        description="Test SMB Contact Pipeline V2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test on 50 companies with all stages
  python run_smb_v2_test.py --input ../data/smb_sample_1400.json --limit 50

  # Skip website scraping (faster but less data)
  python run_smb_v2_test.py --input ../data/smb_sample_1400.json --limit 50 --skip website

  # Skip enrichment (no LeadMagic credits used)
  python run_smb_v2_test.py --input ../data/smb_sample_1400.json --limit 50 --skip enrichment
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to input CSV or JSON file"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to save results (JSON)"
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=50,
        help="Number of companies to process (default: 50)"
    )
    parser.add_argument(
        "--concurrency", "-c",
        type=int,
        default=5,
        help="Concurrent processing (default: 5)"
    )
    parser.add_argument(
        "--skip",
        nargs="+",
        default=[],
        choices=["data_fill", "website", "serper_osint", "enrichment"],
        help="Stages to skip"
    )

    args = parser.parse_args()

    # Set default output if not specified
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"evaluation/results/smb_v2_test_{args.limit}_{timestamp}.json"

    # Run async
    asyncio.run(run_test(
        input_file=args.input,
        output_file=args.output,
        limit=args.limit,
        concurrency=args.concurrency,
        skip_stages=args.skip
    ))


if __name__ == "__main__":
    main()
