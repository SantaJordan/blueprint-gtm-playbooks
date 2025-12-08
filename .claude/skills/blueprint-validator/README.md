# Blueprint Validator

**Quality enforcement skill for Blueprint GTM. Validates segments and PVPs against 5 mandatory gates, banned patterns, and data feasibility.**

## Quick Start

This skill is invoked by other Blueprint skills - not called directly:

```markdown
# From blueprint-turbo (Hard Gate Checkpoint):
Skill(skill: "blueprint-validator")
Pass: Mode=SEGMENT_VALIDATION, segments, product_fit

# From blueprint-pvp-deep (Phase 3):
Skill(skill: "blueprint-validator")
Pass: Mode=PVP_VALIDATION, pvp_messages, product_fit
```

## What This Skill Does

1. **5-Gate Validation** - Validates each segment against mandatory quality gates
2. **Banned Pattern Detection** - Auto-destroys segments with anti-patterns
3. **Data Feasibility Rating** - Assesses whether data is actually accessible
4. **Revision Management** - Allows one revision for Gate 3/4 failures only

## 5 Hard Gates

| Gate | Question | Auto-Destroy? | Revision? |
|------|----------|---------------|-----------|
| 1: Horizontal Disqualification | Is ICP operationally specific? | YES | NO |
| 2: Causal Link Constraint | Does signal PROVE the pain? | YES | NO |
| 3: No Aggregates Ban | Are stats company-specific? | YES | YES (once) |
| 4: Technical Feasibility | Can we detect this data? | YES | YES (once) |
| 5: Product Connection | Does product solve this pain? | YES | NO |

## Banned Pattern Categories

Segments are auto-destroyed if they contain:

1. **Generic Growth Signals** - funding, hiring, expansion, M&A
2. **Soft Data Sources** - Crunchbase, Apollo, ZoomInfo as primary
3. **Industry-Wide Statistics** - averages without their specific data
4. **Weak Causal Links** - signal doesn't prove pain
5. **Undetectable Data Claims** - internal metrics, private dashboards
6. **Banned Phrases** - template openers/closers ("I hope this finds you well")

## Input/Output Contract

### Input

```markdown
**Mode:** SEGMENT_VALIDATION | PVP_VALIDATION

**Product Context:**
- Core Problem: [From Wave 0.5]
- Valid Pain Domains: [List]
- Invalid Pain Domains: [List]

**Segments to Validate:**
1. Name, Description, Data Sources, Fields
```

### Output

```markdown
**Summary:** Total=X, Passed=Y, Failed=Z, Revision=W

**Validated Segments:** (passed all 5 gates)
**Rejected Segments:** (failed gates, with reasons)
**Revision Candidates:** (Gate 3/4 only, with fix suggestions)
```

## Key Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Orchestration logic and full documentation |
| `prompts/hard-gate-validator.md` | 5-gate validation framework |
| `prompts/banned-patterns-registry.md` | Anti-patterns to auto-reject |
| `prompts/data-feasibility-framework.md` | Data accessibility assessment |

## Architecture

```
blueprint-turbo
      |
      v (invokes after Synthesis)
blueprint-validator
      |
      ├── Loads: hard-gate-validator.md
      ├── Loads: banned-patterns-registry.md
      ├── Loads: data-feasibility-framework.md
      |
      v (returns)
Validated/Rejected/Revision segments
      |
      v
blueprint-turbo Wave 3 (messaging)
```

## Invoking Skills

- **blueprint-turbo** - Invokes validator at Hard Gate Checkpoint
- **blueprint-pvp-deep** - Invokes validator for PVP concept validation

## Version

**Version:** 1.0.0 (December 2025)

**Principle:** Quality enforcement is non-negotiable. Pass = ship it. Fail = destroy it. No "close enough."

## Related Skills

- **blueprint-turbo** - Fast GTM execution (12-15 min)
- **blueprint-pvp-deep** - Gold Standard 8.0+ PVP generation
- **blueprint-gtm-complete** - Original thorough execution (30-45 min)
