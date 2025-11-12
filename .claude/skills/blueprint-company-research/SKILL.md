---
name: blueprint-company-research
description: Research a company to identify pain-qualified segments, ideal customer profile, and target personas. Use when starting Blueprint GTM analysis with a company URL. Always visits live website first.
---

# Blueprint GTM Company Research

## Purpose

Analyze a target company to identify Pain-Qualified Segments (PQS) - specific situations where prospects experience measurable pain that the company's solution addresses. This is Stage 1 of the Blueprint GTM Intelligence System.

## Methodology Reference

This skill implements the Blueprint GTM v1.1.0 methodology. For detailed guidance on:
- PVP vs PQS distinction (8.5+ threshold for TRUE PVPs, 7.0-8.4 for Strong PQS)
- Independently Useful Test (complete actionable information requirements)
- Data tier framework (Tier 1: Government, Tier 2: Hybrid, Tier 3: Competitive/Velocity)
- Message scoring rubrics and quality standards

See: `references/methodology.md`

## When to Use This Skill

- User provides a company URL and wants Blueprint GTM analysis
- User asks to "research [company]" or "analyze [company] for GTM"
- Starting a new Blueprint GTM engagement
- Need to understand a company's ICP, persona, and pain segments

## Requirements

**Input Required:**
- Company website URL (required)

**No Dependencies:** This is the entry point skill for Blueprint GTM analysis

## Workflow

### Phase 1: Live Website Analysis (ALWAYS REQUIRED)

**CRITICAL:** You MUST visit and analyze the live website. Never rely on cached knowledge.

Visit the company's website and document:

1. **Core Offering**: What specific products/services do they sell?
2. **Value Proposition**: How do they position themselves? What benefits do they claim?
3. **Target Markets**: What industries or customer types are mentioned?
4. **Customer Evidence**: Case studies, testimonials, customer logos visible?
5. **Pricing Model**: Any pricing information available?
6. **Recent Updates**: News, blog posts, product launches?
7. **Unique Angle**: What makes them different from typical vendors in their space?

**Output Section 1: Company Context**

```markdown
## Company Context

**Company Name:** [Official name from website]

**Core Offering:** [Specific products/services - not generic categories]

**Primary Value Proposition:** [How they position themselves, in their words]

**Unique Advantage:** [What differentiates them - especially data/intelligence capabilities]

**Target Markets Mentioned:** [Industries, company types, use cases from website]

**Website Analysis Date:** [Today's date]
```

### Phase 2: Deep ICP Research

Now research beyond the website to understand who their typical customers are.

**Research Strategy:**

1. **Review Site Analysis:**
   - Look for customer testimonials with company names
   - Check case studies for customer details
   - Note any customer logos or partner mentions

2. **Search for Reviews:**
   - Search: "[Company] reviews" on G2, Capterra, TrustRadius
   - Look for common customer characteristics in reviews
   - Note what types of companies praise them

3. **Find Patterns:**
   - What industries appear repeatedly?
   - What company sizes are mentioned?
   - What job titles write reviews?
   - What problems are they solving?

4. **Research Customer Examples:**
   - If customers are named, look them up
   - What industry are they in?
   - Approximate size/scale?
   - What likely pain points do they have?

**Output Section 2: Ideal Customer Profile**

```markdown
## Ideal Customer Profile (ICP)

**Industries Served:** [Specific industries based on evidence, not assumptions]

**Company Scale Indicators:**
- Employee range: [Typical size]
- Revenue indicators: [If discernible]
- Operational scale: [Number of locations, transaction volume, etc.]

**Common Operational Context:**
- Key processes: [What operations do these customers manage?]
- Typical workflows: [Day-to-day activities]
- Technology environment: [What systems do they likely use?]
- Regulatory environment: [Industry-specific compliance requirements]

**Key Business Pains & Goals:**
[Document specific challenges mentioned in reviews, case studies, or inferred from their industry]

**Source Evidence:**
- [List where you found this information: website case studies, G2 reviews, etc.]
```

### Phase 3: Second-Layer Analysis

Understand the external forces affecting the ICP by researching THEIR customers.

**Research Focus:**

1. **Identify ICP's Customers**: Who do your target customers serve?
   - B2B company? Research their customer industries
   - B2C company? Research consumer behavior in their market
   - Service provider? Research their end clients

2. **Market Dynamics**: Search for trends affecting the ICP's customers
   - "[ICP industry] market trends 2025"
   - "[ICP industry] challenges"
   - "[ICP industry] regulatory changes"

3. **External Pressures**: What forces create urgency for the ICP?
   - Economic factors (labor costs, supply chain, etc.)
   - Technology shifts (AI adoption, platform migrations, etc.)
   - Regulatory changes (new compliance requirements)
   - Competitive pressures

**Output Section 3: Second-Layer Context**

```markdown
## Second-Layer Analysis (ICP's Market Environment)

**ICP's Customer Industries:** [Who do they serve?]

**Key Market Dynamics Affecting ICP:**
- [Trend 1 and its impact on ICP]
- [Trend 2 and its impact on ICP]
- [Trend 3 and its impact on ICP]

**External Pressures Creating Pain:**
- [Pressure 1: e.g., rising labor costs]
- [Pressure 2: e.g., new compliance requirements]
- [Pressure 3: e.g., customer expectations changing]

**Source Evidence:**
- [Industry reports, news articles, government sources referenced]
```

### Phase 4: Target Persona Research

Identify the specific person within the ICP who experiences the pain.

**Research Strategy:**

1. **Determine Decision-Maker**: Based on the solution type, who would buy this?
   - Enterprise software? CTO, VP Engineering, Director of IT?
   - Compliance tool? Chief Compliance Officer, VP Risk?
   - Sales/Marketing tool? CRO, CMO, VP Sales?

2. **Search for Job Descriptions**:
   - "[Persona title] job description [ICP industry]"
   - Look for: responsibilities, required skills, KPIs, pain points mentioned

3. **Find Persona Discussions**:
   - Search LinkedIn for posts from people with that title in target industries
   - Look for forum discussions (Reddit, industry forums)
   - Check professional articles written BY that persona

4. **Understand Their World**:
   - What do they measure success on?
   - What keeps them up at night?
   - What information do they lack access to?
   - What would genuinely impress them?

**Output Section 4: Target Persona Profile**

```markdown
## Target Persona

**Primary Job Title:** [Specific title - not generic]

**Alternative Titles:** [Other titles for same role]

**Key Responsibilities:**
- [Specific duty 1]
- [Specific duty 2]
- [Specific duty 3]

**Daily Workflow Context:** [What their typical day looks like]

**Primary KPIs:** [What they're measured on - be specific]

**Core Pains & Frustrations:**
[Documented frustrations relevant to the solution space, from job descriptions, forums, LinkedIn discussions]

**Information Environment:**
- **What they know**: [Data/systems they have access to]
- **Blind spots**: [Information gaps they face]
- **What impresses them**: [What insights would make them say "holy shit"?]

**Value Drivers:** [What outcomes matter most to their success?]

**Source Evidence:**
- [Job postings analyzed, forums reviewed, LinkedIn searches, etc.]
```

### Phase 5: Pain-Qualified Segment Hypothesis

Synthesize everything into 3-5 specific painful situations.

**Critical Principles:**

1. **Specificity over generality**: "Struggling with FedRAMP compliance after failed audit" beats "needs better security"
2. **Timing matters**: The pain must be happening NOW, not theoretically
3. **Data detectability**: Consider how you'd identify companies in this situation
4. **Brand relevance**: The pain must directly connect to what the company solves
5. **Data completeness for PVPs** (v1.1.0): Consider whether public data provides COMPLETE actionable information (names, contacts, prices) or just pain identification. Most segments will generate Strong PQS (7.0-8.4), not TRUE PVPs (8.5+).

**Understanding PVP vs PQS Potential:**

- **TRUE PVP potential**: Data sources provide complete action info (agent contacts, vendor pricing, mechanic names with LinkedIn profiles)
- **Strong PQS potential**: Data sources identify pain with specificity (violations, deadlines, benchmarks) but lack complete action info
- **Realistic expectation**: Most segments are Strong PQS opportunities - this is success! TRUE PVPs are rare and require specific data (contacts, prices, names).

**For Each Segment, Document:**

- **Segment Name**: Descriptive title capturing the situation
- **Trigger Event/Situation**: What specific event or condition creates this pain NOW?
- **Core Pain/Challenge**: What friction, inefficiency, risk, or mistake are they experiencing?
- **Why This Matters to [Company]**: How does this pain relate to the company's unique value?
- **Initial Data Hypothesis**: What public data might reveal companies in this situation?
- **Data Completeness Level**: Does this data provide complete actionable information (TRUE PVP potential) or pain identification only (Strong PQS)?

**Output Section 5: Pain-Qualified Segment Hypotheses**

```markdown
## Pain-Qualified Segment Hypotheses

### Segment 1: [Descriptive Name]

**Trigger Event/Situation:**
[What specific, observable event or condition creates this pain? Examples:
- Failed compliance audit requiring remediation
- Rapid headcount growth straining existing systems
- M&A integration creating operational chaos
- Major customer loss revealing operational gaps]

**Core Pain/Challenge:**
[What specific friction, inefficiency, risk, or mistake is the prospect experiencing RIGHT NOW?]

**Brand Relevance:**
[Why is this segment highly relevant for [Company Name]? Connect the pain directly to their unique solution/positioning/data advantage.]

**Initial Data Hypothesis:**
[What types of HARD public data might reveal companies in this situation? Focus on:
- Regulatory violation records (EPA ECHO, OSHA enforcement, FDA inspections)
- Compliance databases (FMCSA/SAFER, state licensing violations)
- Government enforcement actions with specific dates and record numbers
- Permit applications/denials with facility-specific details
- Court records, UCC filings, regulatory deadlines
- Operational metrics from government databases

AVOID soft signals like job postings, M&A activity, and generic industry trends - these apply too broadly and aren't specific enough]

**Data Completeness Level (v1.1.0):**
[Assess whether this data enables TRUE PVP (8.5+) or Strong PQS (7.0-8.4):
- **TRUE PVP potential**: Data includes complete actionable information (contact names, phone/email, prices, vendor lists)
- **Strong PQS potential**: Data identifies pain with specificity (violation numbers, deadlines, facility addresses) but lacks complete contact info
- Note: Most segments will be Strong PQS - this is excellent and should be labeled as success!]

---

### Segment 2: [Descriptive Name]
[Same structure]

---

### Segment 3: [Descriptive Name]
[Same structure]

---

[Continue for 3-5 segments total]
```

## Complete Output Format

Compile all sections into a single structured document:

```markdown
# Blueprint GTM Research Report: [Company Name]

**Date:** [Today's date]
**Analyst:** [Your name/role]
**Stage:** Company Research (Stage 1 of 3)

---

## Company Context
[Section 1 content]

---

## Ideal Customer Profile (ICP)
[Section 2 content]

---

## Second-Layer Analysis
[Section 3 content]

---

## Target Persona
[Section 4 content]

---

## Pain-Qualified Segment Hypotheses
[Section 5 content]

---

## Next Steps

This research provides the foundation for Stage 2: Data Source Research.

**Ready for Stage 2:** The blueprint-data-research skill will validate which segments are detectable using public data sources and create specific "Pain Data Recipes" for each segment.

**To proceed:** Run blueprint-data-research skill with this output as input.
```

## Quality Checklist

Before completing, verify:

- [ ] Website was visited and analyzed (not relying on cached knowledge)
- [ ] ICP is based on actual evidence (reviews, case studies, customer examples)
- [ ] Second-layer analysis connects to real market forces
- [ ] Persona profile is specific to a real job title with researched details
- [ ] Each pain segment has a clear trigger event and current timing
- [ ] Each pain segment connects to the company's unique value
- [ ] At least 3 pain segments identified (ideally 4-5)
- [ ] Initial data hypotheses are plausible and specific
- [ ] Source evidence is documented throughout

## Common Pitfalls to Avoid

1. **Generic Pain Points**: "Needs to save time" or "wants to reduce costs" are too vague
   - ✅ Better: "Burning 40 hours/month manually reconciling data from 3 disconnected systems"

2. **Assuming vs. Researching**: Don't assume the ICP based on the solution category
   - ✅ Better: Find actual customer examples and build profile from evidence

3. **Ignoring the Persona's Context**: Understanding WHAT they do isn't enough
   - ✅ Better: Understand what they're measured on, what impresses them, what blind spots they have

4. **Segments Without Timing**: "Companies that need X" is static
   - ✅ Better: "Companies experiencing Y trigger event that creates urgent need for X"

5. **Undetectable Segments**: "Companies that are frustrated" - how would you find them?
   - ✅ Better: Consider from the start whether public data could reveal this situation

## Integration with Other Skills

**This Skill Feeds Into:**
- `blueprint-data-research` (Stage 2): Takes pain segment hypotheses and validates with data sources

**Depends On:** Nothing (this is the entry point)

**Expected Usage Pattern:**
```
User: "Run Blueprint GTM analysis for https://company.com"
→ Claude automatically invokes this skill
→ Produces research report
→ Claude recognizes need for Stage 2
→ Automatically invokes blueprint-data-research with this output
```

## Tips for Consultants

1. **Start Broad, Then Narrow**: Phase 1-2 cast a wide net; Phase 4-5 focus sharply
2. **Evidence Over Assumptions**: Every claim should trace to a source
3. **Think Like a Detective**: Follow customer breadcrumbs across the web
4. **Consider the Recipient**: Would a VP in this role find your segment hypothesis credible?
5. **Quality > Quantity**: 3 strong segments beat 7 weak ones

## References

- See `references/methodology.md` for complete Blueprint GTM v1.1.0 methodology (PVP vs PQS, scoring rubrics, quality standards)
- See `references/PAIN_SEGMENTS_REFERENCE.md` for examples of strong vs weak segments
- See `references/ICP_FRAMEWORK.md` for deeper ICP profiling methodology
- See `examples/overjet/company-research.md` for a complete real-world example
