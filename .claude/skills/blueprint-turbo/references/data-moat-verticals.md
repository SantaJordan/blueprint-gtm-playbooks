# Data Moat Verticals Reference

**Purpose:** Pre-scored vertical catalog for rapid segment qualification. Use during Wave 1 to convert generic verticals to regulated niches with data moats.

---

## Quick Reference: Tier 1 Verticals (Score 30+/40)

These verticals ALWAYS qualify. Use when available.

| Vertical | Key Database | Update Freq | Pain Signal |
|----------|-------------|-------------|-------------|
| Nursing Homes | CMS Care Compare | Monthly | <3 stars, staffing deficiencies |
| Chemical Plants | EPA ECHO | Weekly | Open violations, consent decrees |
| Trucking Companies | FMCSA SAFER | Daily | Conditional/Unsatisfactory rating, OOS% |
| Food Manufacturing | FDA Warning Letters | Weekly | 483s, warning letters, recalls |
| Restaurants (Major Cities) | Local Health Dept | Daily-Weekly | Grade drops, critical violations |
| Construction (Heavy Equipment) | State DOT Permits | Daily | Permit gaps = idle equipment |
| Multi-State Insurance Agents | NIPR | Daily | New licenses, CE requirements |
| Licensed Real Estate Agents | State RE Boards | Weekly | License status, disciplinary actions |
| Home Healthcare Agencies | CMS Home Health Compare | Quarterly | Star ratings, patient outcomes |
| Dialysis Centers | CMS Dialysis Compare | Monthly | Star ratings, infection rates |

---

## Auto-Reject Verticals (NEVER Use as Primary)

These verticals have NO data moat. Do NOT proceed without niche conversion.

| Generic Vertical | Why No Data Moat | Required Conversion |
|------------------|------------------|---------------------|
| "SaaS companies" | No regulatory body | → Look at THEIR customers (regulated industries) |
| "Tech startups" | No regulatory body | → Find regulated verticals they serve |
| "B2B companies" | Too generic | → Must specify operational context |
| "Sales teams" (generic) | No regulatory body | → Insurance agents, RE agents, Financial advisors |
| "Growing companies" | Soft signal only | → Must have compliance/operational pain |
| "Funded companies" | Soft signal only | → Funding ≠ specific pain |
| "Marketing teams" | No regulatory body | → None (Blueprint-incompatible) |
| "HR departments" | No regulatory body | → None (Blueprint-incompatible) |
| "Professional services" | Too generic | → Licensed contractors, accountants, engineers |

---

## Niche Conversion Table

When you encounter a generic vertical, convert to a regulated niche:

### "Sales Teams" → Regulated Niches

| Regulated Niche | Data Source | Pain Signal | Score |
|-----------------|-------------|-------------|-------|
| Multi-state insurance agents | NIPR, State DOI | New licenses, CE deadlines | 35/40 |
| Licensed real estate agents | State RE boards | License expirations, MLS access | 32/40 |
| Financial advisors | FINRA BrokerCheck | Disclosures, disciplinary actions | 28/40 |
| Mortgage loan officers | NMLS Consumer Access | License status, education requirements | 30/40 |
| Securities representatives | SEC IARD | Form ADV, registration status | 26/40 |

### "Professional Services" → Regulated Niches

| Regulated Niche | Data Source | Pain Signal | Score |
|-----------------|-------------|-------------|-------|
| Licensed contractors | State licensing boards | Bond expiration, complaint history | 32/40 |
| Licensed engineers | State PE boards | License renewals, disciplinary actions | 28/40 |
| Certified accountants | State CPA boards | CPE requirements, ethics violations | 26/40 |
| Architects | State licensing boards | License status, project approvals | 24/40 |
| Attorneys | State Bar associations | Disciplinary records, CLE requirements | 30/40 |

### "Healthcare" → Regulated Niches

| Regulated Niche | Data Source | Pain Signal | Score |
|-----------------|-------------|-------------|-------|
| Nursing homes | CMS Nursing Home Compare | <3 stars, staffing deficiencies | 38/40 |
| Home health agencies | CMS Home Health Compare | Star drops, patient outcomes | 35/40 |
| Dialysis centers | CMS Dialysis Compare | Infection rates, star ratings | 35/40 |
| Hospice providers | CMS Hospice Compare | Quality measures, complaints | 32/40 |
| DME suppliers | CMS DME Compare | Accreditation, claims data | 28/40 |
| Ambulatory surgery centers | State health dept + CMS | Inspection deficiencies | 30/40 |

### "Food Service" → Regulated Niches

| Regulated Niche | Data Source | Pain Signal | Score |
|-----------------|-------------|-------------|-------|
| Restaurants (NYC, LA, Chicago, SF) | Local health dept APIs | Grade drops, critical violations | 36/40 |
| Food manufacturers | FDA Warning Letters | 483s, warning letters | 38/40 |
| Food distributors | FDA + state licensing | Temperature violations, recalls | 32/40 |
| Commercial kitchens | Local health dept | Inspection failures | 30/40 |
| Catering companies | State licensing | License status, complaints | 26/40 |

### "Logistics/Transportation" → Regulated Niches

| Regulated Niche | Data Source | Pain Signal | Score |
|-----------------|-------------|-------------|-------|
| Motor carriers (trucking) | FMCSA SAFER | Safety rating, OOS%, crash rate | 40/40 |
| Freight brokers | FMCSA Broker Search | Bond status, authority | 35/40 |
| Hazmat carriers | FMCSA + PHMSA | HM permit status, violations | 38/40 |
| Part 135 air carriers | FAA Registry | Certificate status, aircraft age | 28/40 |
| Passenger carriers (bus) | FMCSA | Safety rating, driver violations | 36/40 |

### "Manufacturing" → Regulated Niches

| Regulated Niche | Data Source | Pain Signal | Score |
|-----------------|-------------|-------------|-------|
| Chemical manufacturers | EPA ECHO | Air/water violations, permits | 40/40 |
| Metal fabricators | OSHA inspections | Serious citations, repeat violations | 35/40 |
| Food processors | FDA + OSHA | 483s, workplace injuries | 38/40 |
| Pharmaceutical mfg | FDA Warning Letters | cGMP violations, consent decrees | 40/40 |
| Medical device mfg | FDA 510(k) + Warning Letters | Recalls, quality system issues | 38/40 |

---

## Data Moat Scoring Rubric

Score each vertical on 4 criteria (0-10 each, max 40):

### Criterion 1: Regulatory Footprint (0-10)

| Score | Description |
|-------|-------------|
| 10 | Heavy federal regulation with searchable databases (EPA, OSHA, CMS, FDA, FMCSA) |
| 8-9 | Federal + state regulation, multiple databases |
| 6-7 | State-level licensing with public lookup portals |
| 4-5 | Industry self-regulation with some disclosure |
| 2-3 | Voluntary certifications only |
| 0-1 | No regulatory oversight |

### Criterion 2: Compliance-Driven Pain (0-10)

| Score | Description |
|-------|-------------|
| 10 | Violations directly create the pain the solution solves |
| 8-9 | Regulations force behaviors creating solution-relevant pain |
| 6-7 | Compliance requirements indirectly create pain |
| 4-5 | Regulations exist but weak connection to solution |
| 2-3 | Voluntary compliance creates mild pain |
| 0-1 | No compliance-driven pain |

### Criterion 3: Data Accessibility (0-10)

| Score | Description |
|-------|-------------|
| 10 | Free public API with documented fields, daily updates |
| 8-9 | Free API or portal, weekly updates |
| 6-7 | Free portal, monthly updates |
| 4-5 | Paid API ($200-500/mo) or manual access |
| 2-3 | Expensive API (>$500/mo) or difficult manual |
| 0-1 | Data doesn't exist or is proprietary |

### Criterion 4: Specificity Potential (0-10)

| Score | Description |
|-------|-------------|
| 10 | Record numbers, violation IDs, dates, facility addresses all available |
| 8-9 | Multiple specific identifiers, dates available |
| 6-7 | Some specific fields, entity identification |
| 4-5 | Basic entity data, limited specificity |
| 2-3 | Aggregate data only |
| 0-1 | No specific data available |

---

## Decision Logic

```
Calculate Total Score (sum of 4 criteria, max 40)

>= 30: PROCEED as Tier 1 (Government Data)
       → HIGH confidence, pure PQS messages possible

25-29: PROCEED as Tier 2 (Hybrid Approach)
       → MEDIUM confidence, requires 2-3 source combination

20-24: CONDITIONAL (Try Harder First)
       → Search for internal data + external data combinations
       → If promising hybrid found: PROCEED
       → If no good combination: WARN user, suggest alternatives

< 20:  REJECT VERTICAL
       → Do NOT proceed without finding better niche
       → Suggest alternative niches from conversion table
```

---

## Usage During Wave 1

1. **Identify verticals** from company website/research
2. **Check Auto-Reject list** - if matched, MUST convert to niche
3. **Look up scores** in Niche Conversion Tables
4. **Select highest-scoring niche** (must be ≥25/40)
5. **If no niche qualifies**: Search for internal data opportunities
6. **Proceed to Wave 2** with selected niche, not generic vertical

---

## Example: Blinq (Digital Business Cards)

**Generic Verticals Identified:** "Sales teams, professional services, insurance, real estate"

**Auto-Reject Check:**
- "Sales teams" → AUTO-REJECT (no regulatory body)
- "Professional services" → AUTO-REJECT (too generic)

**Niche Conversion:**
- "Sales teams" → Multi-state insurance agents (NIPR) = 35/40 ✅
- "Sales teams" → Licensed real estate agents = 32/40 ✅
- "Professional services" → Licensed contractors = 32/40 ✅

**Selected Niche:** Multi-state insurance agents (highest score: 35/40)

**Proceed to Wave 2 with:** Insurance agents (NIPR data), NOT "Sales teams"

---

## Version & Maintenance

**Version:** 1.0.0 (November 2025)

**Adding New Verticals:** When you discover a high-value vertical, add to appropriate section with:
- Data source(s)
- Pain signal(s)
- Score (using rubric above)
