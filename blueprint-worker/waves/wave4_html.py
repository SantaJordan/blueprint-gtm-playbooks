"""
Wave 4: HTML Playbook Assembly

Populates the Blueprint HTML template with generated content.
"""
from typing import Dict, List
import os


class Wave4HTML:
    """Wave 4: Assemble the final HTML playbook."""

    # HTML template (inline to avoid file dependencies)
    TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blueprint GTM Playbook for {company_name}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {{
            --print-blue: #5611A6;
            --dark-print: #280A4A;
            --light-print: #D6B2FF;
            --corn: #FFF277;
            --ice: #F5F8FF;
            --white: #FFFFFF;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.7;
            color: var(--dark-print);
            background: var(--ice);
            font-size: 16px;
        }}

        .container {{
            max-width: 100%;
            margin: 0 auto;
            padding: 1rem;
        }}

        h1 {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--dark-print);
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid var(--light-print);
        }}

        h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--dark-print);
            margin: 2.5rem 0 1rem;
            padding-left: 1rem;
            position: relative;
        }}

        h2::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: var(--print-blue);
        }}

        h3 {{
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--dark-print);
            margin-bottom: 0.5rem;
        }}

        p {{
            font-size: 1rem;
            color: rgba(40, 10, 74, 0.9);
            margin-bottom: 1rem;
            line-height: 1.7;
        }}

        .section {{
            background: var(--white);
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 8px rgba(86, 17, 166, 0.08);
            margin-bottom: 2rem;
        }}

        .highlight-box {{
            background: var(--corn);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        }}

        .old-way-example {{
            background: #FFF8DC;
            border: 2px solid #F0E68C;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }}

        .message-example {{
            background: var(--ice);
            padding: 1rem;
            border-radius: 0.5rem;
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
            line-height: 1.6;
            white-space: pre-wrap;
            overflow-x: auto;
            margin: 0.5rem 0;
        }}

        .play-card {{
            background: var(--white);
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(86, 17, 166, 0.08);
            border: 1px solid var(--light-print);
        }}

        .play-type {{
            display: inline-block;
            background: var(--print-blue);
            color: var(--white);
            padding: 0.25rem 0.75rem;
            border-radius: 2rem;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }}

        .play-type.pvp {{
            background: var(--dark-print);
        }}

        .play-explanation {{
            background: var(--ice);
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }}

        .data-sources {{
            background: var(--corn);
            padding: 0.75rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            font-size: 0.875rem;
        }}

        .why-section {{
            font-size: 0.875rem;
            color: rgba(40, 10, 74, 0.8);
            margin-bottom: 1rem;
        }}

        .score-badge {{
            display: inline-block;
            background: #10B981;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 2rem;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 0.5rem;
        }}

        .score-badge.medium {{
            background: #F59E0B;
        }}

        .score-badge.low {{
            background: #EF4444;
        }}

        .segment-label {{
            display: inline-block;
            background: var(--ice);
            color: var(--print-blue);
            padding: 0.25rem 0.75rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            font-weight: 500;
            margin-left: 0.5rem;
            border: 1px solid var(--light-print);
        }}

        .calculation-worksheet {{
            background: #F0FDF4;
            border: 1px solid #86EFAC;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
        }}

        .calculation-worksheet h4 {{
            color: #166534;
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
        }}

        .data-confidence {{
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.625rem;
            font-weight: 600;
            margin-left: 0.25rem;
        }}

        .data-confidence.high {{
            background: #DCFCE7;
            color: #166534;
        }}

        .data-confidence.medium {{
            background: #FEF3C7;
            color: #92400E;
        }}

        .data-confidence.low {{
            background: #FEE2E2;
            color: #991B1B;
        }}

        .texada-badge {{
            display: inline-block;
            background: var(--dark-print);
            color: var(--corn);
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.625rem;
            font-weight: 600;
            margin-right: 0.25rem;
        }}

        .texada-badge.fail {{
            background: #FEE2E2;
            color: #991B1B;
        }}

        @media (min-width: 768px) {{
            .container {{
                max-width: 900px;
                padding: 2rem;
            }}

            h1 {{
                font-size: 2.5rem;
            }}

            h2 {{
                font-size: 1.75rem;
            }}

            .section, .play-card {{
                padding: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">

        <!-- SECTION 1: Title & Bio -->
        <div class="section">
            <h1>Blueprint GTM Playbook for {company_name}</h1>

            <h2>Who the Hell is Jordan Crawford?</h2>

            <p>Founder of Blueprint GTM. Built a business by scraping 25M+ job posts to find company pain points. Believes the Predictable Revenue model is dead. Thinks mounting an AI SDR on outdated methodology is like putting a legless robot on a horse—no one gets anywhere, and it still shits along the way.</p>

            <p>The core philosophy is simple: The message isn't the problem. The LIST is the message. When you know exactly who to target and why they need you right now, the message writes itself.</p>
        </div>

        <!-- SECTION 2: The Old Way -->
        <div class="section">
            <h2>The Old Way (What Everyone Does)</h2>

            <p>Let's be brutally honest about what your GTM team is doing right now. They're buying lists from ZoomInfo, adding some "personalization" like mentioning a LinkedIn post, then blasting generic messages about features. Here's what it actually looks like:</p>

            <div class="old-way-example">
                <p><strong>The Typical {company_name} SDR Email:</strong></p>
                <div class="message-example">{bad_email}</div>
            </div>

            <p><strong>Why this fails:</strong> The prospect is an expert. They've seen this template 1,000 times. There's zero indication you actually understand their specific situation. It's interruption disguised as personalization. Delete.</p>
        </div>

        <!-- SECTION 3: The New Way -->
        <div class="section">
            <h2>The New Way: Intelligence-Driven GTM</h2>

            <p>Blueprint GTM flips the entire approach. Instead of interrupting prospects with pitches, you deliver insights so valuable they'd pay consulting fees to receive them. You become the person who helps them see around corners, not another vendor in their inbox.</p>

            <p>This requires two fundamental shifts:</p>

            <div class="highlight-box">
                <h3>1. Hard Data Over Soft Signals</h3>
                <p><strong>Stop:</strong> "I see you're hiring compliance people" (job postings - everyone sees this)</p>
                <p><strong>Start:</strong> "Your facility at 1234 Industrial Pkwy received EPA violation #2024-XYZ on March 15th" (government database with record number)</p>
            </div>

            <div class="highlight-box">
                <h3>2. Mirror Situations, Don't Pitch Solutions</h3>
                <p><strong>PQS (Pain-Qualified Segment):</strong> Reflect their exact situation with such specificity they think "how did you know?" Use government data with dates, record numbers, facility addresses.</p>
                <p><strong>PVP (Permissionless Value Proposition):</strong> Deliver immediate value they can use today - analysis already done, deadlines already pulled, patterns already identified - whether they buy or not.</p>
            </div>
        </div>

        <!-- SECTION 4: PQS Examples -->
        <div class="section">
            <h2>{company_name} PQS Plays: Mirroring Exact Situations</h2>

            <p>These messages demonstrate such precise understanding of the prospect's current situation that they feel genuinely seen. Every claim traces to a specific government database with verifiable record numbers.</p>

            {pqs_cards}
        </div>

        <!-- SECTION 5: PVP Examples -->
        <div class="section">
            <h2>{company_name} PVP Plays: Delivering Immediate Value</h2>

            <p>These messages provide actionable intelligence before asking for anything. The prospect can use this value today whether they respond or not. That's the power of permissionless value.</p>

            {pvp_cards}
        </div>

        <!-- SECTION 6: The Transformation -->
        <div class="section">
            <h2>The Transformation</h2>

            <p>Notice the difference? Traditional outreach talks about YOUR product and YOUR benefits. Blueprint GTM talks about THEIR situation and THEIR challenges using verifiable data they can look up themselves.</p>

            <div class="highlight-box">
                <p><strong>The shift is simple but profound:</strong></p>
                <p>Stop sending messages about what you do. Start sending intelligence about what they need to know right now. When you lead with specific data instead of generic pitches, you're not another sales email - you're the person who actually did the research.</p>
            </div>

            <p>This isn't about templates or tactics. It's about building a systematic way to identify prospects experiencing specific, urgent challenges where {company_name}'s solutions provide unique value - and proving you've done the homework with verifiable data.</p>

            <p>The companies that master this approach don't compete on features. They compete on intelligence.</p>
        </div>

    </div>
</body>
</html>'''

    PLAY_CARD_TEMPLATE = '''
            <div class="play-card">
                <div style="margin-bottom: 0.75rem;">
                    <span class="play-type{pvp_class}">{play_type}</span>
                    <span class="score-badge{score_class}">Score: {score}/10</span>
                    <span class="segment-label">{segment}</span>
                </div>
                <h3>{title}</h3>

                <div style="margin-bottom: 0.75rem;">
                    {texada_badges}
                </div>

                <div class="play-explanation">
                    <p><strong>What's the play?</strong> {explanation}</p>
                </div>

                <div class="why-section">
                    <p><strong>Why this works:</strong> {why_works}</p>
                </div>

                <div class="data-sources">
                    <strong>Data Sources:</strong> {data_source}
                </div>

                {calculation_section}

                <p><strong>The message:</strong></p>
                <div class="message-example">Subject: {subject}

{body}</div>
            </div>'''

    CALCULATION_TEMPLATE = '''
                <div class="calculation-worksheet">
                    <h4>📊 Calculation Worksheet</h4>
                    <p>{calculation}</p>
                </div>'''

    def __init__(self):
        pass

    def generate(self, company_context: Dict, messages: List[Dict]) -> str:
        """
        Generate the final HTML playbook.

        Args:
            company_context: Context from Wave 1
            messages: Scored messages from Wave 3

        Returns:
            Complete HTML string
        """
        company_name = company_context.get("company_name", "Company")

        # Separate PQS and PVP messages (allow up to 8 each for more output)
        pqs_messages = self._order_messages([m for m in messages if m.get("type") == "PQS"][:8])
        pvp_messages = self._order_messages([m for m in messages if m.get("type") == "PVP"][:8])

        # Generate bad email example
        bad_email = self._generate_bad_email(company_context)

        # Generate play cards
        pqs_cards = self._generate_cards(pqs_messages, "PQS")
        pvp_cards = self._generate_cards(pvp_messages, "PVP")

        # Fill template
        html = self.TEMPLATE.format(
            company_name=company_name,
            bad_email=bad_email,
            pqs_cards=pqs_cards,
            pvp_cards=pvp_cards
        )

        return html

    def _generate_bad_email(self, context: Dict) -> str:
        """Generate a realistic bad SDR email example."""
        company = context.get("company_name", "Company")
        persona = context.get("persona_title", "there")

        return f"""Subject: Quick Question about {company}

Hi {persona.split()[0] if persona else "there"},

I noticed on LinkedIn that your company recently expanded. Congrats on the growth!

I wanted to reach out because we work with companies like yours to help with {context.get('offering', 'operational challenges')[:50]}.

Our platform offers:
- Feature 1
- Feature 2
- Feature 3

We've helped companies achieve 40% improvement in efficiency.

Would you have 15 minutes next week to explore how we might be able to help?

Best,
Generic SDR"""

    def _generate_cards(self, messages: List[Dict], play_type: str) -> str:
        """Generate HTML play cards for messages."""
        cards = []

        for i, msg in enumerate(messages, 1):
            critique = msg.get("critique", {})
            score = critique.get("average", 0)
            texada = critique.get("texada", {})

            # Determine score badge class
            if score >= 8.0:
                score_class = ""  # Green (default)
            elif score >= 6.5:
                score_class = " medium"  # Yellow
            else:
                score_class = " low"  # Red

            # Generate Texada badges
            texada_badges = self._generate_texada_badges(texada)

            # Generate calculation section if available
            calculation = msg.get("calculation_worksheet", "")
            calculation_section = ""
            if calculation:
                calculation_section = self.CALCULATION_TEMPLATE.format(calculation=calculation)

            # Format data sources with confidence indicators
            data_sources = msg.get("data_sources", ["Government databases"])
            if isinstance(data_sources, list):
                formatted_sources = []
                for ds in data_sources:
                    if isinstance(ds, dict):
                        name = ds.get("name", ds.get("source", "Unknown"))
                        feasibility = ds.get("feasibility", "MEDIUM")
                        conf_class = feasibility.lower()
                        formatted_sources.append(
                            f'{name} <span class="data-confidence {conf_class}">{feasibility}</span>'
                        )
                    else:
                        formatted_sources.append(str(ds))
                data_source_html = ", ".join(formatted_sources)
            else:
                data_source_html = str(data_sources)

            card = self.PLAY_CARD_TEMPLATE.format(
                play_type=play_type,
                pvp_class=" pvp" if play_type == "PVP" else "",
                score=f"{score:.1f}",
                score_class=score_class,
                segment=msg.get("segment", "General"),
                title=f"Play {i}: {msg.get('subject', 'Target Segment')[:50]}",
                texada_badges=texada_badges,
                explanation=msg.get("segment", "Target prospects in this segment."),
                why_works=critique.get("feedback", "Uses specific, verifiable data."),
                data_source=data_source_html,
                calculation_section=calculation_section,
                subject=msg.get("subject", "Subject"),
                body=msg.get("body", "Message body")
            )
            cards.append(card)

        return "\n".join(cards) if cards else "<p>No messages generated for this category.</p>"

    def _generate_texada_badges(self, texada: Dict) -> str:
        """Generate Texada test badges HTML."""
        badges = []

        tests = [
            ("hyper_specific", "Hyper-Specific"),
            ("factually_grounded", "Factually Grounded"),
            ("non_obvious", "Non-Obvious")
        ]

        for key, label in tests:
            passed = texada.get(key, False)
            badge_class = "" if passed else " fail"
            status = "✓" if passed else "✗"
            badges.append(f'<span class="texada-badge{badge_class}">{status} {label}</span>')

        return "".join(badges)

    def _order_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Order messages for maximum impact using primacy/recency effect.

        Strategy: Best first, second-best last, middle scores in between.
        People remember the first and last items best.

        Args:
            messages: List of messages, already sorted by score descending

        Returns:
            Reordered list with best first, second-best last, middle in between
        """
        if len(messages) <= 2:
            return messages

        # Messages should already be sorted by score descending from Wave 3
        # But let's ensure they are
        sorted_msgs = sorted(
            messages,
            key=lambda m: m.get("critique", {}).get("average", 0),
            reverse=True
        )

        # Best goes first
        best = sorted_msgs[0]

        # Second-best goes last
        second_best = sorted_msgs[1]

        # Everything else in the middle
        middle = sorted_msgs[2:]

        # Reorder: best, middle..., second-best
        result = [best] + middle + [second_best]

        return result
