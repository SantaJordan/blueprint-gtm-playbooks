"""
Wave 3: Message Generation + Buyer Critique (PARALLELIZED)

Generates PQS and PVP messages for validated segments,
then critiques them from the buyer's perspective.

OPTIMIZATION: All Claude API calls run in parallel via asyncio.gather()
- Before: 4 segments × (PQS + PVP + Critique) = 12 sequential calls (~28 min)
- After: 3 parallel batches = ~7 min (4x faster)
"""
from typing import Dict, List, Tuple
import re
import asyncio


class Wave3Messages:
    """Wave 3: Generate and validate messages for each segment."""

    PQS_PROMPT = """Generate a PQS (Pain-Qualified Segment) message for this segment.

SEGMENT: {segment_name}
DESCRIPTION: {segment_description}
DATA SOURCES: {data_sources}
FIELDS: {fields}

TARGET PERSONA: {persona_title}
COMPANY OFFERING: {offering}

=== PQS MESSAGE RULES ===

FORMAT:
- Subject: 2-4 words max, specific situation reference
- Intro: Exact data mirror with SPECIFIC identifiers (see examples below)
- Insight: Non-obvious synthesis the persona doesn't already know
- Question: Low-effort question to spark reply
- Length: Under 75 words total

MANDATORY REQUIREMENTS:
1. NEVER use placeholders: [X], [company_name], [similar company], [specific data] → AUTO-FAIL
2. MUST include at least ONE specific identifier (examples):
   - Record/case numbers: "solicitation #W912QR-25-R-0047"
   - Dates: "March 14, 2025" (not "recently" or "last month")
   - Addresses: "1847 Main St, Denver" (not "your facility")
   - License numbers: "NPI 1234567890"
   - Dollar amounts: "$847,000" (not "significant amount")

3. MUST trace every claim to a data source from FIELDS above
4. Mirror their EXACT situation, don't pitch anything

CALCULATION WORKSHEET (required for any numeric claim):
Example: "8 AEs × 6 hours/week = 48 hours saved monthly"
Format: [number] × [rate] = [result] from [source]

=== GOOD vs BAD EXAMPLES ===

BAD (fails - uses placeholders):
"I noticed [company_name] has been expanding..."
"Your team spends [X] hours on manual work..."

GOOD (passes - uses specifics):
"Your February 12 permit filing for 1847 Main St requires OSHA 30-hour certification..."
"Solicitation #W912QR-25-R-0047 closes in 18 days with 12 competitors already..."

Generate 4 PQS message variants with DIFFERENT angles:

PQS_VARIANT_1:
Subject: [2-4 words only]
Body: [full message with specific data - NO placeholders]
Calculation_Worksheet: [if any numeric claims, show the math]

PQS_VARIANT_2:
Subject: [2-4 words only]
Body: [full message with specific data - NO placeholders]
Calculation_Worksheet: [if any numeric claims, show the math]

PQS_VARIANT_3:
Subject: [2-4 words only]
Body: [full message with specific data - NO placeholders]
Calculation_Worksheet: [if any numeric claims, show the math]

PQS_VARIANT_4:
Subject: [2-4 words only]
Body: [full message with specific data - NO placeholders]
Calculation_Worksheet: [if any numeric claims, show the math]"""

    PVP_PROMPT = """Generate a PVP (Permissionless Value Proposition) message for this segment.

SEGMENT: {segment_name}
DESCRIPTION: {segment_description}
DATA SOURCES: {data_sources}
FIELDS: {fields}

TARGET PERSONA: {persona_title}
COMPANY OFFERING: {offering}

=== PVP MESSAGE RULES ===

FORMAT:
- Subject: Specific value being offered (the deliverable, not a pitch)
- Intro: What you're giving them RIGHT NOW (already done, not an offer to do)
- Insight: Why this matters to them specifically (with their data)
- Question: Who should receive this? (route to right person)
- Length: Under 100 words total

MANDATORY REQUIREMENTS:
1. NEVER use placeholders: [X], [company_name], [similar company] → AUTO-FAIL
2. MUST deliver IMMEDIATE usable value:
   - "I pulled your 3 upcoming deadlines: March 14, April 2, May 9..."
   - "Your competitor analysis: 12 companies in NAICS 541330 with >$5M revenue..."
   - "Benchmark comparison: Your 3.2 stars vs. county median 4.1..."

3. Analysis ALREADY DONE (not an offer to analyze)
4. Include specific: dates, dollar amounts, percentages, record numbers

CALCULATION WORKSHEET (required for any numeric claim):
Example: "3 facilities × 4.2 avg deficiencies = 12.6 annual citations at ~$2,400 each = $30,240 exposure"
Format: [number] × [rate] = [result] → [implication] from [source]

=== GOOD vs BAD EXAMPLES ===

BAD (fails - offer to help):
"We can help you analyze your competitor landscape..."
"Would you like me to pull your deadline data?"

GOOD (passes - value already delivered):
"Your March 28 CMS audit has 3 deficiencies still open from October..."
"I found 8 active federal opportunities in NAICS 541330 closing Q2 - here's the list..."

Generate 4 PVP message variants with DIFFERENT value offerings:

PVP_VARIANT_1:
Subject: [specific value deliverable]
Body: [full message with specific data - NO placeholders]
Calculation_Worksheet: [show the math for any numeric claims]
Data_Sources_Used: [which APIs/databases this comes from]

PVP_VARIANT_2:
Subject: [specific value deliverable]
Body: [full message with specific data - NO placeholders]
Calculation_Worksheet: [show the math for any numeric claims]
Data_Sources_Used: [which APIs/databases this comes from]

PVP_VARIANT_3:
Subject: [specific value deliverable]
Body: [full message with specific data - NO placeholders]
Calculation_Worksheet: [show the math for any numeric claims]
Data_Sources_Used: [which APIs/databases this comes from]

PVP_VARIANT_4:
Subject: [specific value deliverable]
Body: [full message with specific data - NO placeholders]
Calculation_Worksheet: [show the math for any numeric claims]
Data_Sources_Used: [which APIs/databases this comes from]"""

    CRITIQUE_PROMPT = """Adopt this buyer persona and brutally critique these messages.

PERSONA: {persona_title}
RESPONSIBILITIES: {persona_responsibilities}
KPIs: {persona_kpis}

"I am now {persona_title}. I receive 50+ sales emails per day. I delete 95% without reading.
I only respond to emails that:
1. Mirror an exact situation I'm in RIGHT NOW
2. Contain data I can verify and don't already have
3. Offer a non-obvious insight I haven't considered
4. Require minimal effort to reply

I am NOT a marketer evaluating this message. I AM THE BUYER. Would I reply to this?
If 'maybe'—that's a NO."

MESSAGES TO CRITIQUE:
{messages}

=== AUTOMATIC DISQUALIFICATION ===

Check FIRST for these instant-fail conditions:
- Contains [X] or [company_name] or [similar company] → AUTO-DESTROY (score 0)
- Uses "recently", "many", "some", "significant" without specific numbers → Score 2 max
- Makes claims without traceable data source → Score 3 max

=== SCORING (only if no auto-disqualification) ===

Score each message (0-10 on 5 criteria):
1. Situation Recognition: Does this mirror my EXACT current situation? Generic=0, Hyper-specific=10
2. Data Credibility: Can I verify this data? Is it from trusted source? Assumed=0, Provable=10
3. Insight Value: Is this non-obvious synthesis I don't already know? Obvious=0, Revelation=10
4. Effort to Reply: How easy to respond? High friction=0, One-word answer=10
5. Emotional Resonance: Does this trigger urgency or curiosity? Meh=0, Must investigate=10

=== TEXADA TEST ===

Apply Texada Test for each:
- Hyper-specific: Contains dates (March 14), record numbers (#W912QR), dollar amounts ($847K)?
  FAIL if: uses "recent", "many", "some", "significant" without numbers
- Factually grounded: Every claim traces to documented data source (API field name)?
  FAIL if: can't name the API or database for each fact
- Non-obvious synthesis: Insight persona doesn't already have access to?
  FAIL if: information is on their own website or obvious industry knowledge

=== OUTPUT FORMAT ===

For EACH message:
MESSAGE: [which one]
PLACEHOLDER_CHECK: PASS / AUTO-DESTROY (contains [X], [company_name], etc.)
SCORES:
- Situation Recognition: [0-10]
- Data Credibility: [0-10]
- Insight Value: [0-10]
- Effort to Reply: [0-10]
- Emotional Resonance: [0-10]
AVERAGE: [calculated average]
TEXADA:
- Hyper-specific: PASS/FAIL [with evidence]
- Factually grounded: PASS/FAIL [with evidence]
- Non-obvious: PASS/FAIL [with evidence]
VERDICT: KEEP (≥8.0) / REVISE (6.5-7.9) / DESTROY (<6.5)
FEEDBACK: [specific improvement needed to make me reply]"""

    def __init__(self, claude_client):
        self.claude = claude_client

    async def generate(self, segments: List[Dict], company_context: Dict) -> List[Dict]:
        """
        Generate and critique messages for all segments IN PARALLEL.

        ULTRA-AGGRESSIVE PARALLELIZATION:
        - Step 1: Generate ALL PQS + PVP messages in ONE batch (8 concurrent calls)
        - Step 2: Critique ALL segments in parallel (4 concurrent calls)

        Before: 3 parallel batches (~7 min each) = ~21 min
        After: 2 parallel batches (~5 min each) = ~10 min

        Args:
            segments: Validated segments from Hard Gates
            company_context: Context from Wave 1

        Returns:
            List of messages with scores, sorted by quality
        """
        if not segments:
            return []

        print(f"[Wave 3] ULTRA-PARALLEL: Generating messages for {len(segments)} segments...")

        # Step 1: Generate ALL PQS + PVP messages simultaneously (8 concurrent API calls)
        print(f"[Wave 3] Step 1/2: Generating {len(segments) * 2} message sets in parallel (PQS + PVP together)...")
        pqs_tasks = [self._generate_pqs(seg, company_context) for seg in segments]
        pvp_tasks = [self._generate_pvp(seg, company_context) for seg in segments]

        # Run all 8 calls at once
        all_results = await asyncio.gather(*pqs_tasks, *pvp_tasks, return_exceptions=True)

        # Split results back into PQS and PVP
        all_pqs_results = all_results[:len(segments)]
        all_pvp_results = all_results[len(segments):]

        # Combine PQS + PVP for each segment (for critique)
        segment_messages: List[Tuple[Dict, List[Dict], List[Dict]]] = []
        for i, segment in enumerate(segments):
            pqs_msgs = all_pqs_results[i] if not isinstance(all_pqs_results[i], Exception) else []
            pvp_msgs = all_pvp_results[i] if not isinstance(all_pvp_results[i], Exception) else []
            if pqs_msgs or pvp_msgs:
                segment_messages.append((segment, pqs_msgs, pvp_msgs))

        # Step 2: Critique ALL segments in parallel (switched to Sonnet for speed)
        print(f"[Wave 3] Step 2/2: Critiquing {len(segment_messages)} message sets in parallel...")
        critique_tasks = [
            self._critique_messages(pqs + pvp, company_context)
            for (seg, pqs, pvp) in segment_messages
        ]
        all_critiques = await asyncio.gather(*critique_tasks, return_exceptions=True)

        # Assemble final messages with critiques
        all_messages = []
        for idx, (segment, pqs_msgs, pvp_msgs) in enumerate(segment_messages):
            critiques = all_critiques[idx] if not isinstance(all_critiques[idx], Exception) else []

            combined_msgs = pqs_msgs + pvp_msgs
            for i, msg in enumerate(combined_msgs):
                if i < len(critiques):
                    msg["critique"] = critiques[i]
                    msg["segment"] = segment.get("name", f"Segment {idx + 1}")
                    msg["type"] = "PQS" if i < len(pqs_msgs) else "PVP"
                    all_messages.append(msg)

        print(f"[Wave 3] Generated {len(all_messages)} total messages")

        # Filter to keep only messages scoring ≥6.5 (lowered from 7.0 for more output)
        passing_messages = [
            m for m in all_messages
            if m.get("critique", {}).get("average", 0) >= 6.5
        ]

        # Sort by score (best first)
        passing_messages.sort(
            key=lambda m: m.get("critique", {}).get("average", 0),
            reverse=True
        )

        print(f"[Wave 3] {len(passing_messages)} messages passed quality threshold (≥6.5)")

        return passing_messages

    async def _generate_pqs(self, segment: Dict, context: Dict) -> List[Dict]:
        """Generate PQS messages for a segment."""
        prompt = self.PQS_PROMPT.format(
            segment_name=segment.get("name", ""),
            segment_description=segment.get("description", ""),
            data_sources=", ".join(segment.get("data_sources", [])),
            fields=", ".join(segment.get("fields", [])),
            persona_title=context.get("persona_title", ""),
            offering=context.get("offering", "")
        )

        response = await self.claude.messages.create(
            model="claude-opus-4-20250514",  # Maximum quality for paying customers
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_messages(response.content[0].text, "PQS")

    async def _generate_pvp(self, segment: Dict, context: Dict) -> List[Dict]:
        """Generate PVP messages for a segment."""
        prompt = self.PVP_PROMPT.format(
            segment_name=segment.get("name", ""),
            segment_description=segment.get("description", ""),
            data_sources=", ".join(segment.get("data_sources", [])),
            fields=", ".join(segment.get("fields", [])),
            persona_title=context.get("persona_title", ""),
            offering=context.get("offering", "")
        )

        response = await self.claude.messages.create(
            model="claude-opus-4-20250514",  # Maximum quality for paying customers
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_messages(response.content[0].text, "PVP")

    async def _critique_messages(self, messages: List[Dict], context: Dict) -> List[Dict]:
        """Critique all messages from buyer perspective."""
        messages_text = ""
        for i, msg in enumerate(messages, 1):
            messages_text += f"\nMESSAGE {i} ({msg.get('type', 'Unknown')}):\n"
            messages_text += f"Subject: {msg.get('subject', '')}\n"
            messages_text += f"Body: {msg.get('body', '')}\n"

        prompt = self.CRITIQUE_PROMPT.format(
            persona_title=context.get("persona_title", "Decision Maker"),
            persona_responsibilities=context.get("persona", ""),
            persona_kpis=", ".join(context.get("persona_kpis", [])),
            messages=messages_text
        )

        response = await self.claude.messages.create(
            model="claude-opus-4-20250514",  # Maximum quality for paying customers
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_critiques(response.content[0].text, len(messages))

    def _parse_messages(self, text: str, msg_type: str) -> List[Dict]:
        """Parse generated messages from response."""
        messages = []

        # Find message variants
        pattern = rf'{msg_type}_VARIANT_(\d+)[:\s]+(.+?)(?={msg_type}_VARIANT_|$)'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

        for _, content in matches:
            msg = {"type": msg_type, "subject": "", "body": ""}

            # Extract subject
            subject_match = re.search(r'Subject[:\s]+(.+?)(?=\n|Body|$)', content)
            if subject_match:
                msg["subject"] = subject_match.group(1).strip()

            # Extract body
            body_match = re.search(r'Body[:\s]+(.+?)$', content, re.DOTALL)
            if body_match:
                msg["body"] = body_match.group(1).strip()

            if msg["subject"] or msg["body"]:
                messages.append(msg)

        return messages

    def _parse_critiques(self, text: str, expected_count: int) -> List[Dict]:
        """Parse critique results for each message."""
        critiques = []

        # Split by MESSAGE blocks
        message_blocks = re.split(r'MESSAGE[:\s]*\d*', text, flags=re.IGNORECASE)

        for block in message_blocks[1:expected_count + 1]:  # Skip first empty split
            critique = {
                "scores": {
                    "situation_recognition": 0,
                    "data_credibility": 0,
                    "insight_value": 0,
                    "effort_to_reply": 0,
                    "emotional_resonance": 0
                },
                "average": 0,
                "texada": {
                    "hyper_specific": False,
                    "factually_grounded": False,
                    "non_obvious": False
                },
                "verdict": "DESTROY",
                "feedback": ""
            }

            # Parse scores
            score_patterns = {
                "situation_recognition": r"Situation Recognition[:\s]+(\d+)",
                "data_credibility": r"Data Credibility[:\s]+(\d+)",
                "insight_value": r"Insight Value[:\s]+(\d+)",
                "effort_to_reply": r"Effort to Reply[:\s]+(\d+)",
                "emotional_resonance": r"Emotional Resonance[:\s]+(\d+)"
            }

            total = 0
            for key, pattern in score_patterns.items():
                match = re.search(pattern, block, re.IGNORECASE)
                if match:
                    score = min(10, max(0, int(match.group(1))))
                    critique["scores"][key] = score
                    total += score

            critique["average"] = total / 5 if total > 0 else 0

            # Parse average if explicitly stated
            avg_match = re.search(r"AVERAGE[:\s]+(\d+(?:\.\d+)?)", block, re.IGNORECASE)
            if avg_match:
                critique["average"] = float(avg_match.group(1))

            # Parse Texada
            texada_match = re.search(r"TEXADA[:\s]+(.+?)(?=VERDICT|FEEDBACK|$)", block, re.DOTALL | re.IGNORECASE)
            if texada_match:
                texada_text = texada_match.group(1).lower()
                critique["texada"]["hyper_specific"] = "pass" in texada_text and "specific" in texada_text
                critique["texada"]["factually_grounded"] = "pass" in texada_text and "grounded" in texada_text
                critique["texada"]["non_obvious"] = "pass" in texada_text and "obvious" in texada_text

            # Parse verdict
            verdict_match = re.search(r"VERDICT[:\s]+(KEEP|REVISE|DESTROY)", block, re.IGNORECASE)
            if verdict_match:
                critique["verdict"] = verdict_match.group(1).upper()

            # Parse feedback
            feedback_match = re.search(r"FEEDBACK[:\s]+(.+?)$", block, re.DOTALL)
            if feedback_match:
                critique["feedback"] = feedback_match.group(1).strip()[:300]

            critiques.append(critique)

        return critiques
