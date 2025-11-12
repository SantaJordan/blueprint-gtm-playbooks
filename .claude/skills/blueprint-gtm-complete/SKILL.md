---
name: blueprint-gtm-complete
description: Complete end-to-end Blueprint GTM Intelligence System in one execution. Analyzes company, validates pain segments with hard data (EPA, OSHA, FDA, CMS, Mimidata labs), generates buyer-validated messages, and delivers HTML playbook. Single command, full workflow.
---

# Blueprint GTM Complete Analysis

## Purpose

Execute the complete Blueprint GTM Intelligence System pipeline in a single automated workflow:

1. **Stage 1: Company Research** - Analyze target company, identify ICP, define personas, develop pain segment hypotheses
2. **Stage 2: Data Research** - Validate segments with hard government data sources (EPA ECHO, OSHA, FDA, CMS, Mimidata labs)
3. **Stage 3: Message Generation** - Generate and validate PQS/PVP messages using brutal buyer critique (8.5+/10 for TRUE PVPs, 7.0+/10 for Strong PQS)
4. **Stage 4: Explainer Builder** - Create mobile-responsive HTML playbook with all validated messages

**Final Deliverable:** Single HTML file (`blueprint-gtm-playbook-[company].html`) with complete GTM analysis and methodology demonstration.

## Methodology Reference

This skill implements the Blueprint GTM v1.1.0 methodology. For detailed guidance on:
- PVP vs PQS distinction (8.5+ threshold for TRUE PVPs, 7.0-8.4 for Strong PQS)
- Independently Useful Test (complete actionable information requirements)
- Action Extraction & Completeness Check phase
- Data tier framework (Tier 1: Government, Tier 2: Hybrid, Tier 3: Competitive/Velocity)
- Buyer critique rubric and quality standards
- Realistic expectations (TRUE PVPs are rare, Strong PQS is success)

See: `references/methodology.md`

## When to Use This Skill

- User provides a company URL and wants complete Blueprint GTM analysis
- Starting from scratch with new target company
- Need full end-to-end workflow without manual stage transitions
- Ready to invest 30-45 minutes for comprehensive analysis

## Requirements

**Input Required:**
- Company website URL (required)

**Optional Context:**
- Target persona preference (defaults to primary buyer persona discovered)
- Geographic focus (if applicable)
- Industry-specific data source preferences

## Workflow Overview

This skill executes all four Blueprint GTM stages sequentially without pausing. Each stage feeds directly into the next:

```
Company URL Input
    ↓
Stage 1: Company Research (10-15 min)
    → Company context, ICP, persona, 3-5 pain segment hypotheses
    ↓
Stage 2: Data Research (10-15 min)
    → Validate segments with government databases, create data recipes
    ↓
Stage 3: Message Generation (10-15 min)
    → Generate 5-7 variants per segment, brutal critique, keep only 8.0+/10
    ↓
Stage 4: Explainer Builder (5 min)
    → Package into mobile-responsive HTML document
    ↓
Final HTML Playbook Delivered
```

---

# STAGE 1: COMPANY RESEARCH

## Purpose

Analyze the target company to identify Pain-Qualified Segments (PQS) - specific situations where prospects experience measurable pain that the company's solution addresses.

## Phase 1: Live Website Analysis (ALWAYS REQUIRED)

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

## Phase 2: Deep ICP Research

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

## Phase 3: Second-Layer Analysis

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

## Phase 4: Target Persona Research

Identify the specific person within the ICP who experiences the pain.

**Research Strategy:**

1. **Determine Decision-Maker**: Based on the solution type, who would buy this?
   - Enterprise software? CTO, VP Engineering, Director of IT?
   - Compliance tool? Chief Compliance Officer, VP Risk?
   - Sales/Marketing tool? CRO, CMO, VP Sales?
   - Healthcare tool? Chief Medical Officer, Practice Administrator, Clinical Director?

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

## Phase 5: Pain-Qualified Segment Hypothesis

Synthesize everything into 3-5 specific painful situations.

**Critical Principles:**

1. **Specificity over generality**: "Struggling with FedRAMP compliance after failed audit" beats "needs better security"
2. **Timing matters**: The pain must be happening NOW, not theoretically
3. **Data detectability**: Consider how you'd identify companies in this situation
4. **Brand relevance**: The pain must directly connect to what the company solves

**For Each Segment, Document:**

- **Segment Name**: Descriptive title capturing the situation
- **Trigger Event/Situation**: What specific event or condition creates this pain NOW?
- **Core Pain/Challenge**: What friction, inefficiency, risk, or mistake are they experiencing?
- **Why This Matters to [Company]**: How does this pain relate to the company's unique value?
- **Initial Data Hypothesis**: What public data might reveal companies in this situation?

**Output Section 5: Pain-Qualified Segment Hypotheses**

```markdown
## Pain-Qualified Segment Hypotheses

### Segment 1: [Descriptive Name]

**Trigger Event/Situation:**
[What specific, observable event or condition creates this pain? Examples:
- Failed compliance audit requiring remediation
- Rapid headcount growth straining existing systems
- M&A integration creating operational chaos
- Major customer loss revealing operational gaps
- New regulatory requirements with approaching deadlines
- Recent violations requiring corrective action]

**Core Pain/Challenge:**
[What specific friction, inefficiency, risk, or mistake is the prospect experiencing RIGHT NOW?]

**Brand Relevance:**
[Why is this segment highly relevant for [Company Name]? Connect the pain directly to their unique solution/positioning/data advantage.]

**Initial Data Hypothesis:**
[What types of HARD public data might reveal companies in this situation? Focus on:
- Healthcare: CMS data, state licensing boards, CDC databases, OSHA healthcare violations, Mimidata labs datasets
- General regulatory: EPA ECHO, OSHA enforcement, FDA inspections, FMCSA/SAFER
- Compliance databases: State licensing violations, permit applications/denials
- Government enforcement: Specific dates, record numbers, facility details
- Court records, UCC filings, regulatory deadlines
- Operational metrics from government databases

AVOID soft signals like job postings, M&A activity, and generic industry trends - these apply too broadly and aren't specific enough]

---

### Segment 2: [Descriptive Name]
[Same structure]

---

### Segment 3: [Descriptive Name]
[Same structure]

---

[Continue for 3-5 segments total]
```

## Stage 1 Complete Output Format

```markdown
# Blueprint GTM Research Report: [Company Name]

**Date:** [Today's date]
**Analyst:** Claude (Blueprint GTM System)
**Stage:** Company Research (Stage 1 of 4)

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

## Transition to Stage 2

This research provides the foundation for Stage 2: Data Source Research.

**Proceeding automatically to Stage 2...**
```

---

# STAGE 2: DATA RESEARCH

## Purpose

Take pain segment hypotheses from company research and validate whether they're **detectable** using hard public data. Focus on government databases with timestamped violations, permits, enforcement actions, and compliance records - NOT soft signals like job postings or M&A.

## Core Philosophy: Hard Data Only

**What We're Looking For:**
- Government enforcement databases (EPA ECHO, OSHA, FDA, FMCSA/SAFER)
- Healthcare compliance data (CMS, state licensing boards, CDC, Mimidata labs)
- Regulatory compliance records with dates and violation numbers
- Permit applications, license renewals, inspection schedules
- Court records, consent decrees, corrective action plans
- Facility-specific operational data from government sources

**What We Avoid:**
- ❌ Job posting data (too generic, everyone hires)
- ❌ M&A announcements (no specific pain indicated)
- ❌ Funding rounds (thousands qualify, no urgency)
- ❌ Tech stack changes (speculative, unverifiable)
- ❌ Generic industry trends (applies to everyone)

**Why:** Hard data enables specific messaging: "I noticed your facility at 123 Main St received OSHA citation #987654 on March 15, 2025 for..." vs. generic "I see you're hiring compliance people..."

## Phase 1: Review Pain Segment Hypotheses

Start by reviewing the output from Stage 1 company research.

**For Each Segment, Extract:**

1. **Trigger Event/Situation**: What specific event creates the pain?
2. **Target Company Type**: What industries/operations would experience this?
3. **Timing**: When does this pain occur (how recent, how urgent)?
4. **Initial Data Hypothesis**: What data sources were suggested?

**Output Section 1: Segment Summary**

```markdown
## Segment Summary (From Company Research)

### Segment 1: [Name]
- **Trigger**: [Event/situation]
- **Target**: [Industries/company types]
- **Timing**: [When this occurs]
- **Initial hypothesis**: [Proposed data sources]

### Segment 2: [Name]
[Same structure]

[Continue for all segments]
```

## Phase 2: Hard Data Source Discovery (MANDATORY WEB SEARCH)

For each segment, **actively search the web** to discover what specific government databases exist that could reveal companies in that situation.

**YOU MUST USE WEB SEARCH - DO NOT RELY ON INTERNAL KNOWLEDGE**

**Research Strategy:**

### Step 1: Identify Regulatory Context

Based on the segment's industry and pain type, determine what agencies likely regulate them.

**Search Queries to Execute:**

```
"[ICP Industry] regulatory agencies"
"[ICP Industry] compliance requirements"
"[ICP Industry] government databases"
"[Specific pain type] enforcement data"
"[Industry] violation records public database"

Healthcare-specific:
"[Healthcare specialty] CMS data"
"[Healthcare specialty] state licensing board violations"
"healthcare facility inspection database"
"mimidata labs healthcare datasets"
"CDC [specific health area] database"
```

### Step 2: Search for Specific Government Databases

For each potentially relevant agency discovered, search for their public data portals.

**Search Queries to Execute:**

```
"[Agency name] public data"
"[Agency name] enforcement database"
"[Agency name] violation search"
"[Agency name] API documentation"
"[Agency name] bulk data download"
"[Agency name] inspection records"

Healthcare-specific:
"CMS provider data download"
"state medical board disciplinary actions"
"mimidata labs database catalog"
"CDC WONDER database"
"OSHA healthcare violations"
```

### Step 3: Verify Database Access and Capabilities

**ACTUALLY VISIT THE DATABASE URLs YOU FIND**

Don't just confirm a database exists - open it and explore:

1. **Navigate to the search portal**
   - Can you actually perform searches?
   - What search filters are available?
   - Try a sample query

2. **Check for API documentation**
   - Search: "[database name] API"
   - Search: "[database name] developer documentation"
   - Look for terms like "REST API", "JSON", "XML", "SOAP"

3. **Look for bulk data access**
   - Search: "[database name] bulk download"
   - Search: "[database name] data export"
   - Check for FTP, CSV downloads, data.gov listings
   - Check Mimidata labs catalog for pre-processed healthcare data

4. **Document what you ACTUALLY find**
   - Don't assume - verify by visiting the site
   - Take note of exact URLs
   - Screenshot or note field names if visible

**Critical Questions to Answer Through Active Research:**

1. **What's the exact database name and URL?**
2. **What level of detail does it provide?** (facility-specific, company-wide, dates, violation types)
3. **How is it accessible?** (web portal, API, bulk download, Mimidata labs)
4. **How often is it updated?**
5. **What's the data quality?**
6. **What specific fields are available?** (THIS IS CRITICAL - document ACTUAL field names)

### Step 4: Document Field-Level Details

For each promising data source discovered through your web research, create detailed documentation.

**Required Documentation:**

```markdown
### Data Source: [Database Name]

**Discovery Method:** [How you found this - web search queries used]

**Source Type:** Government enforcement database / Permit system / Licensing database / Healthcare compliance

**Agency:** [Specific agency/department - confirmed via web search]

**Access URL:** [Direct link to search portal or API docs - VERIFIED BY VISITING]

**Update Frequency:** [How often data refreshes - found on site or via search]

**Geographic Coverage:** [National / State-specific / Local - confirmed via site]

**Historical Data:** [How far back records go - verified by checking database]

**Access Method (check all that you CONFIRMED exist):**
- [ ] Web portal with search (tested and working)
- [ ] Public API (link to docs: _____)
- [ ] Bulk download available (link: _____)
- [ ] Mimidata labs dataset (catalog link: _____)
- [ ] Apify actor available (link: _____)
- [ ] RapidAPI listing (link: _____)
- [ ] Data.gov dataset (link: _____)
- [ ] FOIA request required
- [ ] Paid access required ($____ pricing found at: _____)

**Key Data Fields Available:**
[List ACTUAL field names found by visiting database/API docs]

Example format:
- `violation_date` (format: MM/DD/YYYY - confirmed in sample results)
- `violation_type` (values seen: "Serious", "Willful", "Repeat", "Other")
- `facility_name` (string, confirmed in search results)
- `facility_address` (separate fields: street, city, state, zip)
- `naics_code` (6-digit industry code)
- `penalty_amount` (dollar amount, some records show $0)

**Filtering Capabilities:**
[Document ACTUAL filters available in the search interface - verified by using it]

**Data Quality Assessment (based on sample queries run):**
- Completeness: [High/Medium/Low]
- Accuracy: [High/Medium/Low]
- Timeliness: [Most recent record date found: ___]
- Consistency: [Formats consistent across records?]
```

## Phase 3: Build Pain Data Recipes

For each segment, create a specific "recipe" - the combination of data signals that identify companies experiencing that pain.

**Pain Data Recipe Structure:**

```markdown
## Segment [#]: [Name]

### Data Recipe (How to Identify Companies in This Situation)

**Primary Data Signal:**
- **Source**: [Database name]
- **Filter**: [Specific query/filter criteria]
- **Field**: [Exact field name(s) to check]
- **Threshold**: [What value/pattern indicates pain]
- **Timing**: [How recent must data be?]

**Example Query:**
[Pseudo-code or actual query showing how to find companies]

```
Example:
OSHA Establishment Search
WHERE violation_type = "serious" OR "willful"
AND violation_date > DATE_SUB(CURRENT_DATE, 180) -- last 6 months
AND facility_state = "CA" -- if targeting specific geography
AND naics_code IN (3231, 3232, 3233) -- specific industries
```

**Secondary Data Signal (Optional):**
[If combining multiple sources strengthens targeting]

**Combined Logic:**
[How signals combine to indicate pain]

**Expected Volume:**
[Rough estimate of how many companies would match]

**Data Confidence:**
- Signal strength: [Strong/Medium/Weak]
- False positive risk: [High/Medium/Low]
- Data availability: [Consistent/Intermittent/Limited]
```

## Phase 4: Assess Segment Feasibility

Rate each segment's detectability.

**Feasibility Criteria:**

| Rating | Criteria |
|--------|----------|
| **HIGH** | Specific government database exists, field-level detail confirmed, updated regularly, free/low-cost access, can filter by date/location/severity |
| **MEDIUM** | Data source exists but has limitations (partial coverage, infrequent updates, requires paid access, limited filtering) |
| **LOW** | Data exists but impractical (FOIA required, inconsistent formatting, no API, expensive, very limited fields) |
| **UNDETECTABLE** | No public data source found that reliably indicates this situation |

**For Each Segment:**

```markdown
### Segment [#]: [Name]

**FEASIBILITY: [HIGH / MEDIUM / LOW / UNDETECTABLE]**

**Rationale:**
[Explain why this rating - cite specific data source strengths/weaknesses]

**If HIGH/MEDIUM:**
- Primary data source: [Name with link]
- Key fields: [List critical fields]
- Update frequency: [How current]
- Estimated addressable companies: [Rough count if knowable]

**If LOW/UNDETECTABLE:**
- **Data limitations**: [What's missing or impractical]
- **Alternative approaches considered**: [What else was researched]
- **Suggested pivot**: [Recommend different segment or targeting approach]

**Next Steps for This Segment:**
[If HIGH: "Ready for message generation" / If MEDIUM: "Proceed with data quality caveats" / If LOW/UNDETECTABLE: "Pivot to alternative segment"]
```

## Stage 2 Complete Output Format

```markdown
# Blueprint GTM Data Source Research: [Company Name]

**Date:** [Today's date]
**Analyst:** Claude (Blueprint GTM System)
**Stage:** Data Source Research (Stage 2 of 4)

---

## Executive Summary

**Segments Analyzed:** [Number]
**Feasibility Breakdown:**
- HIGH feasibility: [Count] segments
- MEDIUM feasibility: [Count] segments
- LOW feasibility: [Count] segments
- UNDETECTABLE: [Count] segments

**Recommendation:**
[Quick statement: "Proceed with [X] segments" / "Pivot to alternative segments recommended below"]

---

## Segment Summary (From Company Research)
[Section from Phase 1]

---

## Data Source Research

### Segment 1: [Name]

**FEASIBILITY: [Rating]**

[Complete documentation from Phases 2-4:
- Data source details
- Pain data recipe
- Feasibility rationale
- Next steps]

---

### Segment 2: [Name]
[Same structure]

---

[Continue for all segments]

---

## Data Source Catalog

[Comprehensive list of all databases researched]

---

## Transition to Stage 3

**Recommended Segments for Stage 3 (Message Generation):**
1. [Segment name] - HIGH feasibility
2. [Segment name] - HIGH or MEDIUM feasibility
3. [Alternative segment if needed]

**Proceeding automatically to Stage 3 with HIGH feasibility segments...**
```

---

# STAGE 3: MESSAGE GENERATION

## Purpose

Transform validated pain segments and hard data sources into Texada-level outreach messages that earn replies. Generate multiple message variants, brutally critique them as the buyer, auto-revise failures, and output only messages that pass the "Would I reply?" test.

## Core Philosophy

**You are not a copywriter. You are the buyer.**

Your job is to inhabit the target persona completely, generate messages using hard data principles, and answer the only question that matters: **"Would I reply to this?"**

If the answer is "maybe" or "no," you don't flag it for revision—you DESTROY it and rebuild it until it's Texada-level or you admit it can't work.

## Phase 1: Context Extraction & Persona Inhabitation

**Step 1.1: Extract the Target Persona**

From Stage 1 company research, identify:
- Job title (specific, not "decision maker")
- Responsibilities (what they own day-to-day)
- Pain points (what keeps them up at night)
- Expertise level (what they already know - this is CRITICAL)

**Step 1.2: Extract HIGH Feasibility Pain Segments**

From Stage 2 data source research, list ONLY segments rated HIGH feasibility:
- The specific situation/trigger (documented in government database)
- The pain/challenge it creates
- Why it matters to the persona

**If no HIGH feasibility segments exist, STOP and recommend returning to research phases.**

**Step 1.3: Map Data Sources to Segments**

From Stage 2 data source research, for each HIGH segment identify:
- Which specific government database detects this (EPA ECHO, OSHA, FDA, CMS, Mimidata labs, etc.)
- What ACTUAL field names exist (from verified documentation)
- What's provable vs what's inferred
- Example record numbers, violation types, date formats

**Step 1.4: Formally Adopt Buyer Persona**

Write this statement and embody it for the rest of the process:

> "I am now [Job Title] at [Company Type]. My responsibilities include [X, Y, Z]. My biggest pain is [Pain]. I am an expert in [Domain] which means I already know [Common Knowledge]. I receive 50+ sales emails per day, most of which I delete in 2 seconds. For the rest of this skill, I will evaluate every message as THIS person, not as a marketer or copywriter. I will be brutally honest about what would make me reply vs delete."

## Phase 2: Generate Message Variants

**For each HIGH feasibility pain segment, generate TWO message types:**

### Type 1: PQS (Pain-Qualified Segment)

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
- ✅ "CMS citation Q3 2024"
- ✅ "Permit expires in 90"
- ❌ "Important compliance information"

**Intro Principles (CRITICAL - This is Where Data Matters):**
- Reference the EXACT government database
- Use ACTUAL record numbers, violation IDs, dates
- Use facility-specific addresses or identifiers
- Format dates exactly as they appear in database
- Include severity classifications if available
- ✅ "Your facility at 1234 Industrial Pkwy received OSHA citation #987654321 on March 15, 2025 for three serious violations (CFR 1910.147, 1910.212, 1910.305)"
- ✅ "CMS.gov shows your facility (Provider ID: 445678) with 3-star quality rating dropped to 2-star on Q3 2024 review"
- ❌ "It looks like you might have some compliance issues"

**Insight Principles:**
- Connect the data to a consequence they might not see
- Reference patterns from similar companies
- Non-obvious synthesis, not obvious advice
- ✅ "Most facilities don't catch this pattern until inspectors return - second violations within 12 months trigger mandatory willful citations with 10x penalties"
- ❌ "This could be a problem for your company"

**Inquisition Principles:**
- "Did I get it right?" style question
- Low effort to answer (yes/no, confirm number)
- NO meeting requests
- NO solution pitches
- ✅ "Did I get the violation count right?"
- ❌ "Would you like to schedule a demo?"

**Total Length:** Under 75 words

### Type 2: PVP (Permissionless Value Proposition)

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
- ✅ "I pulled the CMS survey deadlines for all 3 of your facilities - you have 4 deadlines between now and Q2 2026, with the first one (infection control follow-up) due May 15, 2025"
- ❌ "I have valuable compliance insights to share"

**Insight Principles - Why It Matters:**
- Connect value to their specific situation using data
- Show you understand their constraints/priorities
- Reference specific numbers if available
- ✅ "The May deadline matters because it triggers the quarterly reporting requirement - if you miss it, you're automatically escalated to state enforcement"
- ❌ "Deadlines are important to track"

**Inquisition Principles - Facilitate Forwarding:**
- Make it easy to forward internally
- Don't ask for anything in return
- Focus on logistics, not commitment
- ✅ "Who's best to send the deadline calendar to?"
- ❌ "Can we schedule a call to discuss?"

**Total Length:** Under 100 words

## Phase 3: Buyer Role-Play Critique (BRUTAL HONESTY REQUIRED)

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

TEXADA TEST (The Gold Standard):
- Hyper-specific? [YES/NO + evidence]
- Factually grounded? [YES/NO + evidence]
- Non-obvious synthesis? [YES/NO + evidence]

DATA SOURCE VERIFICATION (CRITICAL):
For EACH claim in the message, verify against Stage 2 data source research:

- Intro claim: "[Exact claim from message]"
  → Database: [Name, e.g., "EPA ECHO"]
  → Field: [Actual field name, e.g., "VIOLATION_DATE"]
  → Status: [✅ Provable / ⚠️ Inferred / ❌ Not Possible]

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

## Phase 4: Auto-Revision Engine (Maximum 2 Attempts)

**For every message with verdict "REVISE", immediately rebuild it.**

**Revision Process:**
1. Identify the primary failure mode (from critique)
2. Check if it's fixable with data you have (from Stage 2)
3. If YES → Rewrite addressing the failure, using MORE specific data
4. If NO → Change verdict to DESTROY and explain why data doesn't support this angle
5. Re-critique the revision using same framework
6. If still scores < 8.0 after 2 revisions → DESTROY

**Common Failure Modes & Fixes:**

| Failure Mode | Fix Strategy | Example |
|--------------|--------------|---------|
| Too vague | Add specific record numbers, dates, facility addresses | "violations" → "OSHA citation #987654321 on March 15, 2025" |
| Data not credible | Add exact database name, record ID, field format | "I noticed" → "CMS data shows provider ID 445678" |
| Obvious insight | Research deeper consequences or patterns | "You should fix this" → "Second violations trigger 10x penalties" |
| Too long | Cut fluff, keep only data + insight + question | Remove pleasantries, company descriptions |
| Asks for meeting | Change to low-effort question | "Can we talk?" → "Did I get the count right?" |

## Phase 5: Select Top Messages

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

## Phase 6: Create Implementation Blueprint

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
- Based on: [Database update frequency from Stage 2]

### Targeting Criteria
Who gets this message:
- Industry: [Specific NAICS codes if applicable]
- Geography: [States, regions, or nationwide]
- Trigger: [Specific data condition that qualifies them]
- Exclusions: [Who NOT to send to]

**Expected Volume:** [Estimate based on Stage 2]

### Execution Notes
- Best send time: [Based on urgency]
- Follow-up: [If no reply, appropriate timeline]
- Reply handling: [Common responses to expect]
```

## Stage 3 Complete Output Format

```markdown
# Blueprint GTM Message Generation Report: [Company Name]

**Date:** [Today's date]
**Analyst:** Claude (Blueprint GTM System)
**Stage:** Message Generation (Stage 3 of 4)

---

## Executive Summary

**Segments Processed:** [Number of HIGH feasibility segments]
**Messages Generated:** [Total variants created]
**Messages Validated:** [Number scoring ≥ 8.0/10]
**Final Selection:** [Number of messages recommended]

**Quality Assessment:**
- Average buyer score: X.X/10
- Data verification: [% of claims fully provable]
- Texada Test pass rate: [X of Y messages]

---

## Persona Context

[Persona statement from Phase 1.4]

---

## Segment 1: [Name]

### Selected Message 1: [Type - PQS/PVP] - [Title]

**Final Message:**
```
[Complete message text]
```

**Buyer Critique Summary:**
- Overall Score: X.X/10
- [Why this message won]

**Data Verification:**
[Claims verified against government database fields]

**Implementation Blueprint:**
[Complete blueprint]

---

### Selected Message 2: [Type]
[Same structure]

---

## Segment 2: [Name]
[Same structure]

---

## Transition to Stage 4

**Messages ready for explainer document:**
- [X] PQS messages validated
- [X] PVP messages validated
- All scoring 8.0+/10
- All data fully provable

**Proceeding automatically to Stage 4 (Explainer Builder)...**
```

---

# STAGE 4: EXPLAINER BUILDER

## Purpose

Transform validated PQS/PVP messages into a beautiful, mobile-responsive HTML document that explains the Blueprint GTM methodology through company-specific examples. Shows the "old way" (generic pitches) vs "new way" (data-driven intelligence).

## Phase 1: Extract Content Components

Gather all necessary content from previous stages:

**From Stage 1 (Company Research):**
- Company name
- Core offering
- Target ICP industries
- Target persona job title

**From Stage 3 (Message Generation):**
- 3 best PQS messages with buyer scores
- 3 best PVP messages with buyer scores
- Data sources used
- Why each message works

**Content You'll Create:**
- "Old Way" example (generic SDR email)
- Jordan's bio section
- Transformation narrative

## Phase 2: Create "Old Way" Example

Write a typical bad SDR email that the company's team might send today.

**Bad Email Template:**

```
Subject: Quick question about [their process area]

Hi [Persona Name],

I noticed [generic observation from LinkedIn/website/news].

I'm reaching out because [Company Name] helps companies like yours [vague benefit claim]. Our [technology type] has helped [big name customers] [achieve generic outcome].

[Insert feature list or ROI claim]

Do you have 15 minutes next week to discuss how we could help [Prospect Company] achieve similar results?

Best,
[SDR Name]
[Company Name]
```

## Phase 3: Build HTML Document

Use the Blueprint brand HTML template with inline CSS.

**CRITICAL REQUIREMENTS:**
- All CSS must be inline (in `<style>` tag)
- No external dependencies
- Mobile-responsive
- Blueprint brand colors
- Under 2MB file size

**HTML Template Structure:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blueprint GTM Playbook for [COMPANY_NAME]</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --print-blue: #5611A6;
            --dark-print: #280A4A;
            --light-print: #D6B2FF;
            --corn: #FFF277;
            --ice: #F5F8FF;
            --white: #FFFFFF;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.7;
            color: var(--dark-print);
            background: var(--ice);
            font-size: 16px;
        }

        .container {
            max-width: 100%;
            margin: 0 auto;
            padding: 1rem;
        }

        h1 {
            font-size: 2rem;
            font-weight: 700;
            color: var(--dark-print);
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid var(--light-print);
        }

        h2 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--dark-print);
            margin: 2.5rem 0 1rem;
            padding-left: 1rem;
            position: relative;
        }

        h2::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: var(--print-blue);
        }

        h3 {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--dark-print);
            margin-bottom: 0.5rem;
        }

        p {
            font-size: 1rem;
            color: rgba(40, 10, 74, 0.9);
            margin-bottom: 1rem;
            line-height: 1.7;
        }

        .section {
            background: var(--white);
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 8px rgba(86, 17, 166, 0.08);
            margin-bottom: 2rem;
        }

        .highlight-box {
            background: var(--corn);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        }

        .old-way-example {
            background: #FFF8DC;
            border: 2px solid #F0E68C;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }

        .message-example {
            background: var(--ice);
            padding: 1rem;
            border-radius: 0.5rem;
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
            line-height: 1.6;
            white-space: pre-wrap;
            overflow-x: auto;
            margin: 0.5rem 0;
        }

        .play-card {
            background: var(--white);
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(86, 17, 166, 0.08);
            border: 1px solid var(--light-print);
        }

        .play-type {
            display: inline-block;
            background: var(--print-blue);
            color: var(--white);
            padding: 0.25rem 0.75rem;
            border-radius: 2rem;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }

        .play-type.pvp {
            background: var(--dark-print);
        }

        .play-explanation {
            background: var(--ice);
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }

        .data-sources {
            background: var(--corn);
            padding: 0.75rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            font-size: 0.875rem;
        }

        .why-section {
            font-size: 0.875rem;
            color: rgba(40, 10, 74, 0.8);
            margin-bottom: 1rem;
        }

        @media (min-width: 768px) {
            .container {
                max-width: 900px;
                padding: 2rem;
            }

            h1 {
                font-size: 2.5rem;
            }

            h2 {
                font-size: 1.75rem;
            }

            .section, .play-card {
                padding: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">

        <!-- SECTION 1: Title & Jordan's Bio -->
        <div class="section">
            <h1>Blueprint GTM Playbook for [COMPANY_NAME]</h1>

            <h2>Who the Hell is Jordan Crawford?</h2>

            <p>Founder of Blueprint GTM. Built a business by scraping 25M+ job posts to find company pain points. Believes the Predictable Revenue model is dead. Thinks mounting an AI SDR on outdated methodology is like putting a legless robot on a horse—no one gets anywhere, and it still shits along the way.</p>

            <p>The core philosophy is simple: The message isn't the problem. The LIST is the message. When you know exactly who to target and why they need you right now, the message writes itself.</p>
        </div>

        <!-- SECTION 2: The Old Way -->
        <div class="section">
            <h2>The Old Way (What Everyone Does)</h2>

            <p>Let's be brutally honest about what your GTM team is doing right now. They're buying lists from ZoomInfo, adding some "personalization" like mentioning a LinkedIn post, then blasting generic messages about features. Here's what it actually looks like:</p>

            <div class="old-way-example">
                <p><strong>The Typical [COMPANY_NAME] SDR Email:</strong></p>
                <div class="message-example">[INSERT BAD EMAIL]</div>
            </div>

            <p><strong>Why this fails:</strong> The prospect is an expert. They've seen this template 1,000 times. There's zero indication you actually understand their specific situation. It's interruption disguised as personalization. Delete.</p>
        </div>

        <!-- SECTION 3: The New Way -->
        <div class="section">
            <h2>The New Way: Intelligence-Driven GTM</h2>

            <p>Blueprint GTM flips the entire approach. Instead of interrupting prospects with pitches, you deliver insights so valuable they'd pay consulting fees to receive them. You become the person who helps them see around corners, not another vendor in their inbox.</p>

            <p>This requires two fundamental shifts:</p>

            <div class="highlight-box">
                <h3>1. Hard Data Over Soft Signals</h3>
                <p><strong>Stop:</strong> "I see you're hiring compliance people" (job postings - everyone sees this)</p>
                <p><strong>Start:</strong> "Your facility at 1234 Industrial Pkwy received EPA violation #2024-XYZ on March 15th" (government database with record number)</p>
            </div>

            <div class="highlight-box">
                <h3>2. Mirror Situations, Don't Pitch Solutions</h3>
                <p><strong>PQS (Pain-Qualified Segment):</strong> Reflect their exact situation with such specificity they think "how did you know?" Use government data with dates, record numbers, facility addresses.</p>
                <p><strong>PVP (Permissionless Value Proposition):</strong> Deliver immediate value they can use today - analysis already done, deadlines already pulled, patterns already identified - whether they buy or not.</p>
            </div>
        </div>

        <!-- SECTION 4: PQS Examples -->
        <div class="section">
            <h2>[COMPANY_NAME] PQS Plays: Mirroring Exact Situations</h2>

            <p>These messages demonstrate such precise understanding of the prospect's current situation that they feel genuinely seen. Every claim traces to a specific government database with verifiable record numbers.</p>

            <!-- PQS Play Cards will be inserted here -->
        </div>

        <!-- SECTION 5: PVP Examples -->
        <div class="section">
            <h2>[COMPANY_NAME] PVP Plays: Delivering Immediate Value</h2>

            <p>These messages provide actionable intelligence before asking for anything. The prospect can use this value today whether they respond or not. That's the power of permissionless value.</p>

            <!-- PVP Play Cards will be inserted here -->
        </div>

        <!-- SECTION 6: The Transformation -->
        <div class="section">
            <h2>The Transformation</h2>

            <p>Notice the difference? Traditional outreach talks about YOUR product and YOUR benefits. Blueprint GTM talks about THEIR situation and THEIR challenges using verifiable data they can look up themselves.</p>

            <div class="highlight-box">
                <p><strong>The shift is simple but profound:</strong></p>
                <p>Stop sending messages about what you do. Start sending intelligence about what they need to know right now. When you lead with EPA violation #2024-XYZ on March 15th instead of "I see you're hiring," you're not another sales email - you're the person who actually did the research.</p>
            </div>

            <p>This isn't about templates or tactics. It's about building a systematic way to identify prospects experiencing specific, urgent challenges where [COMPANY_NAME]'s solutions provide unique value - and proving you've done the homework with government database record numbers.</p>

            <p>The companies that master this approach don't compete on features. They compete on intelligence.</p>
        </div>

    </div>
</body>
</html>
```

## Phase 4: Populate the Template

Fill in all placeholders with actual content from previous stages:

1. Replace **[COMPANY_NAME]** throughout
2. Insert bad email example created in Phase 2
3. Create play cards for each selected PQS message
4. Create play cards for each selected PVP message
5. Ensure no line breaks within sentences in messages

**Play Card Format:**

```html
<div class="play-card">
    <span class="play-type">PQS</span>
    <h3>Play 1: [Descriptive Title]</h3>

    <div class="play-explanation">
        <p><strong>What's the play?</strong> [Targeting strategy and pain point]</p>
    </div>

    <div class="why-section">
        <p><strong>Why this works:</strong> [Business impact explanation]</p>
    </div>

    <div class="data-sources">
        <strong>Data source:</strong> [Database name]
    </div>

    <p><strong>The message:</strong></p>
    <div class="message-example">[Full message text - no line breaks within sentences]</div>
</div>
```

## Stage 4 Complete Output

**Deliverable:**

Single HTML file named: `blueprint-gtm-playbook-[company-name].html`

**Final Confirmation Message:**

```markdown
# Blueprint GTM Complete Analysis: [Company Name]

**Date:** [Today's date]
**Total Processing Time:** [Estimate: 30-45 minutes]
**Status:** ✅ COMPLETE

---

## Final Deliverable

📄 **File:** `blueprint-gtm-playbook-[company-name].html`

**Contents:**
- Jordan's bio and Blueprint philosophy
- Old Way vs New Way comparison
- [X] PQS play cards with validated messages (8.0+/10 buyer scores)
- [X] PVP play cards with validated messages (8.0+/10 buyer scores)
- Data sources documented for each message
- Full transformation narrative

**File Specifications:**
- Mobile-responsive (works on all devices)
- Inline CSS (no external dependencies)
- Under 2MB
- Ready to share/email/host

---

## Summary Statistics

**Stage 1 - Company Research:**
- ICP: [Industries]
- Persona: [Job title]
- Segments developed: [X]

**Stage 2 - Data Research:**
- HIGH feasibility segments: [X]
- Data sources identified: [List databases]
- Feasibility rating: [X% HIGH/MEDIUM]

**Stage 3 - Message Generation:**
- Messages generated: [Total variants]
- Messages validated (8.0+): [X]
- Average buyer score: [X.X/10]
- Data verification: [100% provable]

**Stage 4 - Explainer Built:**
- Play cards created: [X] PQS + [X] PVP
- HTML file generated: ✅
- Quality checked: ✅

---

## Blueprint GTM Analysis Complete

The complete playbook is ready for [Company Name]'s review. This document demonstrates the transformation from generic outreach to data-driven intelligence using their specific market, validated with hard government data sources.

**Next Steps:**
- Review HTML file
- Share with stakeholders
- Begin implementation using data recipes and targeting criteria provided
```

---

# COMPLETE WORKFLOW SUMMARY

## Execution Flow

When this skill is invoked with a company URL, it automatically executes:

1. **Stage 1 (10-15 min)**: Visit website → Research ICP → Define persona → Develop 3-5 pain segment hypotheses
2. **Stage 2 (10-15 min)**: Search for government databases → Verify field-level data → Create pain data recipes → Rate feasibility
3. **Stage 3 (10-15 min)**: Generate 5-7 message variants per segment → Brutal buyer critique → Keep only 8.0+/10 → Document implementation blueprints
4. **Stage 4 (5 min)**: Create bad email example → Populate HTML template → Generate final playbook file

**Total Time:** 30-45 minutes
**Output:** Single HTML file with complete Blueprint GTM analysis

## Quality Standards

Every stage maintains Blueprint GTM core principles:

- **Hard data only**: Government databases with record numbers, not soft signals
- **Buyer-centric**: Everything evaluated from buyer perspective, not marketer
- **Texada-level specificity**: Hyper-specific, factually grounded, non-obvious synthesis
- **Provable claims**: Every data claim verified against actual database fields
- **High bar for quality**: Only 8.0+/10 messages make it to final deliverable

## Integration Note

This skill consolidates all four Blueprint skills into one automated execution. No manual handoffs between stages required. Just provide a company URL and receive complete HTML playbook.

---

## Common Pitfalls to Avoid Across All Stages

1. **Relying on cached knowledge**: Always web search for current data sources
2. **Accepting soft signals**: Job postings, M&A, funding ≠ pain segments
3. **Being too nice in critique**: Delete-level honesty required in Stage 3
4. **Assuming data exists**: Only document fields you've actually verified
5. **Generic insights**: Buyer already knows obvious stuff - dig deeper
6. **Line breaks in HTML messages**: Let text wrap naturally
7. **Skipping field-level documentation**: Must have actual field names from databases
8. **Creating undetectable segments**: Pivot early if no hard data exists

## Healthcare-Specific Guidance

When analyzing healthcare companies (like Constant Therapy Health targeting clinicians):

**Stage 1 - Company Research:**
- Focus on clinician personas (SLPs, OTs, PTs, neurologists)
- Research healthcare-specific pains (documentation burden, compliance, outcome tracking)
- Consider second-layer: patient outcomes, insurance requirements, regulatory burden

**Stage 2 - Data Research:**
- Prioritize healthcare data sources:
  - CMS provider data (quality ratings, survey results)
  - State licensing boards (disciplinary actions, license status)
  - CDC databases (disease surveillance, health statistics)
  - OSHA healthcare violations (patient handling, infectious disease)
  - Mimidata labs (pre-processed healthcare datasets)
- Search for state-specific healthcare databases
- Check facility-level data (nursing home compare, hospital compare)

**Stage 3 - Message Generation:**
- Clinician persona expertise: They know clinical guidelines already
- Non-obvious insights: Connect data to practice-level business impact
- Value delivery: Pre-pulled compliance deadlines, quality metric analysis
- Low-effort asks: "Is this still your current facility count?"

**Stage 4 - Explainer Builder:**
- Old Way example: Generic "improve patient outcomes" pitch
- New Way: "CMS shows your facility dropped from 4-star to 3-star on Q3 2024 review"
- Emphasize patient safety and quality metrics in "why this works"

---

## References

- See individual skill files for detailed examples and reference materials
- `blueprint-company-research/SKILL.md` - Company research methodology
- `blueprint-data-research/SKILL.md` - Data source discovery and validation
- `blueprint-message-generation/SKILL.md` - Message generation and buyer critique framework
- `blueprint-explainer-builder/SKILL.md` - HTML template and design system

---

**End of blueprint-gtm-complete skill**

This consolidated skill provides the complete Blueprint GTM Intelligence System in a single automated execution. Perfect for comprehensive company analysis without manual stage management.
