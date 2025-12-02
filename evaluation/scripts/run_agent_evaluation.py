#!/usr/bin/env python3
"""
Agent-Based Contact Finder Evaluation

Prepares data for Claude Task agents to evaluate pipeline results.
Each agent independently finds + verifies contacts using:
- MCP Browser (visit websites)
- Web Search (Google OSINT)
- Google Maps data

Usage:
    python -m evaluation.scripts.run_agent_evaluation \
        --input evaluation/data/agent_eval_50.json \
        --pipeline evaluation/results/pilot_baseline_50.json \
        --output evaluation/results/agent_eval_50.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def build_agent_prompt(entity: dict, pipeline_result: dict | None) -> str:
    """Build the prompt for a single Claude Task agent"""

    company_name = entity.get("company_name", "Unknown")
    domain = entity.get("domain", "")
    vertical = entity.get("vertical", "unknown")
    address = entity.get("address", "")
    phone = entity.get("phone", "")

    # Extract pipeline result if available
    pipeline_owner = "None found"
    pipeline_confidence = 0
    pipeline_sources = []

    if pipeline_result and pipeline_result.get("contacts"):
        top_contact = pipeline_result["contacts"][0]
        pipeline_owner = f"{top_contact.get('name', 'Unknown')} ({top_contact.get('title', 'Unknown')})"
        pipeline_confidence = top_contact.get("confidence", 0)
        pipeline_sources = top_contact.get("sources", [])

    prompt = f"""You are evaluating contact discovery for an SMB company.

COMPANY DETAILS:
- Name: {company_name}
- Domain: {domain}
- Vertical: {vertical}
- Address: {address}
- Phone: {phone}

PIPELINE RESULT (to verify):
- Owner Found: {pipeline_owner}
- Confidence: {pipeline_confidence}%
- Sources: {', '.join(pipeline_sources) if pipeline_sources else 'None'}

YOUR TASKS:

1. INDEPENDENTLY find the owner/decision-maker using these tools in order:
   a. Use mcp__browser-mcp__chrome_navigate to visit https://{domain}
   b. Use mcp__browser-mcp__chrome_get_web_content to extract "About Us" or team info
   c. Use WebSearch for "{company_name} owner founder CEO"
   d. If needed, search Google Maps data

2. VERIFY the pipeline result:
   - Does your finding match the pipeline result?
   - Is the pipeline result accurate?

3. RETURN ONLY this JSON (no other text):
{{
  "company_name": "{company_name}",
  "domain": "{domain}",
  "agent_owner_name": "name you found or null",
  "agent_owner_title": "title or null",
  "agent_sources": ["list of sources used"],
  "agent_confidence": "high/medium/low/none",
  "pipeline_owner": "{pipeline_owner}",
  "pipeline_verdict": "correct/incorrect/partial/unknown",
  "reasoning": "brief explanation of your finding"
}}

IMPORTANT:
- Only return the JSON, nothing else
- If you can't find any owner info, set agent_confidence to "none"
- "partial" means pipeline found a real person but wrong details
- "unknown" means you couldn't verify either way
"""
    return prompt


def prepare_evaluation_data(
    input_file: str,
    pipeline_file: str,
    output_file: str
) -> list[dict]:
    """Prepare evaluation data combining entities with pipeline results"""

    # Load entities
    with open(input_file, "r") as f:
        entities = json.load(f)

    # Load pipeline results
    with open(pipeline_file, "r") as f:
        pipeline_data = json.load(f)

    # Index pipeline results by company name
    pipeline_by_company = {}
    for result in pipeline_data.get("results", []):
        company_name = result.get("company_name", "")
        pipeline_by_company[company_name] = result

    # Build evaluation items
    eval_items = []
    for entity in entities:
        company_name = entity.get("company_name", "")
        pipeline_result = pipeline_by_company.get(company_name)

        eval_item = {
            "entity": entity,
            "pipeline_result": pipeline_result,
            "agent_prompt": build_agent_prompt(entity, pipeline_result)
        }
        eval_items.append(eval_item)

    # Save prepared data
    output = {
        "metadata": {
            "input_file": input_file,
            "pipeline_file": pipeline_file,
            "total_entities": len(eval_items),
            "prepared_at": datetime.now().isoformat()
        },
        "items": eval_items
    }

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Prepared {len(eval_items)} entities for agent evaluation")
    print(f"Output saved to: {output_file}")

    return eval_items


def print_sample_prompt(eval_items: list[dict], index: int = 0):
    """Print a sample prompt for verification"""
    if eval_items:
        print("\n" + "="*60)
        print(f"SAMPLE AGENT PROMPT (Entity {index + 1}):")
        print("="*60)
        print(eval_items[index]["agent_prompt"])
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Prepare agent evaluation data")
    parser.add_argument("--input", required=True, help="Input entities JSON file")
    parser.add_argument("--pipeline", required=True, help="Pipeline results JSON file")
    parser.add_argument("--output", required=True, help="Output prepared data file")
    parser.add_argument("--sample", action="store_true", help="Print sample prompt")

    args = parser.parse_args()

    eval_items = prepare_evaluation_data(
        args.input,
        args.pipeline,
        args.output
    )

    if args.sample:
        print_sample_prompt(eval_items)


if __name__ == "__main__":
    main()
