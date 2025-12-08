---
name: blueprint-validator
description: Quality enforcement skill that validates segments and PVPs against 5 hard gates, banned patterns, and data feasibility. Invoked by blueprint-turbo and blueprint-pvp-deep to ensure all outputs meet Blueprint GTM quality standards.
---

# Blueprint Validator

Quality enforcement for Blueprint GTM. Validates segments and PVPs against mandatory quality standards.

---

## When to Invoke This Skill

Use `Skill(skill: "blueprint-validator")` when:
- Blueprint-turbo reaches Hard Gate Checkpoint (after Synthesis)
- Blueprint-pvp-deep needs to validate PVP concepts
- Any skill needs to validate segment quality before proceeding

---

## Input Contract

The invoking skill passes context in this format:

```markdown
## Validation Request

**Mode:** SEGMENT_VALIDATION | PVP_VALIDATION | FULL_VALIDATION

**Product Context:**
- Core Problem: [From Wave 0.5]
- Valid Pain Domains: [List]
- Invalid Pain Domains: [List]

**Segments to Validate:**
1. Name: [Segment name]
   Description: [What pain, what ICP]
   Data Sources: [List of sources]
   Fields: [Specific field names]

2. [Additional segments...]

**PVPs to Validate (if PVP mode):**
1. Title: [PVP title]
   Message: [Full message text]
   Data Claims: [What data is used]
```

---

## Output Contract

Validator returns structured results:

```markdown
## Validation Results

### Summary
- Total Validated: X
- Passed: Y
- Failed: Z
- Revision Candidates: W

### Validated Segments (Passed All 5 Gates)

**1. [Segment Name]** - VALIDATED
- Gate 1: PASS - [rationale]
- Gate 2: PASS - [rationale]
- Gate 3: PASS - [rationale]
- Gate 4: PASS - [rationale]
- Gate 5: PASS - [rationale]
- Feasibility: HIGH

### Rejected Segments

**1. [Segment Name]** - REJECTED
- Failed Gate: [Which gate]
- Failure Reason: [Specific issue]
- Revision Possible: YES/NO
- If YES: [What to fix]

### Revision Candidates (Failed Gate 3 or 4 Only)

**1. [Segment Name]** - NEEDS REVISION
- Failed Gate: 3 or 4
- Issue: [What failed]
- Fix: [How to revise]
```

---

## Validation Process

### Phase 1: Load Validation Framework

```
Read: .claude/skills/blueprint-validator/prompts/hard-gate-validator.md
Read: .claude/skills/blueprint-validator/prompts/banned-patterns-registry.md
Read: .claude/skills/blueprint-validator/prompts/data-feasibility-framework.md
```

### Phase 2: Run 5-Gate Validation (Per Segment)

For EACH segment/PVP:

**Gate 1: Horizontal Disqualification**
- Question: "Is the ICP operationally specific?"
- FAIL if: Generic (any B2B company, SaaS companies, growing companies)
- PASS if: Industry + regulatory/operational context

**Gate 2: Causal Link Constraint**
- Question: "Does the signal PROVE the pain?"
- FAIL if: Growth signals (funding, hiring, expansion)
- PASS if: Regulatory/operational signal directly proves pain

**Gate 3: No Aggregates Ban**
- Question: "Are statistics company-specific?"
- FAIL if: Industry averages without their data
- PASS if: "Your [X] vs benchmark [Y]" format
- REVISION ALLOWED if failed

**Gate 4: Technical Feasibility Audit**
- Question: "Can we actually detect this data?"
- Must answer: Data source? Field name? Access method?
- FAIL if: Cannot name API/field/selector
- REVISION ALLOWED if failed

**Gate 5: Product Connection**
- Question: "Does product solve this pain?"
- FAIL if: Pain in INVALID domain, product tangential
- PASS if: Pain in VALID domain, product is primary solution
- NO REVISION if failed (fundamental flaw)

### Phase 3: Check Banned Patterns

Scan each segment/PVP for:
- Generic growth signals (Category 1)
- Soft data sources as primary (Category 2)
- Industry-wide statistics (Category 3)
- Weak causal links (Category 4)
- Undetectable data claims (Category 5)
- Banned phrases (Category 6)

**If ANY banned pattern found → AUTO-DESTROY**

### Phase 4: Assess Data Feasibility

For validated segments, rate:
- Data Accessibility: HIGH / MEDIUM / LOW
- Processing Complexity: SIMPLE / MODERATE / COMPLEX
- Update Frequency: EXCELLENT / GOOD / POOR
- Coverage: COMPLETE / PARTIAL / SPARSE

**Overall Feasibility:**
- HIGH: Ship it (include in final output)
- MEDIUM: Worth investment (note limitations)
- LOW: Not viable (mark as aspirational)

### Phase 5: Compile Results

Sort segments into:
1. **VALIDATED** - Passed all 5 gates, HIGH/MEDIUM feasibility
2. **REJECTED** - Failed gates 1, 2, or 5 (fundamental flaws)
3. **REVISION_CANDIDATES** - Failed only gate 3 or 4 (can fix)

---

## Revision Protocol

When segment fails Gate 3 or Gate 4 ONLY:

1. Identify specific failure point
2. Suggest fix (add specific data / substitute source)
3. Invoking skill can revise and re-submit
4. ONE revision attempt allowed
5. If still fails after revision → DESTROY

**Revision NOT allowed for:**
- Gate 1 failures (ICP too generic)
- Gate 2 failures (no strong signal exists)
- Gate 5 failures (product doesn't solve pain)

---

## Example Invocation

### From Blueprint-Turbo (Hard Gate Checkpoint)

```markdown
→ Invoke: Skill(skill: "blueprint-validator")
→ Pass:
  - Mode: SEGMENT_VALIDATION
  - Product Context from Wave 0.5
  - Segments from Synthesis phase
→ Receive:
  - Validated segments for Wave 3
  - Rejected segments with reasons
  - Revision candidates with fix suggestions
```

### From Blueprint-PVP-Deep (Phase 3)

```markdown
→ Invoke: Skill(skill: "blueprint-validator")
→ Pass:
  - Mode: PVP_VALIDATION
  - Product Context
  - Draft PVP messages
→ Receive:
  - Validated PVPs for final selection
  - Rejected PVPs with gate failures
```

---

## Quick Reference

### 5 Gates Summary

| Gate | Question | Auto-Destroy? | Revision? |
|------|----------|---------------|-----------|
| 1: Horizontal | ICP specific? | YES | NO |
| 2: Causal Link | Signal proves pain? | YES | NO |
| 3: Aggregates | Stats company-specific? | YES | YES (once) |
| 4: Feasibility | Data detectable? | YES | YES (once) |
| 5: Product Fit | Product solves pain? | YES | NO |

### Banned Pattern Categories

1. Generic Growth Signals (funding, hiring, expansion)
2. Soft Data Sources (Crunchbase, Apollo, ZoomInfo)
3. Industry-Wide Statistics (without their data)
4. Weak Causal Links (signal doesn't prove pain)
5. Undetectable Data Claims (internal metrics)
6. Banned Phrases (template openers/closers)

---

## Version

**Version:** 1.0.0 (December 2025)

**Principle:** Quality enforcement is non-negotiable. If it passes, it passes. If it fails, it's destroyed. No "close enough."
