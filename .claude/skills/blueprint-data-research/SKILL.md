---
name: blueprint-data-research
description: Validate pain-qualified segments with hard public data sources (EPA ECHO, OSHA, FDA, FMCSA, permits, violations). Creates field-level data recipes showing exactly how to identify companies in each painful situation. Use after completing blueprint-company-research.
---

# Blueprint GTM Data Source Research

## Purpose

Take pain segment hypotheses from company research and validate whether they're **detectable** using hard public data. Focus on government databases with timestamped violations, permits, enforcement actions, and compliance records - NOT soft signals like job postings or M&A.

This is Stage 2 of the Blueprint GTM Intelligence System.

## Methodology Reference

This skill implements the Blueprint GTM v1.1.0 methodology. For detailed guidance on:
- PVP vs PQS distinction (8.5+ threshold for TRUE PVPs, 7.0-8.4 for Strong PQS)
- Independently Useful Test (complete actionable information requirements)
- Data tier framework (Tier 1: Government, Tier 2: Hybrid, Tier 3: Competitive/Velocity)
- Message scoring rubrics and quality standards

See: `references/methodology.md`

## Core Philosophy: Hard Data Only

**What We're Looking For:**
- Government enforcement databases (EPA ECHO, OSHA, FDA, FMCSA/SAFER)
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

## When to Use This Skill

- After completing `blueprint-company-research` skill
- User has pain segment hypotheses that need data validation
- Need to create "Pain Data Recipes" for segment targeting
- Determining which segments are actually detectable

## Requirements

**Input Required:**
- Pain segment hypotheses from company research (3-5 segments with trigger events and pain descriptions)
- Company context (what they sell, who they serve)

**Dependencies:**
- Must complete `blueprint-company-research` first
- Requires understanding of target ICP and personas

## Workflow

### Phase 1: Review Pain Segment Hypotheses

Start by reviewing the output from company research.

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

### Phase 2: Hard Data Source Discovery (MANDATORY WEB SEARCH)

For each segment, **actively search the web** to discover what specific government databases exist that could reveal companies in that situation.

**YOU MUST USE WEB SEARCH - DO NOT RELY ON INTERNAL KNOWLEDGE**

**Research Strategy:**

#### Step 1: Identify Regulatory Context

Based on the segment's industry and pain type, determine what agencies likely regulate them.

**Search Queries to Execute:**

```
"[ICP Industry] regulatory agencies"
"[ICP Industry] compliance requirements"
"[ICP Industry] government databases"
"[Specific pain type] enforcement data"
"[Industry] violation records public database"
```

**Example:**
- Segment: Food manufacturers with safety violations
- Searches:
  - "food manufacturing regulatory agencies"
  - "FDA food safety enforcement database"
  - "FSMA violation records public access"
  - "food facility inspection database"

#### Step 2: Search for Specific Government Databases

For each potentially relevant agency discovered, search for their public data portals.

**Search Queries to Execute:**

```
"[Agency name] public data"
"[Agency name] enforcement database"
"[Agency name] violation search"
"[Agency name] API documentation"
"[Agency name] bulk data download"
"[Agency name] inspection records"
```

**Example:**
- Agency discovered: FDA
- Searches:
  - "FDA inspection classification database"
  - "FDA warning letters database"
  - "FDA recall API documentation"
  - "FDA 483 observations public access"

#### Step 3: Verify Database Access and Capabilities

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

4. **Document what you ACTUALLY find**
   - Don't assume - verify by visiting the site
   - Take note of exact URLs
   - Screenshot or note field names if visible

**Critical Questions to Answer Through Active Research:**

1. **What's the exact database name and URL?**
   - Found via web search, confirmed by visiting
   - Example: "EPA ECHO" → Search confirms → Visit https://echo.epa.gov/ → Verify it works

2. **What level of detail does it provide?**
   - Visit the search portal and check available filters
   - Facility-specific? Company-wide? Industry aggregate?
   - Does it include dates, violation types, record numbers?
   - Can you filter by date range, location, severity?

3. **How is it accessible?**
   - Web portal with search? (Test it)
   - API available? (Search for "[database] API docs" and visit)
   - Bulk download (CSV, JSON)? (Look for download links)
   - Requires account/payment? (Check registration pages)

4. **How often is it updated?**
   - Look for "last updated" dates on the site
   - Check "About" or "Data" pages for update frequency
   - Search: "[database name] update frequency"

5. **What's the data quality?**
   - Run sample queries and check results
   - Complete records or missing data?
   - Consistent formatting?
   - Historical data available (how far back)?

6. **What specific fields are available?**
   - THIS IS CRITICAL - document ACTUAL field names by looking at search results
   - If API exists, check API documentation for field schema
   - If bulk download exists, download a sample and inspect column names
   - Look for: violation types, dates, amounts, status, facility identifiers, addresses

#### Step 4: Search for Alternative Access Methods

Sometimes direct government portals are clunky. Search for easier access methods:

**Search Queries:**

```
"[database name] Apify actor"
"[database name] RapidAPI"
"[database name] scraper"
"[database name] data.gov"
"[agency name] open data portal"
```

**Check Aggregator Platforms:**
- Search RapidAPI.com for agency/database name
- Search Apify.com store for relevant actors
- Check data.gov for bulk downloads
- Look for third-party API wrappers

**Example:**
- Database: OSHA Establishment Search
- Additional searches:
  - "OSHA data Apify" → Find if scraper exists
  - "OSHA enforcement RapidAPI" → Check API marketplace
  - "OSHA data.gov" → Find bulk data files

#### Step 5: Document Field-Level Details

For each promising data source discovered through your web research, create detailed documentation.

**Required Documentation (Based on What You Actually Found):**

```markdown
### Data Source: [Database Name]

**Discovery Method:** [How you found this - web search queries used]

**Source Type:** Government enforcement database / Permit system / Licensing database

**Agency:** [Specific agency/department - confirmed via web search]

**Access URL:** [Direct link to search portal or API docs - VERIFIED BY VISITING]

**Update Frequency:** [How often data refreshes - found on site or via search]

**Geographic Coverage:** [National / State-specific / Local - confirmed via site]

**Historical Data:** [How far back records go - verified by checking database]

**Access Method (check all that you CONFIRMED exist):**
- [ ] Web portal with search (tested and working)
- [ ] Public API (link to docs: _____)
- [ ] Bulk download available (link: _____)
- [ ] Apify actor available (link: _____)
- [ ] RapidAPI listing (link: _____)
- [ ] Data.gov dataset (link: _____)
- [ ] FOIA request required
- [ ] Paid access required ($____ pricing found at: _____)

**Key Data Fields Available:**
[List ACTUAL field names found by visiting database/API docs]

CRITICAL: These must be ACTUAL field names, not assumed fields.
Source of field names: [API documentation / Sample query results / Bulk data file / Database search interface]

Example format:
- `violation_date` (format: MM/DD/YYYY - confirmed in sample results)
- `violation_type` (values seen: "Serious", "Willful", "Repeat", "Other")
- `facility_name` (string, confirmed in search results)
- `facility_address` (separate fields: street, city, state, zip)
- `naics_code` (6-digit industry code)
- `penalty_amount` (dollar amount, some records show $0)
- `abatement_due_date` (format: MM/DD/YYYY)
- `current_status` (values seen: "Open", "Closed", "Contested")

**Filtering Capabilities:**
[Document ACTUAL filters available in the search interface - verified by using it]

Example:
- Date range filter: Yes (tested with 6-month range)
- State filter: Yes (dropdown with all states)
- Violation type filter: Yes (checkboxes for serious/willful/repeat)
- NAICS code filter: Yes (text entry)
- Penalty amount range: No (not available)

**Data Quality Assessment (based on sample queries run):**
- Completeness: [High/Medium/Low - tested with 10+ sample queries]
- Accuracy: [High/Medium/Low - primary government source vs aggregator]
- Timeliness: [Most recent record date found: ___]
- Consistency: [Formats consistent across records? Any missing data patterns?]

**Practical Limitations (discovered through testing):**
[Any issues found: incomplete data, access restrictions, technical barriers, slow load times]

**API Documentation (if found):**
- Link: [Actual URL to API docs]
- Authentication: [None / API key required / OAuth / etc.]
- Rate limits: [Requests per minute/hour/day if documented]
- Response format: [JSON / XML / CSV]
- Sample endpoint: [Example API call if provided]

**Alternative Access Methods (discovered via search):**
[List any Apify actors, RapidAPI listings, data.gov datasets, third-party tools found]

**Web Search Confirmation:**
Searches performed to verify this source:
- "[database name] official site"
- "[database name] API documentation"
- "[database name] data access"
[Add any other searches that led to finding/confirming this source]
```

### Phase 3: Build Pain Data Recipes

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

Example:
- Primary: Recent OSHA violations (last 6 months)
- AND Secondary: Active building permits >$5M (expansion underway)
- = Companies with safety issues while growing operations (high risk)

**Expected Volume:**
[Rough estimate of how many companies would match - helps assess market size]

**Data Confidence:**
- Signal strength: [Strong/Medium/Weak - how reliably does this indicate pain?]
- False positive risk: [High/Medium/Low - will many non-targets match?]
- Data availability: [Consistent/Intermittent/Limited]
```

### Phase 4: Assess Segment Feasibility

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

### Phase 5: Suggest Alternatives (If Needed)

If multiple segments rate LOW or UNDETECTABLE, suggest alternative segments based on what data IS available.

**Alternative Segment Development:**

Look at what hard data sources are actually accessible for this ICP/industry, and work backwards:

1. **What government databases exist for this industry?**
   - List all accessible enforcement/compliance databases

2. **What violations/events appear in those databases?**
   - Common violation types, frequent triggers

3. **Which violations indicate meaningful pain for the ICP?**
   - Connect database events to business impact

4. **Can we craft a segment around that data?**
   - Reverse-engineer from data availability

**Example:**

Original segment (UNDETECTABLE):
"Dental practices with low treatment acceptance rates"
- Problem: No public data on acceptance rates

Available hard data:
- State dental licensing databases (new providers, license types)
- Building permits (new locations, expansions)
- Medicare violation data (some states publish)

Alternative segment (DETECTABLE):
"Dental practices that opened new locations in last 6 months (building permits) AND added specialist providers (licensing data)"
- Rationale: Expansion creates case acceptance pressure, specialists need patient flow
- Detectable: Building permits + dental licensing database
- Still relevant to original value prop

**Output for Alternatives:**

```markdown
## Alternative Segment Recommendations

### Alternative 1: [Name]

**Why This Alternative:**
[Explain connection to original pain, why it's relevant to company's value prop]

**Available Hard Data:**
- Source 1: [Database with link]
- Source 2: [Database with link]

**Pain Data Recipe:**
[Quick recipe showing how to identify companies]

**Feasibility:** [Should be HIGH or MEDIUM]

**Trade-offs vs. Original:**
[What's gained/lost by pivoting to this segment]

---

[Repeat for 2-3 alternative segments if needed]
```

## Complete Output Format

Compile all sections into a structured data source research report:

```markdown
# Blueprint GTM Data Source Research: [Company Name]

**Date:** [Today's date]
**Analyst:** [Your name/role]
**Stage:** Data Source Research (Stage 2 of 3)

---

## Executive Summary

**Segments Analyzed:** [Number]
**Feasibility Breakdown:**
- HIGH feasibility: [Count] segments
- MEDIUM feasibility: [Count] segments
- LOW feasibility: [Count] segments
- UNDETECTABLE: [Count] segments

**Recommendation:**
[Quick statement: "Proceed with [X] segments" / "Pivot to alternative segments recommended below" / "Re-scope company research due to data availability issues"]

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

## Alternative Segment Recommendations (If Applicable)
[Section from Phase 5 - only if needed]

---

## Data Source Catalog

[Comprehensive list of all databases researched, even if not used, for future reference]

### [Database 1 Name]
- **URL**: [Link]
- **Coverage**: [What it tracks]
- **Access**: [How to access]
- **Relevance**: [Which segments it could support]

### [Database 2 Name]
[Same structure]

---

## Next Steps

**Recommended Segments for Stage 3 (Message Generation):**
1. [Segment name] - HIGH feasibility
2. [Segment name] - HIGH or MEDIUM feasibility
3. [Alternative segment if needed]

**To Proceed:** Run `blueprint-message-generation` skill with HIGH feasibility segments documented above.

**If No HIGH Feasibility Segments:** Consider returning to Stage 1 to develop new pain segments based on alternative approaches identified in this research.
```

## Quality Checklist

Before completing, verify:

- [ ] Each segment has a specific government database identified (not "industry trends")
- [ ] Field-level details documented for primary data sources (actual field names)
- [ ] API documentation linked where available
- [ ] Update frequency confirmed for each source
- [ ] Feasibility ratings have clear rationale based on data access
- [ ] Data recipes are specific enough to implement (not vague)
- [ ] For UNDETECTABLE segments, alternatives suggested based on available data
- [ ] All database URLs tested and working
- [ ] At least one HIGH feasibility segment identified (or alternatives provided)

## Common Pitfalls to Avoid

### Mistake 1: Accepting "There's probably data" Without Verification

**Problem:** Assuming data exists without actually finding the database

**Solution:** Only document sources you've actually accessed and confirmed

**Example:**
- ❌ "OSHA probably has this data"
- ✅ "OSHA Establishment Search (echo.osha.gov/establishment) - confirmed violation_date, violation_type, penalty fields available"

### Mistake 2: Soft Signal Temptation

**Problem:** Defaulting to job postings or M&A when hard data is hard to find

**Solution:** Push harder to find government databases, or suggest pivoting the segment

**Example:**
- ❌ "We can identify companies hiring compliance officers"
- ✅ "No hard data found. Suggest pivot to companies with documented violations in [database]"

### Mistake 3: Missing Field-Level Documentation

**Problem:** Confirming database exists but not documenting specific fields

**Solution:** Actually access the database and list exact field names/formats

**Example:**
- ❌ "EPA ECHO tracks violations"
- ✅ "EPA ECHO fields: REGISTRY_ID, FACILITY_NAME, VIOLATION_DATE (format: MM/DD/YYYY), VIOLATION_DESC, PENALTY_AMT, NPDES_FLAG"

### Mistake 4: No Feasibility Trade-offs

**Problem:** Rating everything HIGH or everything UNDETECTABLE without nuance

**Solution:** Use MEDIUM rating for "possible but challenging" scenarios, document limitations

**Example:**
- "MEDIUM feasibility: Data exists in state-level databases (not federal), requires checking 15+ individual state portals, updated monthly with 30-60 day lag"

### Mistake 5: Giving Up Too Early

**Problem:** Rating segment UNDETECTABLE without exploring alternatives

**Solution:** If original segment isn't detectable, suggest 2-3 alternatives based on what data IS available

## Integration with Other Skills

**This Skill Receives From:**
- `blueprint-company-research`: Pain segment hypotheses, ICP profile, personas

**This Skill Feeds Into:**
- `blueprint-message-generation`: HIGH feasibility segments with data recipes

**Expected Usage Pattern:**
```
User has completed company research
→ Claude recognizes need for data validation
→ Automatically invokes this skill
→ Produces data source research report
→ Claude recognizes HIGH feasibility segments exist
→ Automatically invokes blueprint-message-generation with validated segments
```

## Tips for Consultants

1. **Start with the big federal databases**: EPA ECHO, OSHA, FMCSA, FDA - these cover most industries
2. **Check state-specific sources**: Many states publish enforcement data not in federal systems
3. **Look for public inspection schedules**: Some agencies publish upcoming audit/inspection calendars
4. **Cross-reference databases**: Combining two weaker signals often creates strong targeting
5. **Document everything**: Field names, URLs, access methods - future-you will thank you
6. **Be honest about limitations**: Better to pivot early than commit to unworkable segment
7. **Think facility-specific**: Best data ties to physical locations with addresses

## References

- See `references/DATA_SOURCES_CATALOG.md` for comprehensive list of government databases by industry
- See `references/FIELD_LEVEL_TEMPLATE.md` for template showing complete field documentation
- See `references/TEXADA_STANDARD.md` for examples of gold-standard data specificity
- See `examples/overjet/data-sources.md` for real-world example including UNDETECTABLE segments
