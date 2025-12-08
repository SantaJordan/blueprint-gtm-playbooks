# Banned Patterns Registry

**Purpose:** Exhaustive list of patterns that AUTOMATICALLY trigger rejection. Reference during synthesis, drafting, and evaluation phases.

**Rule:** If ANY banned pattern appears, message is AUTO-DESTROYED regardless of other scores.

---

## Category 1: Generic Growth Signals (ALWAYS BANNED)

These signals apply to ANY scaling company and indicate NOTHING about specific pain.

| Banned Signal | Why Banned | Example to Reject |
|---------------|------------|-------------------|
| "Recently raised Series A/B/C/D" | All funded companies raise money | "Congrats on your $15M Series B..." |
| "Hiring for [role type]" | All scaling companies hire | "Noticed you're hiring 5 sales reps..." |
| "Growing headcount" | Generic growth indicator | "Your team grew from 50 to 75..." |
| "Expanding to new markets/offices" | Growth activity, not pain | "Saw you're expanding to Chicago..." |
| "Recent M&A activity" | Strategic move, not operational pain | "After your acquisition of XYZ..." |
| "IPO/going public" | Financial milestone, not pain | "As you prepare for your IPO..." |
| "New product launch" | Company activity, not pain | "Congrats on launching your new product..." |
| "Leadership change" | Organizational, not operational | "Saw you have a new VP of Sales..." |

**Detection Pattern:** Message references company activity/milestone rather than operational/compliance situation.

---

## Category 2: Soft Data Sources (BANNED as Primary Signal)

These data sources provide firmographics, not pain indicators.

| Banned Source | Why Banned | What It Actually Shows |
|---------------|------------|------------------------|
| Crunchbase | Company directory | Funding rounds, investor names |
| Apollo.io | Contact enrichment | Employee counts, email addresses |
| ZoomInfo | Firmographics | Revenue estimates, tech stack |
| LinkedIn Company Page | Company profile | Employee counts, job postings |
| LinkedIn Sales Navigator | Prospecting tool | Org charts, job changes |
| PitchBook | Financial data | Valuations, deal flow |
| CB Insights | Market research | Industry trends, signals |
| Owler | Competitive intel | Revenue estimates, news |
| Dun & Bradstreet | Credit scores | Credit ratings (paywalled) |
| Secretary of State filings | Entity status | Active/dissolved (no pain data) |

**Exception:** These sources can be used as SECONDARY enrichment IF:
1. Primary signal comes from regulatory/operational database
2. Secondary source adds contact info or firmographics only
3. NEVER used to infer pain

---

## Category 3: Industry-Wide Statistics (BANNED in Mirror Section)

Statistics that apply to thousands of companies are NOT specific insights.

| Banned Pattern | Example to Reject | Why Banned |
|----------------|-------------------|------------|
| "Industry average is X%" | "The average restaurant pays 28% in delivery fees" | Applies to ALL restaurants |
| "Companies like yours typically..." | "Companies like yours typically see 20-30% inefficiency" | Not about THEM specifically |
| "Research shows that..." | "Research shows 73% of sales teams struggle with..." | Generic stat, not their data |
| "According to Gartner/Forrester..." | "Gartner says 45% of companies..." | Industry report, not specific |
| "[N]% of [industry] faces..." | "63% of manufacturers face compliance challenges" | Could be them, could be anyone |
| "The typical [role] spends..." | "The typical ops manager spends 10 hours on X" | Generic persona stat |

**Exception:** Aggregates are ALLOWED when:
1. Comparing THEIR specific data to an aggregate
2. Format: "Your [specific metric] vs [aggregate benchmark]"
3. Example ALLOWED: "Your 18.4 visits per 1000 residents vs state average of 28.1"

---

## Category 4: Weak Causal Links (BANNED)

Signals that DON'T prove the specific pain the product solves.

| Weak Signal | Claimed Pain | Why Causal Link Fails |
|-------------|--------------|----------------------|
| "Raised funding" | "Need efficiency" | Funding doesn't prove inefficiency |
| "Hiring sales reps" | "Sales process issues" | Could be successful expansion |
| "High review velocity" | "Operational strain" | Could indicate success, not strain |
| "Job posting for [role]" | "Gap in that function" | Normal hiring, not crisis |
| "Tech stack includes X" | "Problems with X" | Using tool ≠ having problems |
| "Company size of N" | "Scale problems" | Size doesn't prove specific pain |
| "Industry is [sector]" | "Sector-specific pain" | Being in sector ≠ experiencing pain |

**Strong Causal Link Test:** Ask "Could a company have this signal but NOT have the pain?"
- If YES → Weak causal link → BANNED
- If NO → Strong causal link → ALLOWED

**Examples of STRONG Causal Links:**
- Open EPA violation → PROVES compliance pressure
- CMS <3 star rating → PROVES quality improvement mandate
- FMCSA Conditional rating → PROVES safety intervention required
- Health dept grade drop → PROVES operational failure

---

## Category 5: Undetectable Data Sources (BANNED)

Technologies or situations that CANNOT be reliably detected from outside.

| Claimed Detection | Why Impossible | Reality |
|-------------------|----------------|---------|
| "BuiltWith for digital business cards" | No web footprint | Digital cards live in mobile apps, not on corporate domains |
| "CRM data quality issues" | Internal system | Can't see CRM data from outside |
| "Sales cycle length" | Internal metric | Not externally observable |
| "Employee satisfaction" | Internal sentiment | Glassdoor is anecdotal, not systematic |
| "Internal process inefficiency" | Operational | Can't prove without inside access |
| "Management decisions" | Strategic | Not detectable externally |
| "Budget constraints" | Financial | Not publicly visible |
| "Tool adoption rates" | Internal usage | Can't see login/usage data |

**Technical Feasibility Test:** Can you explain MECHANICALLY how you detect this?
- API field name?
- Web scraping selector?
- Database query?

If you can't explain the detection mechanism → BANNED

---

## Category 6: Banned Phrases (Auto-Reject Triggers)

These phrases signal generic, template-based messaging.

### Opening Phrases (BANNED)

| Phrase | Why Banned |
|--------|------------|
| "I noticed you..." | Template opener, usually followed by obvious info |
| "Congrats on..." | Generic flattery |
| "I saw that you..." | Usually references public info they know |
| "I came across your..." | Vague, could be anyone |
| "As a [role] at [company type]..." | Generic persona addressing |
| "Companies in your space..." | Not specific to them |
| "Leaders like you..." | Flattery, not insight |

### Middle Phrases (BANNED)

| Phrase | Why Banned |
|--------|------------|
| "Based on our research..." | What research? Vague source |
| "Our data shows that..." | Unverifiable internal claim |
| "Industry trends suggest..." | Generic, not specific |
| "You might be experiencing..." | Guessing at their pain |
| "Companies like yours often..." | Not about them specifically |
| "It's common for [role] to..." | Generic persona assumption |

### Closing Phrases (BANNED)

| Phrase | Why Banned |
|--------|------------|
| "Let's hop on a quick call..." | Value gated behind meeting |
| "I'd love to show you..." | Requires commitment for value |
| "When would be a good time to..." | Forces scheduling |
| "Can we set up 15 minutes..." | Meeting-dependent value |
| "Click here to learn more..." | Generic CTA |
| "Reply to this email if interested..." | Low-value CTA |

### Allowed CTA Patterns

| Allowed Pattern | Why It Works |
|-----------------|--------------|
| "Want the list of [specific thing]?" | Concrete value, one-word reply |
| "Reply 'yes' for the full report" | Zero friction |
| "Want intro to [Name] at [Company]?" | Complete info, specific action |
| "Want to see how your [metric] compares?" | Specific curiosity hook |

---

## Category 7: Blinq-Specific Failures (Case Study Reference)

These specific patterns caused the Blinq playbook failure:

| Pattern | Why It Failed | What Should Have Been |
|---------|---------------|----------------------|
| "Series A-C funding + hiring sales" | Generic growth signals, no pain connection | NIPR license data showing new agents |
| "BuiltWith for digital card detection" | Technology leaves no web footprint | State licensing board for card requirements |
| "23% capture rate industry stat" | Industry-wide, not company-specific | Their specific agent count vs license count |
| "Companies with rapid sales growth" | Applies to everyone in ICP | Agencies with 10+ new licenses in 45 days |
| "CRM sync speed benchmark" | Can't see their CRM from outside | CE requirement deadlines from NIPR |
| "Adoption rate industry average" | Generic stat, not their data | Specific compliance gap calculation |

---

## Validation Checklist

Before ANY message proceeds, verify NONE of these patterns appear:

### Quick Scan (30 seconds)

- [ ] No growth signals (funding, hiring, expansion, M&A)
- [ ] No soft data sources as primary (Crunchbase, Apollo, ZoomInfo, LinkedIn)
- [ ] No industry-wide statistics without their specific data
- [ ] No weak causal links (signal doesn't prove pain)
- [ ] No undetectable data claims
- [ ] No banned phrases (opening, middle, closing)

### If ANY box is UNCHECKED → AUTO-DESTROY

No exceptions. No "well, in this case..." rationalizations.

---

## How to Use This Registry

### During Synthesis (Phase 1)

Before generating synthesis insight:
1. Check if data sources are in banned list → If yes, don't use
2. Check if insight relies on weak causal link → If yes, strengthen or reject
3. Check if insight uses industry-wide stat → If yes, make company-specific

### During Drafting (Phase 2)

Before completing message draft:
1. Scan for banned phrases → Remove or rewrite
2. Verify data source is detectable → If not, don't claim
3. Confirm causal link is strong → If weak, restructure

### During Evaluation (Phase 3)

Before scoring:
1. Run quick scan checklist
2. If ANY banned pattern found → AUTO-DESTROY (don't even score)
3. Proceed to scoring only if clean

---

## Adding New Banned Patterns

When you identify a new pattern that should be banned:

```markdown
### New Banned Pattern: [Name]

**Category:** [1-7 or new category]

**Pattern Description:**
[What it looks like]

**Why It's Banned:**
[Why this doesn't work for Blueprint GTM]

**Example to Reject:**
[Specific message example]

**Detection Method:**
[How to identify this pattern]
```

---

**Version:** 1.0.0 (November 2025)

**Principle:** When in doubt, ban it. False positives (rejecting okay messages) are better than false negatives (shipping bad messages).
