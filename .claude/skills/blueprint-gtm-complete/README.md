# Blueprint GTM Complete - All-in-One Skill

## Overview

This skill combines all four Blueprint GTM stages into a single automated workflow:

1. **Company Research** - Analyze company, identify ICP, define personas, develop pain segments
2. **Data Research** - Validate segments with hard government data sources
3. **Message Generation** - Generate and validate PQS/PVP messages (8.0+/10 only)
4. **Explainer Builder** - Create mobile-responsive HTML playbook

## How to Invoke

### Simple Invocation (Just URL)
```
Run blueprint-gtm-complete for https://constanttherapyhealth.com/constant-therapy/
```

### With Context
```
Run blueprint-gtm-complete for https://constanttherapyhealth.com/constant-therapy/ targeting clinicians
```

### Example for Your Use Case
```
Analyze https://constanttherapyhealth.com/constant-therapy/ using blueprint-gtm-complete, focusing on clinicians as the target persona and using Mimidata labs for healthcare data validation.
```

## What You'll Get

**Single HTML File:** `blueprint-gtm-playbook-constanttherapy.html`

**Contents:**
- Complete company analysis
- Validated pain segments with hard data sources
- 3-6 buyer-validated messages (PQS + PVP)
- Implementation blueprints for each message
- Mobile-responsive design with Blueprint branding

## Execution Time

**Total:** 30-45 minutes (fully automated)
- Stage 1 (Company Research): 10-15 min
- Stage 2 (Data Research): 10-15 min
- Stage 3 (Message Generation): 10-15 min
- Stage 4 (Explainer Builder): 5 min

## Healthcare-Specific Features

When analyzing healthcare companies:
- Automatically searches CMS, CDC, state licensing boards
- Prioritizes Mimidata labs datasets
- Focuses on clinician personas (SLPs, OTs, PTs, neurologists)
- Emphasizes compliance and quality metrics
- Uses facility-level government data

## Data Sources Prioritized

**Healthcare:**
- CMS provider data (quality ratings, survey results)
- State licensing boards (disciplinary actions)
- CDC databases
- OSHA healthcare violations
- Mimidata labs pre-processed datasets

**General:**
- EPA ECHO (environmental violations)
- OSHA enforcement
- FDA inspections
- FMCSA/SAFER (transportation)
- State-specific compliance databases

## Quality Standards

All stages maintain Blueprint GTM core principles:
- **Hard data only** - Government databases with record numbers
- **Buyer-centric** - Everything evaluated from buyer perspective
- **Texada-level specificity** - Hyper-specific, factually grounded
- **Provable claims** - Every data claim verified
- **High bar** - Only 8.0+/10 messages in final deliverable

## Comparison to Individual Skills

### Using Individual Skills
```
1. Run blueprint-company-research for [URL]
   → Wait for completion, review results
2. Run blueprint-data-research with results from step 1
   → Wait for completion, review results
3. Run blueprint-message-generation with results from step 2
   → Wait for completion, review results
4. Run blueprint-explainer-builder with results from step 3
   → Receive final HTML
```
**Time:** 30-45 minutes + manual transitions
**User input:** 4 separate invocations

### Using blueprint-gtm-complete
```
Run blueprint-gtm-complete for [URL]
   → Automatic execution of all 4 stages
   → Receive final HTML
```
**Time:** 30-45 minutes (fully automated)
**User input:** 1 invocation

## File Location

**Skill File:** `.claude/skills/blueprint-gtm-complete/SKILL.md`
**Size:** ~53KB
**Format:** Markdown with YAML front matter

## Troubleshooting

**Issue:** Skill not found
**Fix:** Ensure `.claude/settings.local.json` includes:
```json
"Skill(blueprint-gtm-complete)"
```

**Issue:** No HIGH feasibility segments found
**Result:** Skill will suggest pivoting to alternative segments based on available data

**Issue:** Messages scoring below 8.0/10
**Result:** Skill auto-revises (max 2 attempts) or destroys and generates new variants

## Example Output Structure

```
blueprint-gtm-playbook-constanttherapy.html
├── Jordan's Bio & Philosophy
├── Old Way vs New Way
├── PQS Play 1: [e.g., Recent CMS Quality Drop]
├── PQS Play 2: [e.g., State Licensing Renewal Due]
├── PQS Play 3: [e.g., OSHA Patient Handling Violation]
├── PVP Play 1: [e.g., Pre-Pulled Compliance Deadlines]
├── PVP Play 2: [e.g., Quality Metric Analysis]
├── PVP Play 3: [e.g., Inspection Schedule Research]
└── Transformation Narrative
```

## Notes

- All four stages execute automatically without pausing
- No manual handoffs between stages required
- Healthcare data sources (CMS, Mimidata labs) automatically prioritized for healthcare companies
- Clinician personas automatically focused when analyzing therapy/medical companies
- Final HTML is self-contained (inline CSS, no external dependencies)

## Next Steps After Completion

1. **Review HTML file** - Check all messages and data sources
2. **Share with stakeholders** - Mobile-responsive, ready to forward
3. **Begin implementation** - Use data recipes and targeting criteria
4. **Track results** - Monitor reply rates by message variant

---

**Created:** 2025-11-07
**Version:** 1.0.0
**Status:** Production Ready
