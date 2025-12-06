"""
Blueprint Playbook Quality Checker

Parses HTML playbooks and scores them on 12 quality dimensions.
Used to compare cloud (Modal) output vs local (Claude Code) baseline.
"""

import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


@dataclass
class PlayCard:
    """Represents a single PQS or PVP play card."""
    play_type: str  # "PQS" or "PVP"
    title: str
    score: Optional[float]
    segment: Optional[str]
    explanation: str
    why_works: str
    data_source: str
    subject: str
    body: str


@dataclass
class PlaybookQualityScore:
    """Quality metrics for a Blueprint playbook."""

    # Metadata
    company_name: str
    source: str  # "local" or "cloud"
    file_path: str

    # Structure metrics
    pqs_count: int = 0
    pvp_count: int = 0
    total_plays: int = 0
    segments_identified: int = 0

    # Content metrics
    has_segment_labels: bool = False
    has_score_badges: bool = False
    has_calculation_worksheets: bool = False
    has_data_source_citations: bool = False

    # Data specificity (0-10)
    data_source_specificity: float = 0.0
    record_number_count: int = 0
    specific_date_count: int = 0
    api_field_mentions: int = 0

    # Message quality
    avg_pqs_score: float = 0.0
    avg_pvp_score: float = 0.0
    placeholder_count: int = 0

    # Texada Test estimates
    hyper_specific_indicators: int = 0
    factual_grounding_indicators: int = 0

    # Aggregate score (0-100)
    overall_score: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


class PlaybookQualityChecker:
    """Parses and scores Blueprint playbooks."""

    # Patterns for detecting quality indicators
    PLACEHOLDER_PATTERNS = [
        r'\[company_name\]',
        r'\[Company Name\]',
        r'\[First Name\]',
        r'\[X\]',
        r'\[similar company\]',
        r'\[industry\]',
        r'\[specific.*?\]',
    ]

    RECORD_NUMBER_PATTERNS = [
        r'#[A-Z0-9]{5,}',  # Record IDs like #W912QR-25-R-0047
        r'solicitation\s+#\S+',
        r'violation\s+#\S+',
        r'permit\s+#\S+',
        r'case\s+#\S+',
        r'NPI\s+\d{10}',  # Healthcare NPI numbers
        r'NAICS\s+\d{6}',  # Industry codes
    ]

    SPECIFIC_DATE_PATTERNS = [
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,?\s+\d{4})?',
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b',
        r'\bQ[1-4]\s+\d{4}\b',
    ]

    API_FIELD_PATTERNS = [
        r'API',
        r'field[s]?\s*:',
        r'endpoint',
        r'\.gov\b',
        r'SAM\.gov',
        r'USASpending',
        r'EPA ECHO',
        r'OSHA',
        r'CMS',
        r'FMCSA',
        r'BuiltWith',
        r'G2 (?:Buyer )?Intent',
    ]

    GENERIC_DATA_SOURCES = [
        'government databases',
        'public records',
        'data sources',
        'industry data',
    ]

    SPECIFIC_DATA_SOURCES = [
        'SAM.gov',
        'USASpending',
        'EPA ECHO',
        'OSHA',
        'CMS',
        'FMCSA',
        'BuiltWith',
        'G2',
        'LinkedIn',
        'Crunchbase',
        'NIPR',
    ]

    def __init__(self, html_path: str):
        self.html_path = Path(html_path)
        self.html_content = self.html_path.read_text(encoding='utf-8')
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
        self.play_cards: List[PlayCard] = []

    def extract_company_name(self) -> str:
        """Extract company name from title."""
        title = self.soup.find('title')
        if title:
            match = re.search(r'Blueprint GTM Playbook for (.+)', title.text)
            if match:
                return match.group(1).strip()

        h1 = self.soup.find('h1')
        if h1:
            match = re.search(r'Blueprint GTM Playbook for (.+)', h1.text)
            if match:
                return match.group(1).strip()

        return "Unknown"

    def extract_play_cards(self) -> List[PlayCard]:
        """Extract all play cards from the HTML."""
        cards = []

        # Find all play-card divs
        card_divs = self.soup.find_all('div', class_='play-card')

        for card_div in card_divs:
            # Extract play type
            type_span = card_div.find('span', class_='play-type')
            play_type = "PVP" if type_span and 'pvp' in type_span.get('class', []) else "PQS"
            if type_span:
                play_type = type_span.text.strip() or play_type

            # Extract score
            score = None
            score_badge = card_div.find('span', class_='score-badge')
            if score_badge:
                score_match = re.search(r'(\d+\.?\d*)/10', score_badge.text)
                if score_match:
                    score = float(score_match.group(1))

            # Extract segment label
            segment = None
            segment_label = card_div.find('span', class_='segment-label')
            if segment_label:
                segment = segment_label.text.strip()

            # Extract title
            title_elem = card_div.find('h3')
            title = title_elem.text.strip() if title_elem else ""

            # Extract explanation
            explanation = ""
            explanation_div = card_div.find('div', class_='play-explanation')
            if explanation_div:
                explanation = explanation_div.get_text(strip=True)

            # Extract why it works
            why_works = ""
            why_section = card_div.find('div', class_='why-section')
            if why_section:
                why_works = why_section.get_text(strip=True)

            # Extract data source
            data_source = ""
            data_div = card_div.find('div', class_='data-sources')
            if data_div:
                data_source = data_div.get_text(strip=True)

            # Extract message
            subject = ""
            body = ""
            message_div = card_div.find('div', class_='message-example')
            if message_div:
                message_text = message_div.get_text()
                lines = message_text.strip().split('\n')
                if lines:
                    subject_match = re.search(r'Subject:\s*(.+)', lines[0])
                    if subject_match:
                        subject = subject_match.group(1).strip()
                    body = '\n'.join(lines[1:]).strip()

            cards.append(PlayCard(
                play_type=play_type,
                title=title,
                score=score,
                segment=segment,
                explanation=explanation,
                why_works=why_works,
                data_source=data_source,
                subject=subject,
                body=body
            ))

        self.play_cards = cards
        return cards

    def count_pattern_matches(self, text: str, patterns: List[str]) -> int:
        """Count total matches across all patterns."""
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count

    def calculate_data_source_specificity(self) -> float:
        """Score data source specificity from 0-10."""
        all_data_sources = ' '.join([card.data_source for card in self.play_cards])

        if not all_data_sources:
            return 0.0

        # Check for generic vs specific sources
        generic_count = sum(1 for g in self.GENERIC_DATA_SOURCES
                          if g.lower() in all_data_sources.lower())
        specific_count = sum(1 for s in self.SPECIFIC_DATA_SOURCES
                            if s.lower() in all_data_sources.lower())

        # Check for API/field documentation
        has_api_docs = bool(re.search(r'API|field[s]?\s*:', all_data_sources, re.IGNORECASE))
        has_urls = bool(re.search(r'https?://|\.gov|\.com', all_data_sources, re.IGNORECASE))

        # Calculate score
        if specific_count >= 3 and has_api_docs:
            return 10.0
        elif specific_count >= 2:
            return 8.0 + (1.0 if has_urls else 0)
        elif specific_count >= 1:
            return 6.0 + (1.0 if has_api_docs else 0)
        elif generic_count > 0:
            return 2.0
        else:
            return 1.0

    def evaluate(self, source: str = "unknown") -> PlaybookQualityScore:
        """Evaluate the playbook and return quality score."""

        # Extract components
        company_name = self.extract_company_name()
        self.extract_play_cards()

        # Combine all text for pattern matching
        all_text = self.html_content
        all_messages = ' '.join([f"{c.subject} {c.body}" for c in self.play_cards])

        # Count plays by type
        pqs_cards = [c for c in self.play_cards if 'PQS' in c.play_type.upper()]
        pvp_cards = [c for c in self.play_cards if 'PVP' in c.play_type.upper()]

        # Calculate averages
        pqs_scores = [c.score for c in pqs_cards if c.score is not None]
        pvp_scores = [c.score for c in pvp_cards if c.score is not None]

        avg_pqs = sum(pqs_scores) / len(pqs_scores) if pqs_scores else 0.0
        avg_pvp = sum(pvp_scores) / len(pvp_scores) if pvp_scores else 0.0

        # Count segments
        segments = set(c.segment for c in self.play_cards if c.segment)

        # Build score object
        score = PlaybookQualityScore(
            company_name=company_name,
            source=source,
            file_path=str(self.html_path),

            # Structure
            pqs_count=len(pqs_cards),
            pvp_count=len(pvp_cards),
            total_plays=len(self.play_cards),
            segments_identified=len(segments),

            # Content
            has_segment_labels=any(c.segment for c in self.play_cards),
            has_score_badges=any(c.score is not None for c in self.play_cards),
            has_calculation_worksheets='calculation' in all_text.lower() or 'worksheet' in all_text.lower(),
            has_data_source_citations=any(c.data_source for c in self.play_cards),

            # Specificity
            data_source_specificity=self.calculate_data_source_specificity(),
            record_number_count=self.count_pattern_matches(all_messages, self.RECORD_NUMBER_PATTERNS),
            specific_date_count=self.count_pattern_matches(all_messages, self.SPECIFIC_DATE_PATTERNS),
            api_field_mentions=self.count_pattern_matches(all_text, self.API_FIELD_PATTERNS),

            # Message quality
            avg_pqs_score=avg_pqs,
            avg_pvp_score=avg_pvp,
            placeholder_count=self.count_pattern_matches(all_messages, self.PLACEHOLDER_PATTERNS),

            # Texada indicators
            hyper_specific_indicators=self.count_pattern_matches(all_messages, self.RECORD_NUMBER_PATTERNS + self.SPECIFIC_DATE_PATTERNS),
            factual_grounding_indicators=self.count_pattern_matches(all_text, self.API_FIELD_PATTERNS),
        )

        # Calculate overall score (0-100)
        score.overall_score = self._calculate_overall_score(score)

        return score

    def _calculate_overall_score(self, score: PlaybookQualityScore) -> float:
        """Calculate aggregate score from 0-100."""
        points = 0.0

        # Structure (25 points max)
        points += min(score.pqs_count, 2) * 5  # 10 max
        points += min(score.pvp_count, 2) * 5  # 10 max
        points += min(score.segments_identified, 2) * 2.5  # 5 max

        # Content quality (25 points max)
        points += 5 if score.has_segment_labels else 0
        points += 5 if score.has_score_badges else 0
        points += 5 if score.has_calculation_worksheets else 0
        points += 5 if score.has_data_source_citations else 0
        points += 5 if score.placeholder_count == 0 else 0

        # Data specificity (25 points max)
        points += score.data_source_specificity * 2.5  # 25 max

        # Message scores (25 points max)
        avg_score = (score.avg_pqs_score + score.avg_pvp_score) / 2 if (score.avg_pqs_score + score.avg_pvp_score) > 0 else 0
        points += avg_score * 2.5  # 25 max

        return min(100.0, points)


def compare_playbooks(local_path: str, cloud_path: str) -> Dict:
    """Compare local and cloud playbooks, generate delta report."""

    local_checker = PlaybookQualityChecker(local_path)
    cloud_checker = PlaybookQualityChecker(cloud_path)

    local_score = local_checker.evaluate(source="local")
    cloud_score = cloud_checker.evaluate(source="cloud")

    # Calculate deltas
    deltas = {
        "pqs_count": cloud_score.pqs_count - local_score.pqs_count,
        "pvp_count": cloud_score.pvp_count - local_score.pvp_count,
        "segments_identified": cloud_score.segments_identified - local_score.segments_identified,
        "data_source_specificity": cloud_score.data_source_specificity - local_score.data_source_specificity,
        "record_number_count": cloud_score.record_number_count - local_score.record_number_count,
        "specific_date_count": cloud_score.specific_date_count - local_score.specific_date_count,
        "avg_pqs_score": cloud_score.avg_pqs_score - local_score.avg_pqs_score,
        "avg_pvp_score": cloud_score.avg_pvp_score - local_score.avg_pvp_score,
        "placeholder_count": cloud_score.placeholder_count - local_score.placeholder_count,
        "overall_score": cloud_score.overall_score - local_score.overall_score,
    }

    # Identify issues
    issues = []
    if deltas["pqs_count"] < 0:
        issues.append(f"Missing {-deltas['pqs_count']} PQS plays")
    if deltas["pvp_count"] < 0:
        issues.append(f"Missing {-deltas['pvp_count']} PVP plays")
    if deltas["data_source_specificity"] < -2:
        issues.append("Data sources are too generic")
    if deltas["record_number_count"] < -2:
        issues.append("Missing specific record numbers/IDs")
    if deltas["placeholder_count"] > 0:
        issues.append(f"Contains {cloud_score.placeholder_count} placeholder(s)")
    if not cloud_score.has_segment_labels and local_score.has_segment_labels:
        issues.append("Missing segment labels")
    if not cloud_score.has_score_badges and local_score.has_score_badges:
        issues.append("Missing score badges")

    return {
        "local": local_score.to_dict(),
        "cloud": cloud_score.to_dict(),
        "deltas": deltas,
        "issues": issues,
        "pass": cloud_score.overall_score >= (local_score.overall_score * 0.8),  # 80% of local baseline
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate Blueprint playbook quality")
    parser.add_argument("--local", help="Path to local baseline playbook")
    parser.add_argument("--cloud", help="Path to cloud-generated playbook")
    parser.add_argument("--single", help="Evaluate a single playbook")
    parser.add_argument("--output", help="Output JSON file path")

    args = parser.parse_args()

    if args.single:
        checker = PlaybookQualityChecker(args.single)
        score = checker.evaluate(source="single")
        result = score.to_dict()
    elif args.local and args.cloud:
        result = compare_playbooks(args.local, args.cloud)
    else:
        parser.print_help()
        return

    # Output
    output_json = json.dumps(result, indent=2)

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Results written to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
