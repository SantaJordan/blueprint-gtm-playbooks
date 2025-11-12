# Blueprint GTM Methodology - Core Prompts & Standards

This file contains reusable prompts, rubrics, and standards for the Blueprint Turbo execution to ensure consistency and quality.

---

## Buyer Critique Rubric

### Formal Persona Adoption

Before critiquing any message, FORMALLY ADOPT the buyer persona:

```
I am now [Job Title from persona research]. I work at [typical ICP company type].

My responsibilities include: [list from persona research]
My KPIs are: [list from persona research]
My daily challenges: [list from persona research]

I receive 50+ sales emails per day. I delete 95% of them without reading past the subject line. Of the 5% I open, I respond to maybe 1%.

I only respond to emails that:
1. Mirror an EXACT situation I'm experiencing RIGHT NOW with specific details
2. Contain data I can independently verify and don't already have access to
3. Offer a non-obvious insight I haven't already considered
4. Require minimal cognitive effort to reply to

I am NOT a marketer or SDR evaluating this message. I AM THE BUYER. Would I actually reply to this?

If my answer is "maybe" — that's a NO.
```

---

### 5 Criteria Scoring (0-10 Each)

For EACH message, score on these 5 criteria:

**1. Situation Recognition (0-10)**
- **10:** Hyper-specific to my exact current situation with dates, record numbers, facility addresses
- **7-9:** Specific to my industry/role but not my exact situation
- **4-6:** Relevant to my general challenges but generic
- **1-3:** Vaguely related to my space
- **0:** Completely irrelevant or generic

**Example 10/10:** "Your facility at 1234 Industrial Parkway received EPA violation #987654321 on March 15, 2025 for three Clean Water Act exceedances"

**Example 3/10:** "I noticed your company works in manufacturing and might have compliance challenges"

---

**2. Data Credibility (0-10)**
- **10:** Every claim traces to a specific government database field with record numbers I can verify
- **7-9:** Credible data source mentioned but not all claims have record numbers
- **4-6:** Data mentioned but no way to verify (e.g., "industry research shows...")
- **1-3:** Claims made without any data backing
- **0:** Contains assumptions or inferences presented as fact

**Example 10/10:** "CMS Geographic Variation Public Use File shows your county at 18.4 post-acute visits per 1,000 Medicare beneficiaries (2022 data, field: VISITS_PER_1000_BENES)"

**Example 2/10:** "I've noticed your market has below-average utilization rates"

---

**3. Insight Value (0-10)**
- **10:** Reveals a non-obvious pattern or deadline I genuinely don't know and should care about
- **7-9:** Interesting synthesis but I could have found this myself with effort
- **4-6:** Mildly useful but not revelatory
- **1-3:** States the obvious (things I already know)
- **0:** No insight, just description

**Example 10/10:** "The consent decree milestones for all 3 of your facilities show 6 deadlines clustered between now and Q2 2026 - you're managing 3 simultaneous remediation timelines with overlapping external audits"

**Example 1/10:** "Environmental compliance can be challenging for manufacturers"

---

**4. Effort to Reply (0-10)**
- **10:** Can reply with a single word or simple yes/no question
- **7-9:** Easy one-sentence reply
- **4-6:** Requires brief explanation
- **1-3:** Needs significant thought/research to respond
- **0:** Impossible to reply without extensive work or meeting request

**Example 10/10:** "Should this analysis go to you or your market analytics lead?"

**Example 0/10:** "Would you have 30 minutes next Tuesday to discuss your environmental compliance strategy?"

---

**5. Emotional Resonance (0-10)**
- **10:** Creates immediate urgency or "how did they know that?" moment
- **7-9:** Sparks genuine curiosity
- **4-6:** Mildly interesting
- **1-3:** Meh, generic
- **0:** Annoying or tone-deaf

**Example 10/10:** "89 days until your June 30 consent decree deadline" (when I'm behind schedule)

**Example 0/10:** "I see you recently posted on LinkedIn about growth" (generic stalking)

---

### Texada Test (Pass/Fail on All 3)

After scoring, apply the Texada Test. ALL THREE must pass:

**✅ Hyper-Specific**
- Contains dates, record numbers, facility addresses, specific field values
- Not: "recent," "many," "several," "some"
- Yes: "March 15, 2025," "#987654321," "1234 Industrial Parkway," "18.4 visits per 1,000"

**✅ Factually Grounded**
- Every claim traces to a specific database field documented in Wave 2
- Can answer: "Which field name from which database proves this?"
- No assumptions, inferences, or "likely" statements

**✅ Non-Obvious Synthesis**
- Insight the persona doesn't already have access to
- Not: "You received a violation" (they know)
- Yes: "Your consent decree has 6 clustered deadlines in next 120 days" (synthesis they didn't do)

---

### Final Verdict & Classification

**Message Type Classification:**

**PVP (Permissionless Value Prop) Requirements:**
- Average score: **8.5+/10** (raised threshold)
- Passes all 3 Texada criteria
- **CRITICAL:** Passes "Independently Useful Test" - recipient can take action WITHOUT replying
- Contains complete actionable information (names, contacts, prices, dates)
- No promises of future value - delivers everything NOW

**PQS (Pain Qualified Segment) Acceptable Range:**
- Average score: **7.0-8.4/10**
- Passes all 3 Texada criteria
- Identifies specific pain with data
- May seek confirmation or provide partial information
- Does NOT need to pass "Independently Useful Test"

**Action Decisions:**

**KEEP AS PVP (Average ≥8.5 AND passes Independently Useful Test)**
- Message is a true PVP
- Document the complete action recipient can take
- Verify all contact info/prices/names are included

**RECLASSIFY AS PQS (Average 7.0-8.4 OR lacks complete action info)**
- Message is actually a strong PQS, not a PVP
- This is NOT a failure - PQS messages are valuable!
- Document as PQS in final output
- Strong pain identification, seeks engagement

**REVISE (Average 6.0-6.9 OR fails 1-2 Texada criteria)**
- Generate ONE revised version addressing specific weaknesses
- Re-critique with same rubric
- Can become either PQS (7.0-8.4) or PVP (8.5+) after revision
- If revised version still <7.0 or fails Texada → DESTROY

**DESTROY (Average <6.0 OR fails all 3 Texada criteria OR contains soft signals)**
- Message is eliminated
- Document why it failed (for learning)
- Do not waste time revising

**Important Notes:**
- Most messages that score 7.0-8.4 are EXCELLENT PQS messages - don't force them to be PVPs
- True PVPs are RARE and require specific data (contacts, prices, names)
- A strong PQS (8.0/10) is better than a fake PVP (8.2/10 but no action available)
- Be honest about classification - shooting for PVP and landing on strong PQS is success

---

## PQS Message Format

### Structure

```
Subject: [2-4 words - ultra-specific trigger]

[Intro: Mirror exact situation with government data]
[Record number, date, facility name/address, specific violation type/field value]

[Insight: Non-obvious synthesis they don't know]
[Deadline, pattern, clustering, comparison, consequence they haven't considered]

[Inquisition: Low-effort question]
[Simple routing question or one-word answer request]
```

### Requirements

- **Length:** Under 75 words total
- **Data:** Every claim PROVABLE (traces to database field)
- **Specificity:** Texada-level (dates, record numbers, addresses)
- **Tone:** Factual, direct, no hype
- **No soft signals:** No job postings, M&A, funding, hiring

### Example PQS (EPA ECHO)

```
Subject: March 15 EPA Citation

Your facility at 1234 Industrial Parkway received EPA ECHO violation #987654321 on March 15, 2025 for three Clean Water Act exceedances (pH 9.2, TSS 180 mg/L, BOD 220 mg/L). The consent decree milestone deadline is June 30, 2025—89 days out. Are you tracking remediation progress against this timeline internally, or would an external milestone tracker help?
```

**Why this works:**
- ✅ Hyper-specific: Facility address, violation number, date, exact parameter values
- ✅ Factually grounded: Traces to EPA ECHO fields (VIOLATION_DATE, FACILITY_ADDRESS, POLLUTANT_DESC)
- ✅ Non-obvious: They know about the violation, but may not have calculated days to deadline or considered milestone tracking

### Anti-Pattern PQS (DO NOT DO THIS)

```
Subject: Environmental Compliance Help

Hi [Name],

I noticed your company is in manufacturing and may face environmental compliance challenges. Many facilities in your industry struggle with EPA regulations. Our platform helps companies stay on top of their compliance obligations.

Would you have 15 minutes to discuss how we can help?
```

**Why this fails:**
- ❌ Generic (no specific facility, violation, or date)
- ❌ Not grounded (no database, no record number, just assumptions)
- ❌ Obvious (doesn't tell them anything they don't know)
- ❌ High effort (meeting request, not simple question)

---

## PVP vs PQS: The Critical Distinction

**PQS (Pain Qualified Segment):**
"I think you're in this painful situation, am I right?"
- Identifies pain with data
- Seeks confirmation/engagement
- Points TO value but doesn't deliver it
- Score target: 7-8/10 (strong pain identification)

**PVP (Permissionless Value Prop):**
"Here's the complete actionable thing you can do RIGHT NOW from this message alone"
- Delivers complete value independently
- Recipient can take action WITHOUT replying
- Contains names, contacts, prices, dates for immediate action
- Score target: 8.5-10/10 (true independent value)

### The "Independently Useful" Test (CRITICAL)

A message is ONLY a PVP if the recipient can **take concrete action WITHOUT replying to you**:

✅ **PASSES (True PVPs):**
- "Property at 18904 Bajo Dr sold Oct 22, seller offering $2K flooring credit. Agent: Sheila Gibbs, sheila@gibbshomesales.com, 405-532-3212"
  → Can call agent NOW
- "Buy chlorine from Sunbelt or PoolCorp at $4.20/lb in Phoenix, use 2.3 lbs per pool (not 3.8) to hit 47% margins"
  → Can call suppliers NOW, change ordering NOW
- "186 pools completing at Windgate Ranch Dr (67), Desert Bloom Way (52), Sunset Vista (37), starting Jan 15"
  → Can drive there NOW, plan routes NOW

❌ **FAILS (Actually PQS):**
- "Your 7-aircraft mixed-fleet creates hiring disadvantage in mechanic shortage"
  → No action available, just pain description
- "I'll send you the regional A&P shortage breakdown if useful"
  → Promises future value, doesn't deliver now
- "FAA inspection patterns follow predictable cycles"
  → Describes situation, doesn't provide specific action

### What Makes Information "Complete" for PVPs

To be independently useful, message MUST include:

**For Lead Generation PVPs:**
- [ ] Specific property addresses OR business names
- [ ] Contact names (agents, managers, owners)
- [ ] Phone numbers and/or email addresses
- [ ] Timing/urgency indicators (dates, deadlines)

**For Pricing/Procurement PVPs:**
- [ ] Specific vendor/supplier names
- [ ] Exact prices or pricing ranges
- [ ] Product specifications or requirements
- [ ] Contact information or procurement process

**For Compliance/Regulatory PVPs:**
- [ ] Specific regulation name and number
- [ ] Exact deadline dates
- [ ] Required forms/documents (with numbers)
- [ ] Approved vendors/consultants with contacts
- [ ] Penalty amounts if non-compliant

**For Competitive Intelligence PVPs:**
- [ ] Specific competitor names
- [ ] Exact metrics or benchmarks
- [ ] Data sources they can verify
- [ ] Recommended actions with calculations

## PVP Message Format

### Structure

```
Subject: [Specific value being delivered - what they can DO]

[Intro: What you're giving them - specific, concrete, COMPLETE]
[Names, contacts, prices, dates - everything needed for action]

[Insight: Why this matters to them specifically]
[Business impact, risk avoided, opportunity identified]

[Simple closing question]
[Optional: routing or one additional piece of info they can request]
```

### Requirements

- **Length:** Under 100 words total
- **Value:** Must be immediately ACTIONABLE without meeting or purchase
- **Completeness:** Contains ALL information needed for action (names, contacts, prices, dates)
- **Specificity:** Texada-level data citations
- **Tone:** Generous, helpful, no strings attached
- **Test:** Recipient can take action WITHOUT replying to you

### Example PVP #1 (Floorzap - Real Estate Lead)

```
Subject: floor order

Did you see that 18904 Bajo Dr, Edmond, OK 73012 just sold on October 22nd?

The listing mentioned that the seller is offering a $2,000 flooring credit with an acceptable offer. This suggests there might be some flooring work needed in the home. You can check out more details here: https://www.realtor.com/realestateandhomes-detail/18904-Bajo-Dr_Edmond_OK_73012_M77493-19608

Thought this might be a good lead for you to check out!

Thanks,
Jordan Crawford
Founder | BlueprintGTM

P.S. The listing agent was Sheila Gibbs. You can reach her at sheila@gibbshomesales.com or 405-532-3212.
```

**Why this is a TRUE PVP:**
- ✅ Complete information: Property address, sale date, agent name, email, phone
- ✅ Immediate action: Can call Sheila RIGHT NOW without replying
- ✅ Independently useful: Contains everything needed to pursue lead
- ✅ Specific trigger: $2K flooring credit = work needed
- **Independently Useful Test: PASSES** - They can act without replying

### Example PVP #2 (Skimmer - Pool Service Pricing)

```
Subject: Do you charge $169 for pool care?

We work with thousands of pool pros in CA and our data shows the optimal flat monthly rate including chemicals in 95125 is $169. How does your pricing compare?

The flat monthly rate including chemicals in 95125 typically ranges from $108 to $184.

At less than $169, you're potentially undervaluing your services.

Want me to show you how I know for sure on a call?
```

**Why this is a TRUE PVP:**
- ✅ Complete benchmark: Exact price ($169), exact range ($108-$184), exact zip code
- ✅ Immediate action: Can adjust pricing RIGHT NOW without replying
- ✅ Independently useful: Market data delivered in full
- ✅ Simple calculation: If under $169, they're underpriced
- **Independently Useful Test: PASSES** - They can change pricing without replying

### Example PVP #3 (Skimmer - Chemical Usage Optimization)

```
Subject: You're 1.5 pounds too heavy

Analyzed chemical usage across 8,400 pool service companies nationwide - the top 10% most profitable use just 2.3 lbs chlorine per pool weekly versus the average 3.8 lbs, saving $1,840 per route monthly at current prices.

In Phoenix specifically, companies buying chlorine at $4.20/lb or less (from suppliers like Sunbelt or PoolCorp) while using under 2.5 lbs per pool maintain 47% gross margins versus the market average of 31%.

Want to see how your chemical usage per pool compares to the top performers in your market?
```

**Why this is a TRUE PVP:**
- ✅ Complete information: Specific suppliers (Sunbelt, PoolCorp), exact price ($4.20/lb), target usage (2.3 lbs)
- ✅ Immediate action: Can call those suppliers TODAY and reduce usage
- ✅ Independently useful: Contains benchmark, suppliers, expected margin impact
- ✅ Specific to location: Phoenix pricing and suppliers
- **Independently Useful Test: PASSES** - They can change suppliers/usage without replying

### Anti-Pattern PVP (DO NOT DO THIS)

```
Subject: Market Insights Available

Hi [Name],

I have valuable market intelligence that could help your team make better strategic decisions. I've analyzed data across your industry and found interesting patterns.

Can we schedule 30 minutes for me to share these insights with you?
```

**Why this fails:**
- ❌ No value delivered (just a promise of value)
- ❌ Not specific (what data? what patterns? from where?)
- ❌ No actionable information (no names, contacts, prices, or steps)
- ❌ High effort (requires meeting to get the value)
- ❌ Generic (could be sent to anyone in any industry)
- **Independently Useful Test: FAILS** - Cannot take action without scheduling meeting

### Anti-Pattern "Pseudo-PVP" (ALSO WRONG)

```
Subject: Your mechanic shortage problem

ATEC's 2025 workforce report shows a 5,338 A&P mechanic shortage nationwide. Your 7-aircraft mixed-fleet operation requires cross-training across 4 manufacturer types, which means each new hire needs training across King Air, Citation, Pilatus, and Caravan systems vs. single-type operators.

This creates a significant hiring disadvantage in the current market.

How are you managing maintenance capacity with current staffing?
```

**Why this fails as a PVP (but works as PQS):**
- ❌ No actionable information: Describes pain but provides no solution
- ❌ Missing: WHO to recruit, WHERE to find them, HOW to contact them
- ❌ Missing: Specific mechanic names, recruiters, training programs, vendors
- ✅ Strong pain identification (this IS a good PQS message)
- **Independently Useful Test: FAILS** - Cannot take hiring action without replying

**How to fix it into a TRUE PVP:**
Add complete actionable information:
```
Subject: 3 Dallas A&P mechanics with your certs

These 3 A&P mechanics in Dallas have King Air + Citation certifications:
- Robert Martinez (LinkedIn: /in/robertmartinez-ap) - currently at Lone Star Aviation
- Jennifer Chen (LinkedIn: /in/jchen-mechanic) - currently at DFW Maintenance
- Mike Thompson (LinkedIn: /in/mikethompson-amt) - currently at Texas Air Service

All work at single-type operators. Mixed-fleet operators typically pay $8-12/hour premium in Dallas market.

Want their current employers' turnover data?
```
Now they can recruit these people WITHOUT replying.

---

## Hard Data vs Soft Signals

### ✅ HARD DATA (Use These)

**Government Databases with Timestamped Records:**

- **EPA ECHO:** Violations, permits, inspections (violation number, date, facility address, pollutant types, penalty amounts)
- **OSHA:** Workplace safety citations (citation ID, inspection date, violation type, penalty amount, abatement date)
- **CMS:** Provider quality ratings, utilization data (facility ID, quality scores, utilization rates, county-level data)
- **FDA:** Warning letters, 483 inspection observations (facility name, observation date, specific violations)
- **FMCSA/SAFER:** Transportation violations (carrier ID, violation type, inspection date, out-of-service orders)
- **State Licensing Boards:** Disciplinary actions, license issue dates (license number, action date, action type)

**Characteristics:**
- Record numbers you can cite
- Dates that are specific (not "recent")
- Field names you can reference
- Public access (web portal, API, bulk download)
- Government authority (trusted source)

### ❌ SOFT SIGNALS (Never Use These)

**Job Postings:**
- "I see you're hiring for..." - Everyone sees job posts, prospects already know
- Doesn't indicate CURRENT pain, just future staffing plans
- Weak proxy for urgency

**M&A Activity:**
- "I noticed you recently acquired..." - Public news, everyone knows
- Doesn't indicate specific operational challenges
- Generic and overused

**Funding Announcements:**
- "Congrats on your Series B..." - Spam trigger, everyone says this
- Doesn't indicate what they'll use money for
- Shows you didn't do real research

**Technology Stack:**
- "I see you use Salesforce..." - Tools like BuiltWith make this obvious
- Doesn't indicate dissatisfaction or pain point
- Weak relevance to real challenges

**LinkedIn Activity:**
- "I saw your post about..." - Creepy stalking signal
- Doesn't indicate urgent business need
- Transparently inauthentic

**Industry Trends:**
- "Companies in your space are facing..." - Generic, not about THEM
- Could apply to anyone
- Shows you haven't researched their specific situation

---

## Field Verification Checklist

Before using ANY data claim in a message, verify:

**1. Database Documented**
- [ ] Database name recorded from Wave 2
- [ ] Database URL accessible and verified
- [ ] Database update frequency known

**2. Field Names Actual**
- [ ] Specific field name documented (e.g., "VIOLATION_DATE" not "date field")
- [ ] Field extracted from live portal or API documentation
- [ ] NOT assumed based on logic ("they probably track...")

**3. Data Provable**
- [ ] Can answer: "Which exact field proves this claim?"
- [ ] Value is in database, not inferred
- [ ] Record number or ID available to cite

**4. Specificity Level**
- [ ] Has dates (YYYY-MM-DD format when possible)
- [ ] Has record/violation/citation numbers
- [ ] Has facility names or addresses when relevant
- [ ] Has specific field values (not ranges or "approximately")

---

## Revision Guide

When a message scores REVISE (6.0-7.9), identify WHICH criteria scored lowest:

**If Situation Recognition <8:**
- Add more specific details (facility address, record number, date)
- Replace "your company" with exact facility/location name
- Replace "recent" with actual date

**If Data Credibility <8:**
- Add record numbers or database field references
- Remove any inferred or assumed claims
- Cite specific database name

**If Insight Value <8:**
- Add non-obvious synthesis (deadlines, patterns, comparisons)
- Calculate something they haven't (days to deadline, percentile ranking)
- Find clustering or trends they don't see

**If Effort to Reply <8:**
- Change question to yes/no or routing question
- Remove meeting request
- Make reply trivial

**If Emotional Resonance <8:**
- Add urgency (deadline, countdown, risk)
- Make it more personal (their exact facility, not "companies like yours")
- Surface a consequence they should care about

**If fails Texada Test:**
- Hyper-specific failure → add dates, numbers, addresses
- Factually grounded failure → trace every claim to database field, remove inferences
- Non-obvious failure → add synthesis they don't already know

---

## Action Extraction & Completeness Check (Required for PVPs)

Before classifying any message as a PVP, perform this explicit check:

### Step 1: Identify the Intended Action

**Ask: "What specific action can the recipient take from this message alone?"**

Examples of valid actions:
- Call a specific person (requires: name, phone/email)
- Contact a vendor (requires: company name, contact info, pricing)
- Attend an event (requires: address, date, time)
- Change a process (requires: specific steps, benchmarks, tools)
- Purchase from supplier (requires: supplier name, product, price, contact)

Examples of NON-actions (pain description only):
- "Consider your hiring challenges" → No action
- "Think about your maintenance burden" → No action
- "Be aware of this shortage" → No action

### Step 2: Extract Required Information for That Action

**For each identified action, list what information is REQUIRED:**

**Calling a person:**
- [ ] Person's name
- [ ] Phone number OR email address
- [ ] Context (why call them)

**Contacting a vendor:**
- [ ] Vendor/company name
- [ ] Product/service specifics
- [ ] Price or pricing range
- [ ] Phone/email/website

**Changing a process:**
- [ ] Current benchmark/metric
- [ ] Target benchmark/metric
- [ ] Specific steps to change
- [ ] Tools/vendors if needed

**Attending/visiting location:**
- [ ] Specific address
- [ ] Date/time OR "starting when"
- [ ] What to do there

### Step 3: Check Data Availability

**For each required piece of information, verify:**

Can we get this from our data sources?
- ✅ YES: Property address from real estate database
- ✅ YES: Agent name/contact from listing
- ✅ YES: Supplier names from industry directories
- ✅ YES: Pricing from public rate cards
- ❌ NO: Mechanic LinkedIn profiles (would need manual search)
- ❌ NO: Part 145 shop current lead times (would need calling)
- ❌ NO: Approved vendor pricing (would need RFP process)

### Step 4: Completeness Verdict

**Complete (Can generate TRUE PVP):**
- All required information is available from data sources
- Recipient can take action WITHOUT replying to you
- Generate PVP with 8.5+ target score

**Incomplete (Generate PQS instead):**
- Missing 1+ pieces of required information
- Recipient would need to reply for missing info
- Generate strong PQS (7.0-8.4 target score) that identifies pain

**Insufficient (Don't attempt):**
- Cannot identify concrete action
- Only pain description available
- This may not be a viable Blueprint GTM use case

### Examples of Completeness Check

**Example 1: Floorzap Property Lead**

Action: Call listing agent about flooring work
Required info:
- ✅ Property address (from real estate database)
- ✅ Sale date (from real estate database)
- ✅ Flooring credit amount (from listing description)
- ✅ Agent name (from listing)
- ✅ Agent email (from listing)
- ✅ Agent phone (from listing)

**Verdict: COMPLETE → Generate TRUE PVP**

**Example 2: Wingwork Mechanic Recruitment**

Action: Recruit specific mechanics
Required info:
- ❌ Mechanic names (NOT in FAA databases)
- ❌ Current employers (NOT in FAA databases)
- ❌ LinkedIn profiles (would require manual search)
- ❌ Contact information (NOT public)

**Verdict: INCOMPLETE → Generate PQS about mechanic shortage instead**

**Example 3: Wingwork Regulatory Deadline**

Action: Contact approved software vendors for compliance
Required info:
- ✅ Regulation name/number (AC 120-78A from FAA)
- ✅ Deadline date (from regulatory calendar)
- ✅ Required forms (from FAA documentation)
- ❌ Approved vendor names (would require FAA vendor list search)
- ❌ Vendor pricing (NOT public)
- ❌ Vendor contact info (would need vendor website lookup)

**Verdict: INCOMPLETE → Generate PQS about upcoming deadline instead**

To make this a TRUE PVP, would need to:
1. Search for FAA-approved vendors
2. Get their contact information
3. Get their pricing (if public)
4. THEN can generate PVP with complete vendor list

### Honest Assessment Required

**When data sources don't provide complete action info:**
- Don't force it into a PVP
- Generate excellent PQS instead (7.0-8.4 is great!)
- Note in assessment: "Strong PQS opportunity, PVP would require additional data: [list]"

**When to build proprietary databases:**
- If same data needed repeatedly (e.g., Part 145 shop directory)
- If gathering once enables many PVPs (e.g., approved vendor catalogs)
- Consider ROI of data collection vs. PQS approach

---

## Quality Gate Standards

**Minimum requirements before HTML generation:**

- [ ] At least 2 HIGH feasibility segments validated
- [ ] At least 4 messages total (can be mix of PQS and PVP)
- [ ] All PVP messages score ≥8.5/10 AND pass Independently Useful Test
- [ ] All PQS messages score ≥7.0/10
- [ ] All messages pass all 3 Texada Test criteria
- [ ] All data claims trace to specific database fields (verified in Wave 2)
- [ ] No soft signals in any message
- [ ] All messages under length limits (75 words PQS, 100 words PVP)
- [ ] PVP messages contain complete actionable information (names, contacts, prices, dates)

**Realistic Expectations:**

- **TRUE PVPs are RARE:** Most use cases will generate 0-1 true PVPs (8.5+)
- **Strong PQS is SUCCESS:** 2-4 excellent PQS messages (7.5-8.4) is a great outcome
- **Don't force PVPs:** A score of 8.0 that lacks complete action info is a PQS, not a weak PVP

**Target Mix (Realistic):**

**Ideal Case (Data-Rich):**
- 2 TRUE PVPs (8.5+, complete action info)
- 2 Strong PQS (7.5-8.4, pain identification)

**Typical Case (Most Verticals):**
- 0-1 TRUE PVPs (if complete action data available)
- 3-4 Strong PQS (7.5-8.4, excellent pain identification)

**Challenging Case (Operational Pain):**
- 0 TRUE PVPs (no public action data)
- 2-4 Strong PQS (7.5-8.0, best possible with available data)

**If quality gates not met:**

- Generate 2 additional message variants
- Re-critique with same standards
- Be honest about PQS vs PVP classification
- If still failing threshold:
  * PVP threshold: Keep at 8.5+, don't lower (integrity of definition)
  * PQS threshold: Can lower to 7.0 with CLEAR disclaimer in HTML
- Never ship messages <7.0 under any circumstances

**Classification Honesty:**

In HTML output, clearly label:
- **"TRUE PVP" (8.5+):** Complete actionable information, independently useful
- **"Strong PQS" (7.5-8.4):** Excellent pain identification, seeks engagement
- **"Solid PQS" (7.0-7.4):** Good pain identification with disclosed limitations

Don't label PQS messages as PVPs just to hit targets.

---

## Message Length Guidelines

**PQS: 75 words max**

Why: Busy persona needs to absorb situation instantly. Longer = skip.

Count technique:
- Subject line: 2-4 words (doesn't count toward limit)
- Body: 75 words total
- Use tools like word counter or manual count
- If >75, remove fluff first, then reduce detail as last resort

**PVP: 100 words max**

Why: Delivering value requires slightly more space to explain what you're giving + why it matters. But still must be scannable.

Count technique:
- Subject line: 4-6 words (doesn't count)
- Body: 100 words total
- Prioritize: What value (20-30 words) → Why it matters (30-40 words) → Routing (10-15 words)

---

## Common Failure Patterns to Avoid

**Pattern 1: "Insider" Language**

❌ "Your KPIs around patient throughput optimization..."
✅ "Your county had 18.4 post-acute visits per 1,000 Medicare beneficiaries..."

Use their data, not consulting jargon.

**Pattern 2: Feature Pitching**

❌ "Our platform helps you track compliance with automated alerts..."
✅ "You have 6 consent decree milestones due in next 120 days..."

Mirror situation, don't pitch solution.

**Pattern 3: Vague Urgency**

❌ "You should address this soon..."
✅ "89 days until your June 30 deadline..."

Specific dates, not vague pressure.

**Pattern 4: LinkedIn Stalking**

❌ "I saw your post about innovation..."
✅ [Don't mention their social media AT ALL]

Use government data only.

**Pattern 5: Assumed Pain**

❌ "Like many manufacturers, you probably struggle with..."
✅ "Your facility received violation #987654321..."

Prove, don't assume.

---

## Multi-Modal Data Approaches

**CRITICAL UPDATE:** Blueprint GTM is NOT limited to government databases only.

The original methodology emphasized government data because it's the GOLD STANDARD (90-95% confidence, verifiable, no inference). However, many private business pain points cannot be detected through government data alone.

**The framework now supports 3 tiers of data approaches:**

### Tier 1: Pure Government Data (90-95% Confidence)

**When to Use:**
- Regulated industries (healthcare, environment, safety, finance)
- Pain points that create compliance violations or public records
- Target personas responsible for regulatory compliance

**Examples:**
- EPA ECHO violations → Environmental compliance pain
- OSHA citations → Workplace safety issues
- CMS quality ratings → Healthcare performance gaps
- FDA warning letters → Product quality violations
- State licensing board actions → Professional compliance

**Advantages:**
- Highest confidence (verifiable record numbers)
- No inference required (direct observation)
- Prospects can verify themselves instantly
- Strongest Texada Test performance

**Message Disclosure:** None needed - state facts directly

**Example:**
> "Your facility at 1234 Industrial Parkway received EPA ECHO violation #987654321 on March 15, 2025 for three Clean Water Act exceedances..."

### Tier 2: Hybrid Approaches (60-75% Confidence)

**When to Use:**
- Private business pain points (pricing, competition, efficiency)
- Industries without heavy regulation (restaurants, retail, SaaS)
- Pain points requiring competitive intelligence or velocity signals

**Data Combinations:**
1. **Government + Competitive**
   - Health inspections + online pricing analysis
   - Licensing data + technology stack detection

2. **Competitive + Velocity**
   - Menu pricing arbitrage + review growth rate
   - Pricing comparison + web traffic estimation

3. **Government + Velocity**
   - Quality ratings + patient volume trends
   - Inspection frequency + location expansion rate

**Requirements:**
- MUST combine 2-3 data sources (not single source)
- MUST include calculation worksheet for EVERY claim
- MUST disclose hybrid nature with hedging language ("estimated," "tracked," "based on," "likely")
- MUST show verification path (how prospect can check)

**Message Disclosure:** Use qualifying language

**Example (Owner.com):**
> "I tracked your menu pricing across your website vs. DoorDash over the past 30 days—average markup is 28.3% on 47 items, costing you an **estimated** $4,200/month in platform fees **based on** your 142 reviews/month velocity."

Note the hedging: "tracked" (not "found exactly"), "estimated" (not "you're paying"), "based on" (showing inference)

### Tier 3: Pure Competitive/Velocity (50-70% Confidence)

**When to Use:**
- Absolutely no government data available
- Prospect's industry has zero regulatory footprint
- Pain point is purely competitive/operational

**Examples:**
- SaaS pricing comparison (no violations to cite)
- E-commerce conversion rate benchmarking
- App store rating velocity vs. competitors

**Requirements:**
- HEAVY hedging in message language
- Clear calculation worksheet with ALL assumptions documented
- Multiple verification paths offered
- Consider whether this meets Texada Test at all

**Use Sparingly:** This tier is the weakest. Only use when Tier 1 and Tier 2 are impossible.

**Message Disclosure:** Maximum transparency

**Example:**
> "Comparing your pricing page to your top 5 competitors suggests you're **likely** in the top quartile on price. **This analysis used** [sources]. **Caveat:** Pricing alone doesn't predict win rates—happy to share methodology if useful."

### Decision Tree: Which Tier to Use?

```
START: What pain point does [Company] solve?

↓

Is pain point REGULATED? (Creates violations, licenses, inspections, quality ratings)
  → YES: Use Tier 1 (Pure Government)
  → NO: Continue ↓

Can pain be OBSERVED in competitive behavior? (Pricing, tech stack, reviews, traffic)
  → YES: Can you COMBINE with government data?
    → YES: Use Tier 2 (Hybrid - Gov + Competitive)
    → NO: Continue ↓
  → NO: Continue ↓

Can pain be INFERRED from velocity signals? (Review growth, hiring rate, web traffic)
  → YES: Can you COMBINE with competitive data?
    → YES: Use Tier 2 (Hybrid - Competitive + Velocity)
    → NO: Use Tier 3 (Pure Velocity - LOW confidence)
  → NO: STOP - Cannot apply Blueprint GTM to this use case
```

### Calculation Worksheet Requirements

**ALL tiers require calculation worksheets, but depth varies:**

**Tier 1 (Government):**
```
CLAIM: [exact claim]
DATA SOURCE: [database name, field names, record numbers]
CALCULATION: Direct field value OR simple date math
CONFIDENCE: 95%
VERIFICATION: [exact portal URL + navigation steps]
```

**Tier 2 (Hybrid):**
```
CLAIM: [exact claim with hedging language]
DATA SOURCE #1: [government/competitive source]
DATA SOURCE #2: [velocity/competitive source]
CALCULATION: [formula showing how sources combine]
ASSUMPTIONS: [what you're inferring]
CONFIDENCE: 60-75%
VERIFICATION: [how prospect can check each source]
```

**Tier 3 (Pure Competitive/Velocity):**
```
CLAIM: [heavily hedged claim]
DATA SOURCES: [all sources used, 3+ typically]
CALCULATION: [full formula with all assumptions]
ASSUMPTIONS: [explicitly list every inference]
LIMITATIONS: [what this doesn't tell us]
CONFIDENCE: 50-70%
VERIFICATION: [multiple paths to check]
```

### Quality Standards by Tier

**Tier 1 Messages:**
- **PVP Target:** 8.5+ (if complete actionable info available)
- **PQS Target:** 7.5-8.4 (pain identification)
- Must pass all 3 Texada Test criteria
- No hedging language needed
- Gold standard
- Examples: EPA violations, OSHA citations, CMS ratings

**Tier 2 Messages:**
- **PVP Target:** 8.5+ (if complete actionable info available, WITH disclosed confidence)
- **PQS Target:** 7.0-8.0 (pain identification with disclosed inference)
- Must pass all 3 Texada Test criteria WITH disclosed confidence
- Hedging language REQUIRED ("estimated," "based on," "tracked")
- Must include "how I calculated this" in message or offer to share
- Examples: Owner.com pricing analysis, Skimmer chemical usage benchmarks

**Tier 3 Messages:**
- **PVP Target:** 8.5+ (VERY rare, usually impossible)
- **PQS Target:** 7.0-7.5 (acknowledge heavy inference)
- May struggle with Texada Test "factually grounded" (heavy inference)
- Maximum hedging language REQUIRED
- Often FAILS Blueprint standards—use only when no alternative exists
- Consider if Blueprint GTM applies to this use case at all

**Note on Scoring:**
- PVP threshold (8.5+) is INDEPENDENT of tier
- Tier affects confidence disclosure, not the "independently useful" requirement
- A Tier 2 PVP still needs complete action info (names, contacts, prices)
- A Tier 2 PQS has slightly lower bar due to inference acknowledged

### Owner.com Case Study: Why Tier 2 Works

**Original Problem:**
- Owner.com helps restaurants capture direct orders (avoid DoorDash commissions)
- Target pain: High platform fees on delivery orders
- Government data: Health inspections (irrelevant to pricing pain)

**Failed Approach (Original Execution):**
- Tried to use health violations as proxy for "struggling restaurants"
- Required INFERENCE: violation → financial strain → care about commission fees
- Failed Texada Test (not non-obvious—they know if they have violations)

**Fixed Approach (Tier 2 Hybrid):**
- DATA SOURCE 1 (Competitive): Menu pricing scraping (website vs. DoorDash)
- DATA SOURCE 2 (Velocity): Google Maps review count growth
- SYNTHESIS: Review velocity × pricing markup × industry commission rate = estimated monthly fees

**Calculation:**
```
142 reviews/month (Google Maps API - Tier 2 velocity)
× ~3% review rate (industry benchmark - assumption)
= ~4,733 orders/month (INFERRED)
× $18 avg ticket (scraped menu data - Tier 2 competitive)
× 28.3% markup (DoorDash vs. website pricing - Tier 2 competitive)
÷ 1.283 (to get base commission from markup)
= $4,200/month in platform fees (ESTIMATED)
```

**Why This Works:**
- ✅ Hyper-specific: Exact review count (142), exact markup (28.3%), exact menu items cited
- ✅ Factually grounded: All inputs OBSERVABLE (not assumed), calculation transparent
- ✅ Non-obvious: They know they use DoorDash, DON'T know their exact monthly cost or markup % across full menu
- Confidence: 65% (disclosed with "estimated" and "based on")
- Texada Test: PASSES (with disclosed confidence level)

### When to Reject a Use Case Entirely

**Even Tier 3 won't work if:**

1. **Pain point is purely INTERNAL** (culture issues, management problems, employee satisfaction)
   - No external data trail
   - Would require soft signals (org chart stalking, Glassdoor, LinkedIn)
   - REJECT

2. **Pain point requires PERMISSION** to detect (access to private systems, analytics dashboards)
   - Can't prove without insider access
   - Would be creepy to claim knowledge
   - REJECT

3. **Pain point is ASSUMPTION-BASED** ("companies like yours probably struggle with...")
   - No data trail, just inference from industry/stage/size
   - Violates "factually grounded" Texada criterion
   - REJECT

4. **Only soft signals available** (job posts, M&A, funding, LinkedIn activity)
   - Explicitly banned in methodology
   - Everyone sees these signals
   - REJECT

### Summary: Honest Confidence Levels

Blueprint GTM is most powerful with Tier 1 (pure government data). But it CAN work with Tier 2 hybrid approaches IF:

- You combine 2-3 observable data sources
- You disclose confidence levels honestly (60-75%)
- You provide calculation worksheets showing your work
- You use hedging language ("estimated," "tracked," "based on")
- You still pass the Texada Test with disclosed inference

The framework CANNOT work with:
- Pure assumption ("companies like yours...")
- Soft signals (job posts, M&A, funding)
- Internal pain points with no external data trail
- Single-source inference without triangulation

**When in doubt:** Try Tier 1 first. If impossible, try Tier 2. If both fail, consider whether Blueprint GTM applies to this use case at all.

---

## Blueprint Philosophy Reminders

**The Message Isn't the Problem. The LIST Is the Message.**

- When you target the exact right person experiencing the exact right situation at the exact right time, mediocre copy works.
- When you target the wrong person, Shakespeare couldn't save you.
- This methodology is about FINDING THE RIGHT PEOPLE, not wordsmithing perfect pitches.

**Intelligence Over Interruption**

- Stop sending messages ABOUT what you do
- Start sending intelligence about what THEY need to know right now
- Lead with their data, not your features

**Compete on Intelligence, Not Features**

- Features are table stakes
- Everyone has "AI-powered," "real-time," "seamless"
- What they don't have: this specific EPA violation happened to this specific facility on this specific date
- That's the moat

---

This methodology file should be referenced during Wave 3 (Message Generation + Critique) to ensure consistent quality and adherence to Blueprint standards.
