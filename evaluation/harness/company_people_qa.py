"""
Company → People QA Framework

Tests enrichment providers against LinkedIn connections as ground truth.
Compares results from multiple sources to identify differences.
"""

import asyncio
import csv
import json
import os
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Any

from .multi_source_enricher import MultiSourceEnricher, EnrichedProfile, SourceResult


@dataclass
class LinkedInConnection:
    """A LinkedIn connection from the export"""
    first_name: str
    last_name: str
    full_name: str
    email: str | None
    company: str | None
    title: str | None
    linkedin_url: str | None
    connected_on: str | None

    @property
    def name(self) -> str:
        return self.full_name or f"{self.first_name} {self.last_name}".strip()


@dataclass
class EnrichmentComparison:
    """Comparison of enrichment results for one connection"""
    connection: LinkedInConnection
    enriched: EnrichedProfile | None

    # Per-source results
    sources_data: dict[str, dict] = field(default_factory=dict)

    # Comparison flags
    name_matches: dict[str, bool] = field(default_factory=dict)
    title_matches: dict[str, bool] = field(default_factory=dict)
    company_matches: dict[str, bool] = field(default_factory=dict)

    # Differences found
    differences: list[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        """Check if sources returned different data"""
        return len(self.differences) > 0


class CompanyPeopleQATester:
    """
    QA framework for testing enrichment providers.

    Loads LinkedIn connections and enriches each one from multiple sources,
    comparing results to identify where providers differ.
    """

    def __init__(
        self,
        rapidapi_key: str | None = None,
        scrapin_key: str | None = None,
        output_dir: str = "evaluation/data/qa_results"
    ):
        self.enricher = MultiSourceEnricher(
            rapidapi_key=rapidapi_key,
            scrapin_key=scrapin_key
        )
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def close(self):
        await self.enricher.close()

    def load_linkedin_export(self, zip_path: str) -> list[LinkedInConnection]:
        """
        Load connections from LinkedIn data export ZIP file.

        Args:
            zip_path: Path to LinkedIn export ZIP

        Returns:
            List of LinkedInConnection objects
        """
        connections = []

        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Find Connections.csv in the archive
            csv_filename = None
            for name in zf.namelist():
                if 'Connections' in name and name.endswith('.csv'):
                    csv_filename = name
                    break

            if not csv_filename:
                raise ValueError(f"No Connections.csv found in {zip_path}")

            with zf.open(csv_filename) as f:
                # LinkedIn CSVs are UTF-8 with BOM sometimes
                text_file = TextIOWrapper(f, encoding='utf-8-sig')
                lines = text_file.readlines()

                # Skip header notes (LinkedIn exports have 3 header lines before actual CSV)
                # Find the line with actual column headers
                header_idx = 0
                for i, line in enumerate(lines):
                    if 'First Name' in line or 'first_name' in line.lower():
                        header_idx = i
                        break

                # Parse from header line onwards
                from io import StringIO
                csv_content = ''.join(lines[header_idx:])
                reader = csv.DictReader(StringIO(csv_content))

                for row in reader:
                    # Handle various column name formats
                    first = row.get('First Name', row.get('first_name', ''))
                    last = row.get('Last Name', row.get('last_name', ''))
                    email = row.get('Email Address', row.get('email', ''))
                    company = row.get('Company', row.get('company', ''))
                    title = row.get('Position', row.get('Title', row.get('position', '')))
                    url = row.get('URL', row.get('Profile URL', row.get('linkedin_url', '')))
                    connected = row.get('Connected On', row.get('connected_on', ''))

                    connections.append(LinkedInConnection(
                        first_name=first.strip() if first else '',
                        last_name=last.strip() if last else '',
                        full_name=f"{first} {last}".strip() if first or last else '',
                        email=email.strip() if email else None,
                        company=company.strip() if company else None,
                        title=title.strip() if title else None,
                        linkedin_url=url.strip() if url else None,
                        connected_on=connected.strip() if connected else None
                    ))

        return connections

    def _normalize_for_comparison(self, text: str | None) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        return text.lower().strip()

    def _fuzzy_match(self, a: str | None, b: str | None, threshold: float = 0.8) -> bool:
        """Check if two strings are similar enough"""
        if not a or not b:
            return False

        a_norm = self._normalize_for_comparison(a)
        b_norm = self._normalize_for_comparison(b)

        # Exact match
        if a_norm == b_norm:
            return True

        # One contains the other
        if a_norm in b_norm or b_norm in a_norm:
            return True

        # Simple word overlap for titles/companies
        a_words = set(a_norm.split())
        b_words = set(b_norm.split())
        if a_words and b_words:
            overlap = len(a_words & b_words) / max(len(a_words), len(b_words))
            if overlap >= threshold:
                return True

        return False

    def _compare_sources(
        self,
        connection: LinkedInConnection,
        enriched: EnrichedProfile
    ) -> EnrichmentComparison:
        """Compare enrichment results from different sources"""

        comparison = EnrichmentComparison(
            connection=connection,
            enriched=enriched
        )

        # Extract data from each source
        sources = []

        if enriched.rapidapi and enriched.rapidapi.success:
            sources.append(("rapidapi", enriched.rapidapi))
            comparison.sources_data["rapidapi"] = {
                "name": enriched.rapidapi.name,
                "title": enriched.rapidapi.title,
                "company": enriched.rapidapi.company,
            }

        if enriched.scrapin and enriched.scrapin.success:
            sources.append(("scrapin", enriched.scrapin))
            comparison.sources_data["scrapin"] = {
                "name": enriched.scrapin.name,
                "title": enriched.scrapin.title,
                "company": enriched.scrapin.company,
            }

        # Check matches against ground truth (LinkedIn export)
        ground_truth_name = connection.name
        ground_truth_title = connection.title
        ground_truth_company = connection.company

        for source_name, source_data in sources:
            comparison.name_matches[source_name] = self._fuzzy_match(
                source_data.name, ground_truth_name
            )
            comparison.title_matches[source_name] = self._fuzzy_match(
                source_data.title, ground_truth_title
            )
            comparison.company_matches[source_name] = self._fuzzy_match(
                source_data.company, ground_truth_company
            )

        # Find differences between sources
        if len(sources) >= 2:
            # Compare names
            names = [s[1].name for s in sources if s[1].name]
            if len(set(self._normalize_for_comparison(n) for n in names)) > 1:
                comparison.differences.append(f"Name differs: {names}")

            # Compare titles
            titles = [s[1].title for s in sources if s[1].title]
            if len(titles) >= 2:
                if not self._fuzzy_match(titles[0], titles[1]):
                    comparison.differences.append(f"Title differs: {titles}")

            # Compare companies
            companies = [s[1].company for s in sources if s[1].company]
            if len(companies) >= 2:
                if not self._fuzzy_match(companies[0], companies[1]):
                    comparison.differences.append(f"Company differs: {companies}")

        return comparison

    async def test_connection(
        self,
        connection: LinkedInConnection
    ) -> EnrichmentComparison:
        """Test enrichment for a single connection"""

        if not connection.linkedin_url:
            return EnrichmentComparison(
                connection=connection,
                enriched=None,
                differences=["No LinkedIn URL available"]
            )

        try:
            enriched = await self.enricher.enrich(connection.linkedin_url)
            comparison = self._compare_sources(connection, enriched)
            return comparison
        except Exception as e:
            return EnrichmentComparison(
                connection=connection,
                enriched=None,
                differences=[f"Error: {str(e)}"]
            )

    async def run_test(
        self,
        connections: list[LinkedInConnection],
        concurrency: int = 3,
        delay_between: float = 1.0,
        progress_callback: callable = None
    ) -> list[EnrichmentComparison]:
        """
        Run enrichment test on all connections.

        Args:
            connections: List of connections to test
            concurrency: Max concurrent requests
            delay_between: Delay between requests
            progress_callback: Optional callback(current, total, comparison)
        """
        results = []
        semaphore = asyncio.Semaphore(concurrency)

        async def test_with_limit(i: int, conn: LinkedInConnection):
            async with semaphore:
                result = await self.test_connection(conn)
                await asyncio.sleep(delay_between)

                if progress_callback:
                    progress_callback(i + 1, len(connections), result)

                return result

        tasks = [test_with_limit(i, conn) for i, conn in enumerate(connections)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(EnrichmentComparison(
                    connection=connections[i],
                    enriched=None,
                    differences=[f"Error: {str(result)}"]
                ))
            else:
                final_results.append(result)

        return final_results

    def generate_report(
        self,
        results: list[EnrichmentComparison],
        output_file: str | None = None
    ) -> str:
        """Generate a comparison report"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if not output_file:
            output_file = self.output_dir / f"enrichment_comparison_{timestamp}.md"

        # Calculate stats
        total = len(results)
        with_url = sum(1 for r in results if r.connection.linkedin_url)
        enriched = sum(1 for r in results if r.enriched and r.enriched.sources_succeeded > 0)
        with_differences = sum(1 for r in results if r.has_differences())

        # Per-source stats
        rapidapi_success = sum(1 for r in results if r.enriched and r.enriched.rapidapi and r.enriched.rapidapi.success)
        scrapin_success = sum(1 for r in results if r.enriched and r.enriched.scrapin and r.enriched.scrapin.success)

        # Build report
        lines = [
            "# Enrichment Provider Comparison Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Connections:** {total}",
            f"**With LinkedIn URL:** {with_url}",
            f"**Successfully Enriched:** {enriched}",
            f"**With Differences:** {with_differences}",
            "",
            "## Source Success Rates",
            "",
            "| Source | Success | Rate |",
            "|--------|---------|------|",
            f"| RapidAPI | {rapidapi_success} | {rapidapi_success/with_url*100:.1f}% |" if with_url else "| RapidAPI | 0 | 0% |",
            f"| Scrapin | {scrapin_success} | {scrapin_success/with_url*100:.1f}% |" if with_url else "| Scrapin | 0 | 0% |",
            "",
            "## Connections with Differences",
            "",
        ]

        # List connections with differences
        diff_count = 0
        for r in results:
            if r.has_differences():
                diff_count += 1
                lines.append(f"### {diff_count}. {r.connection.name}")
                lines.append(f"**LinkedIn Export:** {r.connection.title} at {r.connection.company}")
                lines.append("")

                for source, data in r.sources_data.items():
                    lines.append(f"**{source.upper()}:** {data.get('title')} at {data.get('company')}")

                lines.append("")
                lines.append("**Differences:**")
                for diff in r.differences:
                    lines.append(f"- {diff}")
                lines.append("")

        if diff_count == 0:
            lines.append("*No significant differences found between sources.*")

        # Add detailed results section
        lines.extend([
            "",
            "---",
            "",
            "## All Results (JSON)",
            "",
            "```json",
        ])

        # Export as JSON for manual review
        json_data = []
        for r in results:
            json_data.append({
                "name": r.connection.name,
                "linkedin_url": r.connection.linkedin_url,
                "ground_truth": {
                    "title": r.connection.title,
                    "company": r.connection.company,
                },
                "sources": r.sources_data,
                "differences": r.differences,
            })

        lines.append(json.dumps(json_data, indent=2))
        lines.append("```")

        report = "\n".join(lines)

        # Write report
        with open(output_file, 'w') as f:
            f.write(report)

        # Also save raw JSON
        json_file = str(output_file).replace('.md', '.json')
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)

        return str(output_file)


# CLI test
async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test enrichment providers")
    parser.add_argument("--linkedin-export", required=True, help="Path to LinkedIn export ZIP")
    parser.add_argument("--sample", type=int, help="Sample size (default: all)")
    parser.add_argument("--concurrency", type=int, default=3, help="Concurrent requests")

    args = parser.parse_args()

    # Get API keys from environment
    rapidapi_key = os.environ.get("RAPIDAPI_KEY")
    scrapin_key = os.environ.get("SCRAPIN_API_KEY")

    tester = CompanyPeopleQATester(
        rapidapi_key=rapidapi_key,
        scrapin_key=scrapin_key
    )

    try:
        print(f"Loading LinkedIn export: {args.linkedin_export}")
        connections = tester.load_linkedin_export(args.linkedin_export)
        print(f"Loaded {len(connections)} connections")

        # Sample if requested
        if args.sample and args.sample < len(connections):
            import random
            connections = random.sample(connections, args.sample)
            print(f"Sampled {len(connections)} connections")

        # Filter to those with URLs
        connections = [c for c in connections if c.linkedin_url]
        print(f"{len(connections)} have LinkedIn URLs")

        # Progress callback
        def progress(current, total, result):
            status = "ok" if result.enriched and result.enriched.sources_succeeded > 0 else "fail"
            diff = "DIFF" if result.has_differences() else ""
            print(f"[{current}/{total}] {result.connection.name}: {status} {diff}")

        # Run test
        print("\nRunning enrichment comparison...")
        results = await tester.run_test(
            connections,
            concurrency=args.concurrency,
            progress_callback=progress
        )

        # Generate report
        report_path = tester.generate_report(results)
        print(f"\nReport saved to: {report_path}")

    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
