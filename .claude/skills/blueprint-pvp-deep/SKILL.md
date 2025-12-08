---
name: blueprint-pvp-deep
description: Autonomous PVP generation agent that validates context, explores non-obvious data synthesis, infers internal data opportunities, and evaluates from buyer perspective to deliver 5 Gold Standard PVPs (8.0+ quality). Can be run standalone or invoked by blueprint-turbo.
---

# Blueprint PVP Deep Generation

**Mission:** Generate 5 Gold Standard PVPs (8.0+ buyer evaluation score) through rigorous context validation, deep data synthesis, internal data inference, and brutal buyer-perspective evaluation.

**Time:** 10-17 minutes (depending on context gathering needs)

**Output:** 5 PVPs scoring 8.0+ with complete data feasibility validation

---

## Process Overview

**Phase 0: Context Validation & Gathering** (2-5 min)
- Validate we have sufficient context
- Invoke Turbo modules if needed
- Infer internal data possibilities

**Phase 1: Deep Data Synthesis** (3-4 min)
- Use Sequential Thinking for non-obvious connections
- Explore weird data combinations
- Generate 8-12 synthesis insights

**Phase 1.5: Hard Gate Validation** (1-2 min) ⭐ NEW
- Validate ALL insights against 4 mandatory hard gates
- AUTO-DESTROY insights that fail any gate
- Ensure only regulated niches with data moats proceed

**Phase 2: PVP Concept & Message Drafting** (2-3 min)
- Draft concept + 3-paragraph message for each validated insight
- Follow strict PVP format criteria

**Phase 3: Immediate Buyer Evaluation (CYNICAL BUYER)** (2-3 min)
- Role-play as EXHAUSTED, SKEPTICAL persona AFTER EACH draft
- Score against 7 criteria (1-10 scale) + 3 mandatory litmus tests
- 8.0+ = KEEP, 7.0-7.9 = REVISE ONCE, <7.0 = DESTROY

**Phase 4: Selection & Feasibility Validation** (1-2 min)
- Select top 5 scoring 8.0+
- Validate data feasibility
- Document implementation path

---

## PHASE 0: Context Validation & Gathering

**Objective:** Ensure we have Gold Standard context before attempting PVP generation

### Step 1: Check Available Context

Review what context is available:
- [ ] Company context (name, offering, business model, value prop)
- [ ] ICP profile (industries, scale, pains, operational context)
- [ ] Target persona (job title, responsibilities, KPIs, pains)
- [ ] Data landscape (catalog of sources with feasibility ratings)
- [ ] Pain segments (optional - can generate if missing)

### Step 2: Validate Context Quality

Load and apply: `.claude/skills/blueprint-pvp-deep/prompts/context-validation-rubric.md`

For each category, assess:
- **Company Context:** PASS / NEEDS MORE
- **ICP Profile:** PASS / NEEDS MORE
- **Target Persona:** PASS / NEEDS MORE
- **Data Landscape:** PASS / NEEDS MORE
- **Pain Segments:** AVAILABLE / MISSING

**Overall Readiness:**
- 5/5 or 4/5 categories PASS → ✅ **PROCEED**
- 3/5 categories PASS → ⚠️ **MARGINAL** (recommend gathering more)
- <3 categories PASS → ❌ **INSUFFICIENT** (MUST gather more)

### Step 3: Gather Missing Context (If Needed)

**If Company Context = NEEDS MORE:**
```
Read and execute: .claude/skills/blueprint-turbo/modules/wave1-company-research.md

Input: Company URL (request from user if not provided)
Output: Structured company/ICP/persona profile
```

**If Data Landscape = NEEDS MORE:**
```
Read and execute: .claude/skills/blueprint-turbo/modules/wave2-data-landscape.md

Input: Industry/ICP from company research
Output: Data source catalog with feasibility ratings
```

**If Pain Segments = MISSING:**
```
Read and execute: .claude/skills/blueprint-turbo/modules/synthesis-segments.md

Input: Company + ICP + Data landscape
Output: 2-3 pain segments with data combinations
```

### Step 4: Internal Data Inference

Load and apply: `.claude/skills/blueprint-pvp-deep/prompts/internal-data-inference.md`

Based on sender's business model, infer:
1. **Operational Data They MUST Have** (10-15 types)
2. **Aggregatable Data** (what can be ethically aggregated)
3. **Pain-to-Data Mapping** (which data addresses which pains)
4. **Internal Data PVP Concepts** (3-5 concepts)

Label each:
- **INTERNAL DATA - Ready NOW** (sender has 100+ customers)
- **INTERNAL DATA - Ready at SCALE** (sender needs more customers)
- **INTERNAL DATA + PUBLIC - Hybrid** (combines internal + public)

### Phase 0 Output

```markdown
# Phase 0 Complete: Context Validation

## Validation Results
**Company Context:** ✅ PASS
**ICP Profile:** ✅ PASS
**Target Persona:** ✅ PASS
**Data Landscape:** ✅ PASS
**Pain Segments:** ✅ AVAILABLE

**Overall Readiness:** ✅ EXCELLENT (5/5)

## Context Summary

**Company:** [Name - Business Model]
**Core Offering:** [1-2 sentences]

**ICP:**
- Industries: [Specific industries]
- Key Pains: [Top 3-5]

**Persona:**
- Job Title: [Specific title]
- Top Pains: [Top 3]
- KPIs: [What they're measured on]

**Data Landscape:**
- Total sources: [N]
- HIGH feasibility: [N]
- MEDIUM feasibility: [N]

**Internal Data Opportunities:**
- [3-5 internal data types sender would have]
- [Mapped to persona pains]

## Proceeding to Phase 1: Deep Data Synthesis
```

---

## PHASE 1: Deep Data Synthesis

**Objective:** Generate 8-12 non-obvious insights through creative data synthesis

### Load Resources

- `.claude/skills/blueprint-pvp-deep/prompts/data-synthesis-patterns.md`
- `.claude/skills/blueprint-pvp-deep/examples/gold-standard-pvps.md`

### Use Sequential Thinking MCP

Invoke: `mcp__sequential-thinking__sequentialthinking`

**Prompt Template:**
```
I need to generate 8-12 non-obvious data synthesis insights for [COMPANY NAME] that could become Gold Standard PVPs (8.0+).

CONTEXT:
[Include company, ICP, persona, data sources, internal data opportunities from Phase 0]

TASK: Use sequential thinking to explore data combinations and generate insights.

SYNTHESIS PATTERNS TO CONSIDER:
1. Cross-Reference (matching entities across databases)
2. Temporal Correlation (timing patterns)
3. Competitive Benchmarking (position vs market)
4. Velocity Detection (rate of change)
5. Geo-Clustering (spatial density)
6. Cascade Detection (upstream → downstream)
7. Absence as Signal (what's missing)
8. Threshold Crossing (tipping points)
9. Multi-Source Triangulation (3+ sources)
10. Internal + Public Hybrid (unique advantage)

REQUIREMENTS:
- Each insight MUST combine 2-3 data sources
- Must be NON-OBVIOUS (persona doesn't already know)
- Must be HYPER-SPECIFIC (actual values, not vague)
- Must be VERIFIABLE (persona can check if they want)
- Must address a PERSONA PAIN from context
- Include both PUBLIC-only and INTERNAL+PUBLIC insights

THOUGHT PROCESS:
- Thought 1-2: Review data sources and persona pains
- Thought 3-7: Explore 5+ different data combinations using patterns above
- Thought 8-12: Evaluate which combinations create non-obvious insights
- Thought 13-15: Select top 8-12 insights that pass criteria

OUTPUT: 8-12 synthesis insights, each with:
- Insight description
- Data sources used (with specific fields)
- Synthesis pattern applied
- Persona pain addressed
- Why non-obvious (what asymmetry it bridges)
- Confidence level (90%+ pure gov, 60-75% hybrid, etc.)
```

### Validate Each Insight

For each of the 8-12 insights, verify:
- [ ] Combines 2-3 data sources (not single source)
- [ ] Uses specific values (not "many", "recent", "growing")
- [ ] Non-obvious (persona unlikely to discover alone)
- [ ] Addresses persona pain from Phase 0
- [ ] Data sources are available (from Phase 0 catalog)

### Phase 1 Output

```markdown
# Phase 1 Complete: Deep Data Synthesis

## Generated 12 Synthesis Insights

### Insight 1: [Title]
**Data Sources:**
- [Source 1] - [Fields]
- [Source 2] - [Fields]

**Synthesis Pattern:** [Pattern name]

**Non-Obvious Because:** [What asymmetry]

**Persona Pain Addressed:** [Pain from Phase 0]

**Confidence Level:** [90%+ / 60-75% / etc.]

**Data Type:** [Public Only / Internal Only / Hybrid]

[Repeat for all 12 insights]

## Proceeding to Phase 1.5: Hard Gate Validation
```

---

## PHASE 1.5: Hard Gate Validation (MANDATORY)

**Objective:** Validate ALL synthesis insights against 5 hard gates before drafting PVPs. AUTO-DESTROY any insight that fails.

### Invoke Validator Skill

```
→ Invoke: Skill(skill: "blueprint-validator")
→ Pass:
  - Mode: SEGMENT_VALIDATION
  - Product Context: core_problem, valid_domains, invalid_domains (from Phase 0)
  - Segments: all synthesis insights from Phase 1
→ Receive:
  - VALIDATED_SEGMENTS: insights that passed all 5 gates
  - REJECTED_SEGMENTS: insights that failed (with reasons)
  - REVISION_CANDIDATES: insights that can be revised (Gate 3 or 4 failures only)
```

### Validate EACH Insight Against 4 Gates

For EACH of the 8-12 insights from Phase 1:

**Gate 1: Horizontal Disqualification**
- Question: Is the ICP operationally specific?
- FAIL if: "Any B2B company," "SaaS companies," "Sales teams" (generic)
- PASS if: Specific industry with regulatory oversight + observable pain

**Gate 2: Causal Link Constraint**
- Question: Does the signal DIRECTLY PROVE the pain?
- Test: "Could they have this signal but NOT have the pain?" If YES = FAIL
- BANNED: Funding, hiring, expansion, M&A, job postings, tech stack
- ALLOWED: EPA violations, CMS ratings, FMCSA ratings, license deadlines

**Gate 3: No Aggregates Ban**
- Question: Are ALL statistics company-specific?
- FAIL if: "Industry average is X%," "Companies like yours typically..."
- PASS if: "Your [specific metric] vs [benchmark]"

**Gate 4: Technical Feasibility Audit**
- Question: Can you explain MECHANICALLY how to detect this data?
- Must answer: Data source? Specific field? Access method? Detection footprint?
- FAIL if: Undetectable claims (CRM data, sales cycle, employee satisfaction)

### Validation Output Format

```markdown
## Hard Gate Validation: Insight #[N]

**Insight:** [Title]

**Gate 1 (Horizontal):** ✅ PASS / ❌ FAIL
- ICP: [specific description]
- Rationale: [why]

**Gate 2 (Causal Link):** ✅ PASS / ❌ FAIL
- Signal: [what data signal]
- "Could have signal without pain?": YES/NO
- Rationale: [why]

**Gate 3 (Aggregates):** ✅ PASS / ❌ FAIL
- Statistics used: [list]
- Company-specific?: YES/NO
- Rationale: [why]

**Gate 4 (Feasibility):** ✅ PASS / ❌ FAIL
- Data claims: [list]
- Detection mechanism: [API/selector for each]
- Rationale: [why]

**VERDICT:** ✅ PROCEED to Phase 2 / ❌ AUTO-DESTROY
```

### Decision Logic

| Result | Action |
|--------|--------|
| All 4 gates PASS | ✅ Proceed to Phase 2 |
| Gate 3 only fails | ONE revision attempt (add specific data) |
| Gate 4 only fails | ONE revision attempt (substitute data source) |
| Gate 1 or 2 fails | ❌ DESTROY immediately (fundamental flaw) |
| 2+ gates fail | ❌ DESTROY immediately |
| Still fails after revision | ❌ DESTROY (no second attempt) |

### Phase 1.5 Output

```markdown
# Phase 1.5 Complete: Hard Gate Validation

## Validation Results

**Total Insights Evaluated:** 12
**Passed All 4 Gates:** 8
**Destroyed (Gate failures):** 4

### Destroyed Insights:
- Insight #3: Failed Gate 2 (signal = hiring, doesn't prove pain)
- Insight #7: Failed Gate 4 (CRM data quality undetectable)
- Insight #9: Failed Gate 1 (horizontal ICP "B2B companies")
- Insight #11: Failed Gate 3 (used industry-wide stats)

### Validated Insights Proceeding to Phase 2:
1. [Insight #1] - All gates passed
2. [Insight #2] - All gates passed
...

## Proceeding to Phase 2 with 8 validated insights
```

---

## PHASE 2: PVP Concept & Message Drafting

**Objective:** Draft complete PVP concept + 3-paragraph message for EACH of the 8-12 insights

### Drafting Requirements

For EACH insight from Phase 1, create:

**PVP Concept:**
- **Title:** [Descriptive name]
- **Target Persona:** [Job title from Phase 0]
- **Core Insight:** [The synthesis from Phase 1]
- **Data Basis:** [Specific sources + fields]
- **Value Proposition:** [What benefit to persona]
- **Low-Effort CTA:** [Specific, simple action]

**Draft Message:**
- **Format:** 3 paragraphs, <100 words, 8th-grade level
- **Para 1 (Data Hook):** Lead with most compelling, specific data point
- **Para 2 (Value):** State immediate, tangible benefit
- **Para 3 (CTA):** Provide specific, low-effort Call-to-Action

**Message Criteria:**
- Subject: 2-5 words, specific
- Tone: Helpful, direct, peer-to-peer
- No generic CTAs ("click here", "let's discuss")
- Specific CTAs ("Reply for the list of X?", "Want intro to [Name]?")

### Drafting Example Template

```markdown
## PVP Concept 1: [Title]

**Target Persona:** [Job Title]
**Core Insight:** [Synthesis insight]
**Data Basis:** [Sources + fields]
**Value Proposition:** [Benefit]
**Low-Effort CTA:** [Action]

**DRAFT MESSAGE:**

> Subject: [2-5 words]
>
> [Data Hook paragraph - hyper-specific, verifiable data point]
>
> [Value paragraph - direct benefit to them specifically]
>
> [CTA paragraph - low-effort, specific action]

[Repeat for all 8-12 insights]
```

### Phase 2 Output

```markdown
# Phase 2 Complete: PVP Drafting

## Drafted 12 PVP Concept + Message Pairs

[All 12 concepts with complete draft messages]

## Proceeding to Phase 3: Buyer Evaluation
```

---

## PHASE 3: Immediate Buyer Evaluation (CYNICAL BUYER)

**Objective:** Evaluate EACH PVP from CYNICAL buyer perspective immediately after drafting (not batched)

### Load Evaluation Rubric

Read: `.claude/skills/blueprint-pvp-deep/prompts/buyer-evaluation-rubric.md`

### Evaluation Process (Per PVP)

**Step 1: CYNICAL BUYER Persona Adoption (Mandatory)**

Before evaluating, fully adopt the EXHAUSTED, SKEPTICAL persona:
```
"I am [SPECIFIC JOB TITLE] at [TYPICAL ICP COMPANY].

I am EXHAUSTED. I receive 150+ emails per day, 80% are unsolicited sales pitches.
I have been burned by vendors who overpromised. I hate:
- Generic flattery ("Congrats on your growth!")
- Fake personalization ("I noticed you...")
- Vague promises ("Companies like yours see 20-30% improvement")
- Meeting requests with no value ("Quick call to discuss...")

My responsibilities: [From Phase 0]
My KPIs: [From Phase 0]
My pains: [From Phase 0]

I DELETE 97% of sales emails within 1 second. Subject line suspicious? Delete.
Of the 3% I open, I reply to MAYBE one per week.

I ONLY respond to emails that:
1. Mirror an EXACT situation I'm in RIGHT NOW (with verifiable specifics)
2. Contain data I DEFINITELY don't have and can verify myself
3. Offer a non-obvious insight that changes how I think about a problem
4. Provide COMPLETE value in the email (no meeting required)
5. Make me say 'Holy shit, how did they know that?'

If my reaction is 'maybe useful' or 'interesting' or 'pretty good' - that's a NO.
The bar is: 'I need to act on this immediately' or DELETE."
```

**Step 2: Score on 7 Criteria (1-10 each)**

1. **Situation Recognition:** Does this mirror MY exact situation with verifiable details?
2. **Data Credibility:** Can I trust and verify this data?
3. **Insight Value:** Is this non-obvious? Do I genuinely not know this?
4. **Actionability:** Is there a clear, specific action I can take?
5. **Recipient Effort:** How easy is it to get value or respond?
6. **Impact & Urgency:** Does this affect my money/metrics? Why now?
7. **Emotional Resonance:** What's my gut reaction? Does this trigger action?

**Step 3: Calculate Average Score**

Average = (S1 + S2 + S3 + S4 + S5 + S6 + S7) ÷ 7

**Step 4: Apply THREE MANDATORY LITMUS TESTS**

After scoring, apply these 3 litmus tests. **FAIL ANY = AUTO-DESTROY regardless of score.**

**Litmus Test 1: "So What?" Test**
- Question: Does this tell them something NEW they can ACT on?
- If no specific action + no change → ❌ FAIL

**Litmus Test 2: "Wikipedia" Test**
- Question: Could they find this on Wikipedia/Google in 30 seconds?
- If easily discoverable → ❌ FAIL

**Litmus Test 3: "Competitor" Test**
- Question: Could ANY competitor send this EXACT message?
- If no differentiation → ❌ FAIL

**Step 5: Apply Gold Standard Threshold**

- **8.0-10.0 AND all 3 litmus tests pass:** ✅ GOLD STANDARD - Advance to Phase 4
- **7.0-7.9 (MAYBE ZONE):** ⚠️ MANDATORY REVISION (see below)
- **<7.0 OR any litmus test fails:** ❌ DESTROY immediately

**Step 5: Document Evaluation**

```markdown
## Evaluation: PVP #1

**Message Evaluated:**
[Full message]

**Persona Role-Play:**
"I am [Job Title]... [adoption statement]"

**Scoring:**
- Situation Recognition: [X]/10 - [why?]
- Data Credibility: [X]/10 - [why?]
- Insight Value: [X]/10 - [why?]
- Actionability: [X]/10 - [why?]
- Recipient Effort: [X]/10 - [why?]
- Impact & Urgency: [X]/10 - [why?]
- Emotional Resonance: [X]/10 - [why?]

**Average: [X.X]/10**

**Verdict:** ✅ GOLD STANDARD / ⚠️ REVISE / ❌ DESTROY

**Buyer Perspective Rationale:**
[2-3 sentences as the buyer explaining why I would/wouldn't reply]

[If score 7.0-7.9:]
**Revision Recommendations:**
- [Specific fix 1]
- [Specific fix 2]
```

### MANDATORY Revision Cycle (For 7.0-7.9 MAYBE ZONE)

**CRITICAL:** Scores 7.0-7.9 are NOT acceptable as-is. "Pretty good" = NOT good enough.

For concepts scoring 7.0-7.9:
1. Identify specific weaknesses (which criteria scored lowest?)
2. Identify which litmus test(s) nearly failed
3. Generate ONE revised version addressing weaknesses
4. Re-evaluate using FULL rubric + ALL 3 litmus tests
5. **After revision verdict:**
   - Score ≥8.0 AND all litmus tests pass → ✅ Advance to Phase 4
   - Score <8.0 OR any litmus test fails → ❌ DESTROY

**NO SECOND REVISION** - If it can't hit 8.0 in one attempt, the concept is fundamentally flawed. DESTROY and move on.

### Phase 3 Output

```markdown
# Phase 3 Complete: Buyer Evaluation

## Evaluation Results

**Total PVPs Evaluated:** 12

**Gold Standard (≥8.0):** 7 PVPs
**Strong PQS (7.0-7.9):** 3 PVPs
**Destroyed (<7.0):** 2 PVPs

## Gold Standard PVPs (≥8.0)

[List 7 PVPs with scores and evaluation rationales]

## Proceeding to Phase 4: Final Selection & Feasibility
```

---

## PHASE 4: Selection & Feasibility Validation

**Objective:** Select top 5 Gold Standard PVPs and validate data feasibility

### Load Feasibility Framework

Read: `.claude/skills/blueprint-validator/prompts/data-feasibility-framework.md`

### Step 1: Rank Gold Standard PVPs

Sort all PVPs scoring ≥8.0 by average score (highest first)

### Step 2: Validate Data Feasibility (Top 7-8)

For each of the top-scoring PVPs, assess feasibility:

**Data Accessibility:** Can we GET the data?
- HIGH: Public API, free or <$200/month
- MEDIUM: Scraping required, $200-1000/month
- LOW: Manual only, >$1000/month

**Processing Complexity:** Can we PROCESS at scale?
- SIMPLE: Direct API query
- MODERATE: Multiple calls + joining
- COMPLEX: ML/NLP required

**Update Frequency:** Is data FRESH enough?
- EXCELLENT: Real-time or daily
- GOOD: Weekly or monthly
- POOR: Annual or sporadic

**Coverage:** Does data EXIST for target?
- COMPLETE: 80%+ market coverage
- PARTIAL: 40-80% coverage
- SPARSE: <40% coverage

**Overall Feasibility:**
- **HIGH:** All dimensions good, ready to deploy
- **MEDIUM:** Mixed, worth investment
- **LOW:** Not viable, too difficult

### Step 3: Select Final 5

Decision matrix:
- **Priority 1:** Highest-scoring (≥8.5) + HIGH feasibility
- **Priority 2:** High-scoring (8.0-8.4) + HIGH feasibility
- **Priority 3:** Exceptional score (≥9.0) + MEDIUM feasibility

**Minimum Quality Gate:**
- All 5 must score ≥8.0
- At least 3 must have HIGH feasibility
- If can't find 5 meeting criteria: Return best available (2-4) with honest assessment

### Step 4: Document Implementation Path

For each final 5 PVPs:

```markdown
## Final PVP #1: [Title]

**Buyer Evaluation Score:** [X.X]/10

**Target Persona:** [Job Title]

**Core Insight:** [Synthesis]

**Data Requirements:**
- Primary: [Source name] - API: [Yes/No], Cost: [$X], Fields: [List]
- Secondary: [Source name] - Method: [Scraping/API], Cost: [$Y]
- Internal (if applicable): [Data type] - Readiness: [NOW / 6M / 12M]

**Overall Feasibility:** HIGH / MEDIUM / LOW

**DRAFT MESSAGE:**
> Subject: [Subject]
>
> [Para 1: Data hook]
>
> [Para 2: Value]
>
> [Para 3: CTA]

**Buyer Evaluation Summary:**
[Key strengths from evaluation - why this scored 8.0+]

**Implementation Playbook:**
- Data access: [How to get data]
- Processing: [Steps required]
- Estimated setup time: [Hours/days]
- Monthly cost: [$X]
- Scalability: [Prospects/day capacity]

**Label:** [PUBLIC ONLY / INTERNAL DATA - Ready NOW / INTERNAL + PUBLIC HYBRID]

[Repeat for all 5 final PVPs]
```

### Phase 4 Output

```markdown
# Phase 4 Complete: Final Selection

## Top 5 Gold Standard PVPs Selected

[All 5 PVPs with complete documentation]

## Summary Statistics

**Total Insights Generated:** 12
**Total Messages Drafted:** 12
**Gold Standard PVPs (≥8.0):** 7
**Final Selection:** 5

**Feasibility Breakdown:**
- HIGH feasibility: 4 PVPs
- MEDIUM feasibility: 1 PVP
- LOW feasibility: 0 PVPs (excluded)

**Data Type Breakdown:**
- Public data only: 3 PVPs
- Internal + Public hybrid: 2 PVPs
- Internal data (sender at scale): 0 PVPs

## Readiness Assessment

**Ready to Deploy Immediately:** 4 PVPs (HIGH feasibility)
**Requires Investment:** 1 PVP (MEDIUM feasibility - [$X] cost)

**Estimated Total Implementation:**
- Development time: [Hours/days]
- Monthly operational cost: [$X]
- Maintenance: [Low/Medium/High]

## Process Complete ✅

Blueprint PVP Deep Generation successfully completed.
Delivered 5 Gold Standard PVPs (8.0+) with validated data feasibility.
```

---

## Error Handling & Edge Cases

### Insufficient Context (Phase 0)

**Symptom:** <3 categories pass validation

**Action:**
1. List specific gaps
2. Invoke necessary modules (Wave 1, Wave 2, Synthesis)
3. Restart Phase 1 with complete context
4. DO NOT proceed without sufficient context

### No Gold Standard PVPs Found (Phase 3)

**Symptom:** 0 PVPs score ≥8.0 after evaluation

**Action:**
1. Document why PVPs failed (common weaknesses)
2. Return 2-3 best attempts (highest scores) with honest assessment
3. Provide recommendations:
   - Need different data sources?
   - ICP/persona mismatch with available data?
   - This vertical may not be suitable for data-driven PVPs
4. Suggest fallback: Strong PQS messages (7.0-7.9) if available

### Fewer Than 5 Gold Standard PVPs

**Symptom:** Only 2-4 PVPs score ≥8.0

**Action:**
1. Return best available (2-4 PVPs)
2. Be honest: "Generated [N] Gold Standard PVPs (not 5)"
3. Explain why: Data limitations / persona-data mismatch
4. Provide improvement recommendations

### Data Feasibility Blocks Final Selection

**Symptom:** Top-scoring PVPs have LOW feasibility

**Action:**
1. Move to next-highest scoring with better feasibility
2. Document trade-off: "PVP #3 (score 8.2, HIGH feasibility) selected over PVP #1 (score 8.7, LOW feasibility)"
3. Mark LOW feasibility PVPs as "Aspirational - Requires Data Infrastructure"

---

## Success Criteria

Blueprint PVP Deep Generation succeeds when:

- [ ] Phase 0: Context validated (4/5+ categories PASS)
- [ ] Phase 1: 8-12 non-obvious synthesis insights generated
- [ ] Phase 2: 8-12 complete PVP concept + message pairs drafted
- [ ] Phase 3: All PVPs evaluated from buyer perspective
- [ ] Phase 4: 5 PVPs selected, all scoring ≥8.0
- [ ] Phase 4: At least 3/5 have HIGH data feasibility
- [ ] Phase 4: Implementation playbook documented for each
- [ ] Process completes in 10-17 minutes
- [ ] No "impossible PVPs" (all have viable implementation path)

---

## Key Differentiators from Turbo

1. **Context Autonomy:** PVP agent validates and gathers own context (Turbo provides passively)
2. **Deep Synthesis:** More time on Sequential Thinking, weirder combinations (Turbo: faster synthesis)
3. **Internal Data:** Infers and includes internal data opportunities (Turbo: public only)
4. **Rigorous Evaluation:** Per-concept buyer role-play (Turbo: batch evaluation)
5. **Higher Bar:** 8.0+ threshold (Turbo: 7.0+ for PQS, 8.5+ for PVP)
6. **Feasibility Validation:** Validates implementation path (Turbo: assumes feasibility)
7. **Fewer, Better:** 5 Gold Standard PVPs (Turbo: 2 PVPs + 2 PQS)

---

## Usage

### Standalone Mode

```
Run: Skill(skill: "blueprint-pvp-deep")

User provides: Company URL (if no context available)

Agent autonomously:
1. Gathers context (invokes Wave 1, 2, Synthesis if needed)
2. Generates synthesis
3. Drafts PVPs
4. Evaluates rigorously
5. Selects top 5 with feasibility validation
6. Returns complete analysis
```

### Integrated Mode (Called by Turbo)

```
Turbo runs Waves 1-2 and Synthesis, then:

Turbo: Skill(skill: "blueprint-pvp-deep")

Agent receives:
- Company context (from Wave 1)
- ICP/persona (from Wave 1)
- Data landscape (from Wave 2)
- Pain segments (from Synthesis)

Agent skips Phase 0 context gathering (validates only), then:
- Proceeds to Phase 1 (synthesis)
- Completes Phases 2-4
- Returns 5 Gold Standard PVPs to Turbo
```

---

## Final Output Format

Return results in this format:

```markdown
# Blueprint PVP Deep Generation Results

**Company:** [Name]
**Execution Time:** [X minutes]
**Context Quality:** [EXCELLENT / GOOD / MARGINAL]

---

## Top 5 Gold Standard PVPs

### PVP #1: [Title] (Score: [X.X]/10)

[Complete PVP documentation as specified in Phase 4]

### PVP #2: [Title] (Score: [X.X]/10)

[Complete PVP documentation]

### PVP #3: [Title] (Score: [X.X]/10)

[Complete PVP documentation]

### PVP #4: [Title] (Score: [X.X]/10)

[Complete PVP documentation]

### PVP #5: [Title] (Score: [X.X]/10)

[Complete PVP documentation]

---

## Process Summary

**Phase 0 - Context Validation:** ✅ [EXCELLENT / GOOD / MARGINAL]
**Phase 1 - Deep Synthesis:** Generated [N] insights using Sequential Thinking
**Phase 2 - Drafting:** Drafted [N] PVP concepts + messages
**Phase 3 - Buyer Evaluation:** [N] Gold Standard (≥8.0), [N] Strong PQS (7.0-7.9)
**Phase 4 - Selection:** Selected top 5, validated feasibility

**Readiness:**
- Immediately deployable: [N] PVPs (HIGH feasibility)
- Requires investment: [N] PVPs (MEDIUM feasibility)
- Total estimated cost: [$X/month]

---

## Recommendations

[Any recommendations for improving PVP generation in future runs, data gaps identified, or strategic insights about this ICP/vertical]
```

---

**Blueprint PVP Deep Generation - Autonomous Agent for Gold Standard PVPs**

*Context-aware. Data-driven. Buyer-validated. Feasibility-guaranteed.*
