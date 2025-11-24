# Hard Gate Validator

**Purpose:** Four mandatory gates that AUTO-REJECT invalid patterns. Apply to every segment and PVP before proceeding.

**Rule:** Fail ANY gate = AUTO-DESTROY. No exceptions. No "but in this case..." rationalizations.

---

## The Four Hard Gates

```
INPUT: Segment concept OR PVP message

→ GATE 1: Horizontal Disqualification
   "Is the ICP operationally specific?"
   FAIL → AUTO-DESTROY

→ GATE 2: Causal Link Constraint
   "Does the signal PROVE the pain?"
   FAIL → AUTO-DESTROY

→ GATE 3: No Aggregates Ban
   "Are statistics company-specific?"
   FAIL → AUTO-DESTROY

→ GATE 4: Technical Feasibility Audit
   "Can we actually detect this data?"
   FAIL → AUTO-DESTROY

→ ALL PASS → VALIDATED ✓ (proceed to next phase)
```

---

## Gate 1: Horizontal Disqualification

**Question:** Is the ICP operationally specific, or could it be "any B2B company"?

### FAIL Conditions (Auto-Reject if ANY are true)

The segment/message FAILS if the ICP can be described as:
- "Any B2B company"
- "SMB" or "Enterprise" (without operational specificity)
- "Growing companies"
- "Funded companies"
- "Tech companies" (generic)
- "SaaS companies" (generic)
- "Sales teams" (without licensing/regulatory context)
- "Companies with [department]" (e.g., "companies with HR teams")

### PASS Conditions

The segment/message PASSES if ICP includes:
- Specific industry with regulatory oversight
- Operational context (processes, workflows, compliance requirements)
- Specific pain tied to observable data

### Examples

| ICP Description | Gate 1 Result | Rationale |
|-----------------|---------------|-----------|
| "B2B SaaS companies growing fast" | ❌ FAIL | No operational specificity |
| "Companies that raised Series B" | ❌ FAIL | Funding ≠ operational specificity |
| "Sales teams using CRM" | ❌ FAIL | Could be any company |
| "Multi-state insurance agencies" | ✅ PASS | Regulated, specific compliance context |
| "Restaurants with >100 Google reviews/month in NYC" | ✅ PASS | Operational + geographic specificity |
| "Nursing homes with <3 CMS stars" | ✅ PASS | Regulatory + specific threshold |

### Gate 1 Validation Format

```markdown
**Gate 1: Horizontal Disqualification**

ICP Description: [From segment/message]

Check:
- [ ] NOT "any B2B company"
- [ ] NOT generic funding/growth descriptor
- [ ] HAS operational/regulatory specificity
- [ ] HAS observable pain indicator

**Result:** ✅ PASS / ❌ FAIL
**Rationale:** [Why it passes or fails]
```

---

## Gate 2: Causal Link Constraint

**Question:** Does the signal DIRECTLY PROVE the specific pain, or is it just a proxy for growth/activity?

### The Causal Link Test

Ask: "Could a company have this signal but NOT have the pain?"

- If YES → Weak causal link → ❌ FAIL
- If NO → Strong causal link → ✅ PASS

### Banned Signals (Always FAIL Gate 2)

These signals NEVER prove specific pain:

| Banned Signal | Why It Fails |
|---------------|--------------|
| Recently raised funding | Thousands of companies raise, no specific pain implied |
| Hiring for [role type] | All scaling companies hire |
| Growing headcount | Growth activity, not pain |
| Expanding to new markets | Strategic move, not operational pain |
| M&A activity | Business development, not pain |
| Job postings | Normal business operation |
| Tech stack includes [tool] | Using tool ≠ having problem with it |
| Company is [size] | Size alone doesn't prove pain |
| Industry is [sector] | Being in sector ≠ experiencing pain |

### Strong Signals (Can PASS Gate 2)

| Strong Signal | Why It Works |
|---------------|--------------|
| Open EPA violation | Violation IS the compliance pressure |
| CMS <3 star rating | Rating IS the quality mandate |
| FMCSA Conditional rating | Rating IS the safety requirement |
| Health dept grade drop | Grade IS the operational failure |
| License expiration in 30 days | Deadline IS the compliance pain |
| Permit filed requiring specific equipment | Filing IS the need signal |
| Menu price 28% higher on DoorDash | Price difference IS the commission exposure |

### Gate 2 Validation Format

```markdown
**Gate 2: Causal Link Constraint**

Signal Used: [From segment/message]
Claimed Pain: [What pain is this supposed to indicate?]

Causal Test: "Could they have this signal but NOT have the pain?"
- Answer: YES / NO

Check:
- [ ] Signal is NOT on banned list
- [ ] Signal DIRECTLY proves pain (not just activity)
- [ ] Pain connection is necessary, not coincidental

**Result:** ✅ PASS / ❌ FAIL
**Rationale:** [Why the causal link is strong or weak]
```

---

## Gate 3: No Aggregates Ban

**Question:** Are statistics company-specific, or are they industry-wide aggregates presented as insights?

### FAIL Conditions

The segment/message FAILS if it contains:
- Industry averages without their specific data
- Statistics that apply to thousands of companies
- Research findings presented as if about them specifically
- Benchmarks without their data point for comparison

### Banned Patterns

| Pattern | Example | Why It Fails |
|---------|---------|--------------|
| "Industry average is X%" | "The average restaurant pays 28% in fees" | Applies to ALL restaurants |
| "Companies like yours typically..." | "Companies like yours see 20-30% inefficiency" | Not about THEM |
| "Research shows..." | "Research shows 73% of sales teams..." | Generic stat |
| "[N]% of [industry]..." | "63% of manufacturers face..." | Could be them or anyone |
| "The typical [role]..." | "The typical ops manager spends 10 hours..." | Generic persona |

### PASS Conditions

Aggregates are ALLOWED only when:
1. Their SPECIFIC data point is provided
2. Aggregate is used for COMPARISON, not as the insight
3. Format: "Your [specific metric] vs [aggregate benchmark]"

### Examples

| Statement | Gate 3 Result | Rationale |
|-----------|---------------|-----------|
| "23% capture rate is the industry norm" | ❌ FAIL | Industry stat, not their data |
| "Companies in your space face compliance challenges" | ❌ FAIL | Generic, applies to thousands |
| "Your 18.4 visits per 1000 residents vs state avg of 28.1" | ✅ PASS | Their specific data + comparison |
| "Your facility's 14 violations vs county median of 8" | ✅ PASS | Their data + benchmark |
| "Top 10% use 2.3 lbs chlorine vs your 3.8 lbs" | ✅ PASS | Their data + benchmark |

### Gate 3 Validation Format

```markdown
**Gate 3: No Aggregates Ban**

Statistics Used: [List any statistics/numbers in segment/message]

Check for each statistic:
- [ ] Is this THEIR specific data point?
- [ ] If aggregate, is it comparison (not insight)?
- [ ] Format: "Your [X] vs [benchmark]"?

**Result:** ✅ PASS / ❌ FAIL
**Rationale:** [Which stats pass/fail and why]
```

---

## Gate 4: Technical Feasibility Audit

**Question:** Can we actually detect/obtain this data? What is the MECHANICAL detection method?

### The Mechanical Test

For EVERY data claim, you MUST be able to answer:

1. **What is the data source?** (Name of API, database, or scraping target)
2. **What is the specific field/attribute?** (Field name, CSS selector, API response key)
3. **How do we access it?** (API call, web scrape, manual lookup)
4. **What's the detection footprint?** (What exactly makes this detectable?)

If you cannot answer ALL FOUR → ❌ FAIL

### Undetectable Data Claims (Always FAIL)

| Claimed Data | Why Undetectable |
|--------------|------------------|
| Digital business card usage | Apps live on phones, not corporate websites |
| CRM data quality | Internal system, not externally visible |
| Sales cycle length | Internal metric |
| Employee satisfaction | Glassdoor is anecdotal, not systematic |
| Internal process efficiency | Operational, requires inside access |
| Tool adoption rates | Can't see login/usage data |
| Budget constraints | Not publicly visible |
| "BuiltWith for [non-web technology]" | Only detects web-facing tech |

### Detectable Data Claims (Can PASS)

| Data Claim | Detection Mechanism |
|------------|---------------------|
| EPA violation | EPA ECHO API → `violation_id`, `penalty_amount` |
| CMS star rating | CMS Care Compare API → `overall_rating` field |
| Restaurant health grade | Local health dept API → `inspection_score` |
| FMCSA safety rating | FMCSA SAFER API → `safety_rating` field |
| Google review velocity | Google Maps API → `reviews[].time` timestamps |
| Menu price arbitrage | Web scrape: Restaurant site vs DoorDash/UberEats |
| Tech stack (web-facing) | BuiltWith API → specific technology categories |

### Gate 4 Validation Format

```markdown
**Gate 4: Technical Feasibility Audit**

Data Claims in Segment/Message:
1. [Data claim 1]
2. [Data claim 2]

For EACH claim:

**Claim 1: [Data claim]**
- Data Source: [API/database name]
- Specific Field: [field name or selector]
- Access Method: [API call / scrape / manual]
- Detection Footprint: [What makes this visible externally?]
- Feasibility: ✅ Detectable / ❌ Not detectable

[Repeat for each claim]

**Result:** ✅ PASS (all claims detectable) / ❌ FAIL (any claim undetectable)
**Rationale:** [Which claims pass/fail]
```

---

## Complete Validation Process

### For Segments (Synthesis Phase)

```markdown
## Hard Gate Validation: [Segment Name]

### Gate 1: Horizontal Disqualification
[Validation format from above]

### Gate 2: Causal Link Constraint
[Validation format from above]

### Gate 3: No Aggregates Ban
[Validation format from above]

### Gate 4: Technical Feasibility Audit
[Validation format from above]

---

## FINAL VERDICT

| Gate | Result |
|------|--------|
| Gate 1: Horizontal | ✅/❌ |
| Gate 2: Causal Link | ✅/❌ |
| Gate 3: Aggregates | ✅/❌ |
| Gate 4: Feasibility | ✅/❌ |

**VERDICT:** ✅ VALIDATED - Proceed / ❌ AUTO-DESTROY

[If any gate failed:]
**Failed Gate(s):** [List]
**Failure Reason:** [Specific issue]
**Revision Possible?** YES (one attempt) / NO (fundamental flaw)
```

### For PVP Messages (Evaluation Phase)

Apply same format, but check the actual MESSAGE text against all four gates.

---

## Revision Protocol

### When Revision IS Possible

If segment/message fails due to:
- Gate 3 (aggregate used incorrectly) → Can add their specific data
- Gate 4 (one data source undetectable) → Can substitute different source

**Revision Steps:**
1. Identify specific failure point
2. Propose one fix
3. Re-validate through all 4 gates
4. If still fails → DESTROY (no second revision)

### When Revision is NOT Possible

If segment/message fails due to:
- Gate 1 (fundamental ICP issue) → Need different vertical
- Gate 2 (no strong signal exists) → Concept is invalid
- Gate 4 (core premise is undetectable) → Concept impossible

**Action:** DESTROY immediately, don't attempt revision

---

## Quick Reference Card

**Gate 1 Quick Check:**
> "Could this ICP description apply to 10,000+ companies?" If YES → FAIL

**Gate 2 Quick Check:**
> "Could they have this signal but NOT have the pain?" If YES → FAIL

**Gate 3 Quick Check:**
> "Is there a specific number that is THEIR data (not industry)?" If NO → FAIL

**Gate 4 Quick Check:**
> "Can I name the API field or scraping selector for this data?" If NO → FAIL

---

## Integration Points

### Use During Synthesis
- After generating segment concept, before proceeding
- Reject segments that fail any gate
- One revision attempt allowed

### Use During Drafting
- After drafting message, before evaluation
- Catch issues before wasting evaluation time
- No revision at this stage (draft differently)

### Use During Evaluation
- First step before scoring
- Fail any gate → AUTO-DESTROY (don't score)
- Hard gates come BEFORE soft evaluation

---

**Version:** 1.0.0 (November 2025)

**Principle:** These gates are non-negotiable. If a message is good enough to pass, it passes. If not, destroy it. There is no "almost passes" or "close enough."
