---
name: blueprint-message-generation
description: Generate and validate PQS/PVP outreach messages using buyer role-play critique. Takes pain segments and data sources from previous research, generates 5-7 message variants per type, brutally critiques from buyer perspective, and outputs only top 2-3 messages that score 8+/10. Use after completing blueprint-data-research.
---

# Blueprint GTM Message Generation & Buyer Validation

## Purpose

Transform validated pain segments and hard data sources into Texada-level outreach messages that earn replies. Generate multiple message variants, brutally critique them as the buyer, auto-revise failures, and output only messages that pass the "Would I reply?" test.

This is Stage 3 of the Blueprint GTM Intelligence System.

## Methodology Reference

This skill implements the Blueprint GTM v1.1.0 methodology. For detailed guidance on:
- PVP vs PQS distinction (8.5+ threshold for TRUE PVPs, 7.0-8.4 for Strong PQS)
- Independently Useful Test (complete actionable information requirements)
- Action Extraction & Completeness Check phase
- Buyer critique rubric (5 criteria scoring 0-10 each)
- Texada Test (hyper-specific, factually grounded, non-obvious synthesis)
- Quality gate standards (realistic expectations for TRUE PVPs)

See: `references/methodology.md`

## Core Philosophy

**You are not a copywriter. You are the buyer.**

Your job is to inhabit the target persona completely, generate messages using hard data principles, and answer the only question that matters: **"Would I reply to this?"**

If the answer is "maybe" or "no," you don't flag it for revision—you DESTROY it and rebuild it until it's Texada-level or you admit it can't work.

## When to Use This Skill

- After completing `blueprint-data-research` skill
- User has HIGH feasibility segments with validated data sources
- Need to generate buyer-validated PQS and PVP messages
- Ready to create implementation blueprints for execution

## Requirements

**Input Required:**

### Artifact 1: Company Research Output (from blueprint-company-research)
Must contain:
- Pain-situation segments with specific triggers
- Target persona (job title, responsibilities, pains, expertise level)
- ICP profile (industry, company size, operational context)

### Artifact 2: Data Source Research Output (from blueprint-data-research)
Must contain:
- HIGH feasibility segments only
- Data sources mapped to each segment (government databases with URLs)
- Field-level documentation (ACTUAL field names, not assumed)
- PQS detection recipes (exact filters/queries)
- Reality checks (what's provable vs inferred)

**Dependencies:**
- Must complete `blueprint-company-research` and `blueprint-data-research` first

## Methodology: Six-Phase Process

### Phase 1: Context Extraction & Persona Inhabitation

**Step 1.1: Extract the Target Persona**

From company research, identify:
- Job title (specific, not "decision maker")
- Responsibilities (what they own day-to-day)
- Pain points (what keeps them up at night)
- Expertise level (what they already know - this is CRITICAL)

**Step 1.2: Extract HIGH Feasibility Pain Segments**

From data source research, list ONLY segments rated HIGH feasibility:
- The specific situation/trigger (documented in government database)
- The pain/challenge it creates
- Why it matters to the persona

**If no HIGH feasibility segments exist, STOP and recommend returning to research phases.**

**Step 1.3: Map Data Sources to Segments**

From data source research, for each HIGH segment identify:
- Which specific government database detects this (EPA ECHO, OSHA, FDA, etc.)
- What ACTUAL field names exist (from verified documentation)
- What's provable vs what's inferred
- Example record numbers, violation types, date formats

**Step 1.4: Formally Adopt Buyer Persona**

Write this statement and embody it for the rest of the process:

> "I am now [Job Title] at [Company Type]. My responsibilities include [X, Y, Z]. My biggest pain is [Pain]. I am an expert in [Domain] which means I already know [Common Knowledge]. I receive 50+ sales emails per day, most of which I delete in 2 seconds. For the rest of this skill, I will evaluate every message as THIS person, not as a marketer or copywriter. I will be brutally honest about what would make me reply vs delete."

---

### Phase 2: Generate Message Variants

**For each HIGH feasibility pain segment, generate TWO message types:**

#### Type 1: PQS (Pain-Qualified Segment)
**Goal**: Mirror their exact situation with such data-driven specificity that they think "how did you know?"

**Generate 3-5 PQS variants per segment**, each following POM (Principles of Messaging) structure:

**Format:**
```
Subject: [2-4 words that earn curiosity, NOT understanding]

[Intro: Describe EXACT situation using SPECIFIC data from government database]

[Insight: Share non-obvious consequence or pattern they likely don't see]

[Inquisition: Low-effort "did I get it right?" question]
```

**Subject Line Principles:**
- 2-4 words maximum
- Earn curiosity, not understanding
- Never use template language
- ✅ "3 OSHA serious violations"
- ✅ "EPA citation March 15"
- ✅ "Permit expires in 90"
- ❌ "Important compliance information"
- ❌ "Following up on your facility"

**Intro Principles (CRITICAL - This is Where Data Matters):**
- Reference the EXACT government database
- Use ACTUAL record numbers, violation IDs, dates
- Use facility-specific addresses or identifiers
- Format dates exactly as they appear in database
- Include severity classifications if available
- ✅ "Your facility at 1234 Industrial Pkwy received OSHA citation #987654321 on March 15, 2025 for three serious violations (CFR 1910.147, 1910.212, 1910.305)"
- ✅ "EPA ECHO shows your NPDES permit CA0001234 has 2 quarters in non-compliance (Q3 2024, Q4 2024) for total suspended solids exceedances"
- ❌ "It looks like you might have some compliance issues"
- ❌ "I noticed your facility has safety violations"

**Insight Principles:**
- Connect the data to a consequence they might not see
- Reference patterns from similar companies (if you've researched them)
- Non-obvious synthesis, not obvious advice
- ✅ "Most facilities don't catch this pattern until inspectors return - second violations within 12 months trigger mandatory willful citations with 10x penalties"
- ✅ "This specific combination (lockout + machine guarding + electrical) usually indicates aging equipment from the same era - we see it cluster when facilities hit 15-20 year marks"
- ❌ "This could be a problem for your company"
- ❌ "You should fix these violations"

**Inquisition Principles:**
- "Did I get it right?" style question
- Low effort to answer (yes/no, confirm number, clarify detail)
- NO meeting requests
- NO solution pitches
- ✅ "Did I get the violation count right?"
- ✅ "Is this facility still active?"
- ✅ "Are these the same 3 production lines?"
- ❌ "Would you like to schedule a demo?"
- ❌ "Can we discuss how we help with this?"

**Total Length:** Under 75 words (intro + insight + question)

---

#### Type 2: PVP (Permissionless Value Proposition)
**Goal**: Deliver independent value they can use RIGHT NOW without buying anything

**Generate 3-5 PVP variants per segment**, each following structure:

**Format:**
```
Subject: [2-4 words, earn curiosity]

[Intro: Lead with SPECIFIC value you're offering based on data work already done]

[Insight: Why this value matters in their specific context]

[Inquisition: Who should receive this? Make it easy to forward]
```

**Intro Principles - Lead With Value:**
- Offer something they can use immediately
- Based on work you've already done (not a promise)
- Unique/custom to them (not a generic resource)
- ✅ "I pulled the EPA consent decree milestones for all 3 of your facilities - you have 6 deadlines between now and Q2 2026, with the first one (OU-2 groundwater monitoring well installation) due May 15, 2025"
- ✅ "I cross-referenced your OSHA violations against upcoming CA state inspections - facilities with lockout violations typically get re-inspected within 6-9 months, putting you likely in Q3/Q4 2025 window"
- ❌ "I have valuable compliance insights to share"
- ❌ "I can help you with your violations"

**Insight Principles - Why It Matters:**
- Connect value to their specific situation using data
- Show you understand their constraints/priorities
- Reference specific numbers if available
- ✅ "The May deadline matters because it triggers the quarterly reporting requirement - if you miss it, you're automatically escalated to EPA Region 9 enforcement instead of state-level"
- ✅ "State re-inspections focus on the same systems that failed - I pulled the inspection protocol (Form 33A Section III) and highlighted which of your equipment shows up"
- ❌ "Deadlines are important to track"
- ❌ "This could save you money"

**Inquisition Principles - Facilitate Forwarding:**
- Make it easy to forward internally
- Don't ask for anything in return
- Focus on logistics, not commitment
- ✅ "Who's best to send the deadline calendar to?"
- ✅ "Should this go to your EH&S director or facilities manager?"
- ❌ "Can we schedule a call to discuss?"
- ❌ "Would you like a demo of how we help?"

**Total Length:** Under 100 words

---

### Phase 3: Buyer Role-Play Critique (BRUTAL HONESTY REQUIRED)

**For EVERY message variant you generate, IMMEDIATELY critique it as the buyer persona.**

Use this exact framework:

```
🎭 BUYER CRITIQUE: [Segment Name] - [Message Type] - Variant #[X]

WOULD I REPLY? [YES / MAYBE / NO]

SCORING (as the buyer receiving this):
- Situation Recognition: X/10 (Did they nail MY exact situation with real data?)
- Data Credibility: X/10 (Do I believe they actually have this government data?)
- Insight Value: X/10 (Is this non-obvious to ME given my expertise level?)
- Effort to Reply: X/10 (How brain-dead easy is it to respond?)
- Emotional Resonance: X/10 (Does this hit a real pain I'm feeling?)

OVERALL BUYER SCORE: X.X/10

FAILURE MODES DETECTED:
- [ ] Too vague (lacks hyper-specificity with record numbers/dates)
- [ ] Obvious insight (I already know this as an expert in my field)
- [ ] Data not credible (no specific record numbers, feels generic)
- [ ] Too long (exceeds 75 words for PQS / 100 words for PVP)
- [ ] Talks about sender instead of my problem
- [ ] High effort to reply (unclear what I'd even say)
- [ ] Asks for meeting/demo (I'm not ready for that)
- [ ] Generic/templated (could be sent to anyone in my industry)
- [ ] Relies on soft signals (mentions hiring, funding, growth - lazy research)

TEXADA TEST (The Gold Standard):
- Hyper-specific? [YES/NO + evidence]
  (Does it have actual dates, violation numbers, facility addresses, permit IDs?)
- Factually grounded? [YES/NO + evidence]
  (Does every claim trace to a specific government database field?)
- Non-obvious synthesis? [YES/NO + evidence]
  (Does it reveal a pattern or consequence I wouldn't easily see?)

DATA SOURCE VERIFICATION (CRITICAL):
For EACH claim in the message, verify against data source research:

- Intro claim: "[Exact claim from message]"
  → Database: [Name, e.g., "EPA ECHO"]
  → Field: [Actual field name, e.g., "VIOLATION_DATE"]
  → Status: [✅ Provable / ⚠️ Inferred / ❌ Not Possible from this field]

- Insight claim: "[Exact claim from message]"
  → Database: [Name]
  → Field: [Actual field name]
  → Status: [✅ Provable / ⚠️ Inferred / ❌ Not Possible]

If ANY claim shows ❌ Not Possible, automatic DESTROY verdict.

VERDICT: [KEEP / REVISE / DESTROY]
```

**Verdict Guidelines:**
- **KEEP**: Score ≥ 8.0/10, passes Texada Test, all data ✅ Provable, would definitely reply
- **REVISE**: Score 6.0-7.9/10, fixable issues with data you have, has potential
- **DESTROY**: Score < 6.0/10, fundamental problems OR data claims not provable

---

### Phase 4: Auto-Revision Engine (Maximum 2 Attempts)

**For every message with verdict "REVISE", immediately rebuild it.**

**Revision Process:**
1. Identify the primary failure mode (from critique)
2. Check if it's fixable with data you have (from data source research)
3. If YES → Rewrite addressing the failure, using MORE specific data
4. If NO → Change verdict to DESTROY and explain why data doesn't support this angle
5. Re-critique the revision using same framework
6. If still scores < 8.0 after 2 revisions → DESTROY

**Common Failure Modes & Fixes:**

| Failure Mode | Fix Strategy | Example |
|--------------|--------------|---------|
| Too vague | Add specific record numbers, dates, facility addresses | "violations" → "OSHA citation #987654321 on March 15, 2025" |
| Data not credible | Add exact database name, record ID, field format | "I noticed" → "EPA ECHO shows permit CA0001234" |
| Obvious insight | Research deeper consequences or patterns | "You should fix this" → "Second violations within 12mo trigger mandatory willful citations with 10x penalties" |
| Too long | Cut fluff, keep only data + insight + question | Remove: pleasantries, company descriptions, feature lists |
| Asks for meeting | Change to low-effort question | "Can we talk?" → "Did I get the count right?" |

**Revision Example:**

```
ORIGINAL (Score: 6.5/10):
"I noticed your facility has some safety violations that you should address soon."

FAILURE: Too vague, no data credibility, obvious insight

REVISED (Score: 8.5/10):
"Your facility at 1234 Industrial received OSHA citation #987654321 on 3/15/25 for lockout violations (CFR 1910.147). Most facilities don't know this triggers mandatory re-inspection within 6-9 months. Still using the same equipment?"
```

---

### Phase 5: Select Top Messages

**For each pain segment, select the best messages:**

1. **Rank all KEEP messages by buyer score**
2. **Select top 2-3 messages per segment** (mix of PQS and PVP if possible)
3. **Document why these won:**
   - Specific data points that made them credible
   - Insights that were non-obvious
   - Questions that were brain-dead easy to answer

**Selection Criteria:**
- Diversity: Don't pick 3 nearly-identical messages
- Balance: Ideally 1-2 PQS + 1-2 PVP per segment
- Buyer score: All must be ≥ 8.0/10
- Data quality: All claims must be ✅ Provable

**If you can't find 2-3 KEEP messages for a segment:**
- Document why (data limitations, insight not compelling, etc.)
- Suggest returning to data research phase
- Consider if segment should be rated MEDIUM instead of HIGH

---

### Phase 6: Create Implementation Blueprint

For each final selected message, create execution guidance:

**Implementation Blueprint Format:**

```markdown
## Message: [Segment Name] - [Message Title]

### Message Text
[Full final message]

### Buyer Validation
- Buyer Score: X.X/10
- Why it works: [Specific reasons from critique]

### Data Requirements
**Primary Data Source:**
- Database: [Name with URL]
- Required Fields: [List actual field names]
- Filters Needed: [Specific query criteria]
- Example Query: [Pseudo-code or actual query]

**Data Refresh Cadence:**
- How often to check: [Daily/Weekly/Monthly]
- Based on: [Database update frequency from research]

### Targeting Criteria
Who gets this message:
- Industry: [Specific NAICS codes if applicable]
- Geography: [States, regions, or nationwide]
- Trigger: [Specific data condition that qualifies them]
- Exclusions: [Who NOT to send to]

**Expected Volume:** [Estimate based on data source research]

### Execution Notes
- Best send time: [Based on urgency - immediate for violations, etc.]
- Follow-up: [If no reply, what's appropriate timeline]
- Reply handling: [Common responses to expect]

### Quality Checks
Before sending batch:
- [ ] All data is <30 days old (or specify timeframe)
- [ ] Record numbers verified as current
- [ ] Facility addresses confirmed active
- [ ] No duplicate sends to same company
```

---

## Complete Output Format

Compile everything into a comprehensive message validation report:

```markdown
# Blueprint GTM Message Generation Report: [Company Name]

**Date:** [Today's date]
**Analyst:** [Your name/role]
**Stage:** Message Generation (Stage 3 of 3)

---

## Executive Summary

**Segments Processed:** [Number of HIGH feasibility segments]
**Messages Generated:** [Total variants created]
**Messages Validated:** [Number scoring ≥ 8.0/10]
**Final Selection:** [Number of messages recommended for execution]

**Quality Assessment:**
- Average buyer score: X.X/10
- Data verification: [% of claims fully provable]
- Texada Test pass rate: [X of Y messages]

---

## Persona Context

[Persona statement from Phase 1.4 - who you became for this evaluation]

---

## Segment 1: [Name]

### Selected Message 1: [Type - PQS/PVP] - [Title]

**Final Message:**
```
[Complete message text]
```

**Buyer Critique Summary:**
- Overall Score: X.X/10
- Situation Recognition: X/10
- Data Credibility: X/10
- Insight Value: X/10
- Effort to Reply: X/10
- Emotional Resonance: X/10

**Why This Message Won:**
[2-3 specific reasons it scored highly]

**Data Verification:**
[Table showing each claim verified against government database fields]

**Implementation Blueprint:**
[Complete blueprint from Phase 6]

---

### Selected Message 2: [Type - PQS/PVP] - [Title]
[Same structure]

---

## Segment 2: [Name]
[Same structure for each segment]

---

## Messages Destroyed (For Learning)

**Total Destroyed:** [Number]

**Common Failure Patterns:**
1. [Most common failure mode and count]
2. [Second most common]
3. [Third most common]

**Example Destroyed Message:**
[Show one example with critique explaining why it failed]

---

## Data Source Summary

**Databases Used in Final Messages:**
- [Database 1]: [Number of messages using it]
- [Database 2]: [Number of messages using it]

**Field Verification Rate:**
- ✅ Fully Provable: [X%]
- ⚠️ Inferred: [X%]
- ❌ Not Possible: [0% - should be zero]

---

## Next Steps

**Ready for Execution:**
- [X] messages validated and ready to deploy
- [X] segments with implementation blueprints
- Data sources confirmed accessible

**To Execute:** Use implementation blueprints to build targeting system, pull data, and deploy messages.

**To Optimize:** After first batch, track reply rates by message variant and segment to refine.

**If Results Are Weak:** Return to Stage 1-2 to develop additional segments or improve data quality.
```

---

## Quality Checklist

Before completing, verify:

- [ ] Only HIGH feasibility segments processed
- [ ] Every final message scores ≥ 8.0/10 from buyer perspective
- [ ] All data claims verified as ✅ Provable against government databases
- [ ] No soft signals (job postings, M&A, funding) in any message
- [ ] All messages under length limits (75 words PQS, 100 words PVP)
- [ ] All messages use actual record numbers, dates, violation IDs
- [ ] Implementation blueprints include exact database fields and query logic
- [ ] At least 2 messages selected per HIGH feasibility segment
- [ ] Destroyed messages documented for learning

---

## Common Pitfalls to Avoid

### Mistake 1: Being Too Nice in Critique

**Problem:** Scoring messages 7/10 when they'd actually get deleted

**Solution:** Embody the buyer persona completely - they delete 48 of 50 emails daily

**Example:**
- ❌ "This is pretty good, maybe a 7.5"
- ✅ "Would I actually reply to this? No. I'd delete it. Score: 4/10. DESTROY."

### Mistake 2: Assuming Data Exists

**Problem:** Writing messages that claim data you haven't verified exists

**Solution:** Every claim must trace to an ACTUAL field name from data source research

**Example:**
- ❌ "Your facility has been cited multiple times"
- ✅ "EPA ECHO shows 3 CAA violations (violation IDs: 2024-001, 2024-012, 2024-089)"

### Mistake 3: Obvious Insights

**Problem:** Sharing what the buyer already knows as an expert

**Solution:** Research what they DON'T know - patterns, consequences, deadlines

**Example:**
- ❌ "OSHA violations are serious and should be addressed"
- ✅ "Second citations within 12 months trigger mandatory willful classification with 10x penalties"

### Mistake 4: Asking for Meetings Too Soon

**Problem:** PQS messages that ask for calls instead of confirmation

**Solution:** Low-effort questions only - "did I get this right?"

**Example:**
- ❌ "Can we schedule 15 minutes to discuss?"
- ✅ "Did I get the violation count right?"

### Mistake 5: Generic Value Propositions

**Problem:** PVP messages that offer templates or resources instead of custom work

**Solution:** Lead with specific value already created using their data

**Example:**
- ❌ "I can share our compliance checklist with you"
- ✅ "I pulled the EPA consent decree milestones for all 3 of your facilities - 6 deadlines between now and Q2 2026"

---

## Integration with Other Skills

**This Skill Receives From:**
- `blueprint-company-research`: Persona, pain segments, ICP context
- `blueprint-data-research`: HIGH feasibility segments, data sources, field names

**This Skill Feeds Into:**
- `blueprint-explainer-builder`: Top validated messages for HTML document

**Expected Usage Pattern:**
```
User has HIGH feasibility segments from data research
→ Claude recognizes need for message generation
→ Automatically invokes this skill
→ Produces validated messages with implementation blueprints
→ Claude recognizes messages are ready
→ Automatically invokes blueprint-explainer-builder to create final HTML
```

---

## Tips for Consultants

1. **Be the buyer, not the seller**: Delete-level honesty is required
2. **Verify every data claim**: If you can't cite the database field, don't write it
3. **Destroy bad messages**: 60-70% of first drafts should be destroyed
4. **Use actual examples**: Real violation numbers, real dates, real addresses
5. **Test the "would I reply?" question**: If "maybe", that's a "no"
6. **Reference the Texada Test**: Hyper-specific, factually grounded, non-obvious
7. **Don't pitch solutions**: PQS mirrors situations, PVP delivers value, neither sells

---

## References

- See `references/TEXADA_TEST.md` for gold standard message examples with analysis
- See `references/MESSAGE_PRINCIPLES.md` for PQS vs PVP differences and POM structure
- See `references/BUYER_CRITIQUE_FRAMEWORK.md` for deeper dive on evaluation methodology
- See `examples/overjet/messages.md` for real-world example including destroyed messages
