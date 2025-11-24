# Vertical Qualification Module

**Purpose:** Convert generic verticals to regulated niches with data moats BEFORE data discovery begins.

**When:** Execute immediately after Wave 1 industry identification, BEFORE Wave 2.

**Time:** 3-5 minutes

**Output:** 1-2 qualified niches with scores ≥25/40, ready for Wave 2 data discovery

---

## Why This Matters

**The Blinq Failure Pattern:**
1. Wave 1 identifies: "Sales teams, professional services"
2. Wave 2 searches generic data: Crunchbase, Apollo, job postings
3. Synthesis generates: "Companies raising Series B and hiring sales"
4. Result: Generic messages that could be sent by any competitor

**The Correct Pattern:**
1. Wave 1 identifies: "Sales teams, professional services"
2. **NICHE CONVERSION:** "Sales teams" → "Multi-state insurance agents" (NIPR)
3. Wave 2 searches: NIPR, state licensing boards, CE databases
4. Synthesis generates: "Agencies with 14 new licenses in 45 days = compliance gap"
5. Result: Specific messages only we can send

---

## Process

### Step 1: List All Verticals from Wave 1

Extract every industry/vertical mentioned:
- Primary verticals (explicitly stated on website)
- Secondary verticals (mentioned in case studies, use cases)
- Adjacent verticals (logically related)

### Step 2: Check Auto-Reject List

Reference: `.claude/skills/blueprint-turbo/references/data-moat-verticals.md`

For EACH vertical, check if it's on the Auto-Reject list:

| Vertical | Auto-Reject? | Action |
|----------|--------------|--------|
| SaaS companies | YES | MUST convert to niche |
| Tech startups | YES | MUST convert to niche |
| B2B companies | YES | MUST convert to niche |
| Sales teams (generic) | YES | MUST convert to niche |
| Growing companies | YES | MUST convert to niche |
| Professional services | YES | MUST convert to niche |
| Marketing teams | YES | NO good niche exists |
| HR departments | YES | NO good niche exists |

**If vertical is NOT on Auto-Reject list:** Proceed to Step 3 scoring
**If vertical IS on Auto-Reject list:** Proceed to Step 4 niche conversion

### Step 3: Score Non-Rejected Verticals

For verticals NOT on auto-reject list, score using the rubric:

**Criterion 1: Regulatory Footprint (0-10)**
- 10: Heavy federal regulation (EPA, OSHA, CMS, FDA, FMCSA)
- 7-9: State-level licensing with public portals
- 4-6: Industry self-regulation
- 0-3: No regulatory oversight

**Criterion 2: Compliance-Driven Pain (0-10)**
- 10: Violations directly create solution-relevant pain
- 7-9: Regulations force behaviors creating pain
- 4-6: Indirect connection
- 0-3: No compliance-driven pain

**Criterion 3: Data Accessibility (0-10)**
- 10: Free public API, daily updates
- 7-9: Free portal, weekly updates
- 4-6: Paid API or manual access
- 0-3: No accessible data

**Criterion 4: Specificity Potential (0-10)**
- 10: Record numbers, dates, addresses all available
- 7-9: Multiple identifiers available
- 4-6: Basic entity data
- 0-3: Aggregate data only

**Total Score = Sum of 4 criteria (max 40)**

### Step 4: Convert Auto-Reject Verticals to Niches

For each auto-rejected vertical, find regulated niches:

```
CONVERSION SEARCH PATTERN:

1. WebSearch: "[vertical] licensing board database"
2. WebSearch: "[vertical] government records public"
3. WebSearch: "[vertical] compliance violations database"
4. WebSearch: "[vertical] state regulation lookup"

Reference: data-moat-verticals.md Niche Conversion Table
```

**Example Conversions:**

| Generic | Search | Regulated Niche Found | Data Source |
|---------|--------|----------------------|-------------|
| "Sales teams" | "sales licensing board" | Insurance agents | NIPR |
| "Sales teams" | "sales license lookup" | Real estate agents | State RE boards |
| "Professional services" | "professional license database" | Contractors | State licensing |
| "Healthcare" | "healthcare facility ratings" | Nursing homes | CMS Care Compare |

### Step 5: Score Converted Niches

Apply same 4-criterion rubric to each converted niche.

### Step 6: Select Best Niche(s)

**Decision Matrix:**

| Score | Decision |
|-------|----------|
| ≥30 | **PROCEED** - Tier 1 vertical, excellent data moat |
| 25-29 | **PROCEED** - Tier 2 vertical, good data moat |
| 20-24 | **CONDITIONAL** - Try internal data combinations first |
| <20 | **REJECT** - Find different niche |

**Selection Rules:**
1. Select highest-scoring niche (≥25/40)
2. If multiple niches qualify, select top 2 max
3. If NO niche scores ≥25: Try internal data hybrid approach
4. If still nothing: Warn user, this may not be Blueprint-compatible

---

## Output Format

```markdown
# Vertical Qualification Results

## Input Verticals from Wave 1
1. [Vertical 1]
2. [Vertical 2]
3. [Vertical 3]

## Auto-Reject Check

| Vertical | Auto-Reject? | Action |
|----------|--------------|--------|
| [Vertical 1] | YES/NO | Convert/Score |
| [Vertical 2] | YES/NO | Convert/Score |

## Niche Conversions Attempted

### [Generic Vertical] → Niche Conversion

**Search Queries Executed:**
- "[vertical] licensing board database" → Found: [result]
- "[vertical] government records" → Found: [result]

**Niches Identified:**
1. [Niche 1] - Data Source: [source]
2. [Niche 2] - Data Source: [source]

## Scoring Results

### [Niche/Vertical Name]

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Regulatory Footprint | X/10 | [Why] |
| Compliance-Driven Pain | X/10 | [Why] |
| Data Accessibility | X/10 | [Why] |
| Specificity Potential | X/10 | [Why] |
| **TOTAL** | **XX/40** | |

**Verdict:** PROCEED / CONDITIONAL / REJECT

[Repeat for each niche/vertical]

## Final Selection

**Selected Niche(s) for Wave 2:**
1. [Niche] - Score: XX/40 - Data Source: [source]
2. [Niche] - Score: XX/40 - Data Source: [source] (if applicable)

**Rejected:**
- [Vertical/Niche] - Score: XX/40 - Reason: [why]

## Proceeding to Wave 2 with: [Selected Niche(s)]
```

---

## Edge Cases

### No Niche Scores ≥25

**Try Internal Data Hybrid:**
1. What data does the SENDER company have? (from internal data inference)
2. Can sender's aggregated data + public data create PVPs?
3. If yes: Proceed with hybrid approach, score as 20-24 (conditional)
4. If no: Warn user

**Warning Output:**
```markdown
⚠️ VERTICAL QUALIFICATION WARNING

No regulated niche found with score ≥25/40.

**Attempted Niches:**
- [Niche 1]: Score XX/40 - [weakness]
- [Niche 2]: Score XX/40 - [weakness]

**Internal Data Hybrid Attempted:** [Yes/No]
- Sender internal data: [what they might have]
- Potential combination: [if any]

**Recommendation:**
1. This ICP may not be suitable for data-driven Blueprint GTM
2. Consider: [alternative approach or vertical]
3. Proceed with PQS-only approach (lower confidence)

**User Decision Required:** Proceed with limited data / Abort / Try different vertical
```

### Company Only Serves B2B SaaS

If target company's ONLY customers are B2B SaaS (no regulated verticals):

1. Check if they have internal data that could be aggregated
2. If sender has 100+ customers → internal benchmarking possible
3. If no regulated niche AND no internal data → Blueprint may not be suitable

**Output:**
```markdown
⚠️ BLUEPRINT COMPATIBILITY WARNING

This company serves horizontally (B2B SaaS to B2B SaaS).
No regulated vertical found in their customer base.

**Options:**
1. Internal Data Only: If sender has 100+ customers, can create benchmark PVPs
2. PQS-Only Approach: Use competitive intelligence for pain identification
3. Abort: This use case may not be Blueprint-compatible

**Recommendation:** [Based on analysis]
```

### Multiple High-Scoring Niches

If 3+ niches score ≥25:

1. Select top 2 by score
2. Prioritize diversity (different data sources)
3. Document why others were deprioritized

---

## Integration with Wave 2

**Wave 2 Input Changes:**

Instead of searching for generic industry data, Wave 2 receives:

```markdown
## Wave 2 Input: Qualified Niches

**Primary Niche:** [Niche name]
- Score: XX/40
- Data Source(s): [Specific sources to search]
- Pain Signal(s): [What to look for]

**Secondary Niche (if applicable):** [Niche name]
- Score: XX/40
- Data Source(s): [Specific sources]
- Pain Signal(s): [What to look for]

**Search Priority:**
1. [Primary niche data source] - MUST find
2. [Secondary niche data source] - Should find
3. [Supporting sources] - Nice to have
```

---

## Success Criteria

Vertical qualification succeeds when:

- [ ] All Wave 1 verticals checked against auto-reject list
- [ ] Auto-rejected verticals converted to niches
- [ ] All niches scored using 4-criterion rubric
- [ ] At least 1 niche scores ≥25/40
- [ ] Selected niche has identifiable data source
- [ ] Wave 2 receives specific niche (not generic vertical)

---

## Quick Reference: Scoring Shortcuts

**Instant 30+ (Tier 1):**
- CMS databases (Care Compare, Nursing Home Compare)
- EPA ECHO
- FMCSA SAFER
- FDA Warning Letters
- Major city health departments (NYC, LA, Chicago, SF)

**Likely 25-29 (Tier 2):**
- State licensing boards (contractors, professionals)
- NIPR (insurance agents)
- State real estate boards
- FINRA BrokerCheck (manual only)

**Usually <20 (Reject):**
- Any "B2B SaaS" vertical
- Any "tech company" vertical
- Any industry without government oversight
