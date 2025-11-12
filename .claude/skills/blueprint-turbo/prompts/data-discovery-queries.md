# Data Discovery Search Query Templates

This file contains reusable search query patterns for Wave 2: Multi-Modal Data Landscape Scan.

Use these templates during the 15-20 parallel searches to maximize data source discovery across all 4 categories.

---

## CATEGORY A: Government/Regulatory Data (5-6 Queries)

### Query 1: Industry Violation Database
```
"[industry] government database violations API"
"[industry] regulatory violations public records"
"[industry] enforcement actions database"
```

**Examples:**
- "restaurant health violations database API"
- "manufacturing environmental violations public records"
- "healthcare quality violations database"

**What to Extract:**
- Database name and URL
- Record structure (violation ID, date, facility name, violation type)
- Access method (web portal, API, bulk download)
- Update frequency

---

### Query 2: Licensing Board Public Records
```
"[industry] licensing board public records search"
"[state/federal] [industry] license database"
"[industry] professional licensing violations"
```

**Examples:**
- "California restaurant licensing board records search"
- "Florida medical licensing violations database"
- "federal nursing home licensing public records"

**What to Extract:**
- License numbers, issue dates, expiration dates
- Disciplinary actions (dates, types, penalties)
- Access portal and search capabilities

---

### Query 3: Inspection Records Database
```
"[industry] inspection records database field names"
"[regulatory agency] inspection data download"
"[industry] inspection history API documentation"
```

**Examples:**
- "OSHA inspection records database field names"
- "FDA inspection data download CSV"
- "fire safety inspection history API documentation"

**What to Extract:**
- Inspection frequency fields
- Violation codes and descriptions
- Facility identifiers for linking
- Field names for date, type, outcome

---

### Query 4: Quality Ratings & Rankings
```
"[industry] quality ratings public data"
"[agency] quality scores database CSV"
"[industry] performance metrics public download"
```

**Examples:**
- "CMS nursing home quality ratings public data"
- "hospital quality scores database CSV download"
- "school performance metrics public data portal"

**What to Extract:**
- Quality score fields (star ratings, numeric scores)
- Comparison fields (state average, percentile rank)
- Update cadence (annual, quarterly, monthly)

---

### Query 5: Permit & Consent Decree Data
```
"[industry] permit database public records"
"consent decree database [industry]"
"[regulatory agency] enforcement agreements public data"
```

**Examples:**
- "EPA permit database public records API"
- "consent decree database environmental"
- "OSHA enforcement agreements public data"

**What to Extract:**
- Permit types, issue dates, expiration dates
- Consent decree milestones and deadlines
- Facility addresses linked to permits

---

### Query 6: State-Specific Databases
```
"[state] [industry] violations database"
"[state] department of [regulatory area] public records"
"[city] [industry] inspection database open data"
```

**Examples:**
- "New York restaurant violations database"
- "California Department of Environmental Health public records"
- "Los Angeles restaurant inspection database open data"

**What to Extract:**
- State/local specific databases not in federal systems
- City-level open data portals
- More granular local enforcement records

---

## CATEGORY B: Competitive Intelligence (4-5 Queries)

### Query 7: Pricing Data Extraction
```
"[platform] pricing data scraping tools"
"menu pricing extraction API [industry]"
"price comparison scraping [competitive site]"
```

**Examples:**
- "DoorDash pricing data scraping tools"
- "restaurant menu pricing extraction API"
- "Uber Eats price comparison scraping"

**What to Extract:**
- Scraping tools or services (Scrapy, Playwright, commercial APIs)
- Legal/ToS considerations for scraping
- Data structure (item name, price, platform)

---

### Query 8: Review Platform Data Access
```
"[review platform] API review data extraction"
"[platform] reviews bulk download"
"scraping [review site] business data"
```

**Examples:**
- "Yelp API review data extraction documentation"
- "Google Maps reviews bulk download tools"
- "scraping TripAdvisor business review data"

**What to Extract:**
- Official APIs (Google Places, Yelp Fusion)
- Review timestamp fields for velocity tracking
- Rating, text, user fields

---

### Query 9: Technology Stack Detection
```
"technology stack detection API"
"[tool] competitors technology tracking"
"website technology scraping service"
```

**Examples:**
- "BuiltWith API pricing technology detection"
- "Wappalyzer API competitors technology tracking"
- "website CMS detection scraping service"

**What to Extract:**
- Detection accuracy and coverage
- Technology categories (CMS, analytics, e-commerce platform)
- Pricing and API limits

---

### Query 10: Market Share & Competitive Positioning
```
"[industry] market share data sources"
"competitive intelligence [industry] data providers"
"[industry] company ranking database"
```

**Examples:**
- "restaurant delivery market share data sources"
- "competitive intelligence SaaS data providers"
- "fintech company ranking database"

**What to Extract:**
- Public vs. proprietary data sources
- Historical trends availability
- Geographic granularity (national, regional, city)

---

### Query 11: Industry Benchmarks
```
"[industry] benchmark data public"
"[metric] industry average [industry]"
"[industry] performance benchmarks database"
```

**Examples:**
- "restaurant revenue per square foot industry average"
- "SaaS churn rate benchmark data public"
- "hospital readmission rate benchmarks database"

**What to Extract:**
- Benchmark sources (trade associations, research firms)
- Segmentation (by company size, geography, sub-industry)
- Credibility of source

---

## CATEGORY C: Velocity Signals (4-5 Queries)

### Query 12: Review Velocity Tracking
```
"Google Maps API review data documentation"
"review velocity tracking tools [industry]"
"[platform] review timestamp extraction"
```

**Examples:**
- "Google Maps Places API review time field"
- "Yelp review velocity tracking tools restaurant"
- "TripAdvisor review timestamp extraction API"

**What to Extract:**
- Timestamp field format (UNIX, ISO, relative)
- Historical review limits (last 200, last year, etc.)
- Rate limits on API calls

---

### Query 13: Web Traffic Estimation
```
"website traffic estimation API"
"web traffic data providers"
"[tool] traffic analytics competitors"
```

**Examples:**
- "SimilarWeb API website traffic estimation"
- "Alexa web traffic data providers"
- "Semrush traffic analytics competitors API"

**What to Extract:**
- Accuracy levels (top sites vs. long tail)
- Granularity (monthly, daily)
- Cost and access restrictions

---

### Query 14: Hiring Velocity
```
"job posting API [job board]"
"company hiring velocity tracking"
"[platform] job listings scraping"
```

**Examples:**
- "LinkedIn job posting API documentation"
- "Indeed company hiring velocity tracking"
- "Greenhouse job listings API access"

**What to Extract:**
- Job posting fields (date posted, location, role)
- Historical data availability
- Scraping vs. API access options

---

### Query 15: Location Expansion Rate
```
"business location expansion tracking"
"[industry] new location database"
"store opening data [industry]"
```

**Examples:**
- "restaurant location expansion tracking data"
- "retail new store opening database"
- "franchise location growth data sources"

**What to Extract:**
- How locations are tracked (permits, business registrations)
- Address standardization and geocoding
- Date opened/closed fields

---

### Query 16: Social Media Growth Metrics
```
"[platform] follower growth API"
"social media analytics API [platform]"
"[platform] engagement rate tracking"
```

**Examples:**
- "Instagram follower growth API access"
- "Twitter analytics API rate limit"
- "LinkedIn company page engagement tracking"

**What to Extract:**
- Official API capabilities vs. third-party tools
- Historical data depth (how far back)
- Rate limits and authentication

---

## CATEGORY D: Tech/Operational Signals (3-4 Queries)

### Query 17: Technology Presence Detection
```
"detect [specific technology] on website"
"[tool] usage detection API"
"website using [platform] scraping"
```

**Examples:**
- "detect Shopify on website programmatically"
- "WordPress usage detection API"
- "websites using Stripe payment scraping"

**What to Extract:**
- Detection methods (HTML inspection, DNS, headers)
- Accuracy and false positive rates
- Automation options

---

### Query 18: Operational Signal Scraping
```
"[industry] operational metrics web scraping"
"extract [metric] from [site type]"
"[data point] extraction tools [industry]"
```

**Examples:**
- "restaurant hours of operation web scraping"
- "extract delivery radius from restaurant website"
- "parking availability extraction tools retail"

**What to Extract:**
- Data consistency across sites
- Scraping difficulty (structured vs. unstructured)
- Update frequency (static vs. dynamic)

---

### Query 19: Integration & Partnership Signals
```
"[platform] partner directory scraping"
"[integration] usage detection"
"[ecosystem] member list API"
```

**Examples:**
- "Salesforce AppExchange partner directory scraping"
- "Stripe integration usage detection"
- "Shopify app ecosystem member list API"

**What to Extract:**
- Public partner lists and directories
- Integration visibility (public badge, API partnership)
- Depth of integration (basic vs. advanced)

---

### Query 20: Compliance Documentation Signals
```
"[compliance standard] certification database"
"[certification] holder list public"
"[industry] compliance badge verification"
```

**Examples:**
- "SOC 2 certification verification database"
- "HIPAA compliance holder list public"
- "PCI DSS compliance badge verification"

**What to Extract:**
- Public certification directories
- Verification APIs
- Expiration date tracking

---

## Search Execution Best Practices

### Parallel Execution
- Run 15-20 queries simultaneously using multiple WebSearch calls
- Combine related queries: `WebSearch("[query 1] OR [query 2] OR [query 3]")`
- Prioritize queries most relevant to [Company]'s ICP

### Result Evaluation
For each search result, document:
1. **Database/API Name:** Official name and URL
2. **Fields Available:** Specific field names (not assumptions)
3. **Access Method:** Web portal, API, bulk download, scraping required
4. **Feasibility Rating:** HIGH, MEDIUM, LOW (see methodology.md)
5. **Update Frequency:** Daily, weekly, monthly, annual
6. **Cost:** Free, API credits, subscription required

### Handling "No Results"
If a query returns no relevant databases:
- Try adjacent industries (e.g., "food service" instead of "restaurant")
- Try federal vs. state level (e.g., EPA vs. state environmental agencies)
- Try alternative regulatory bodies (e.g., FDA vs. USDA)
- Document as "No data available" in Data Availability Report

### Red Flags to Skip
- Paid-only databases with no public access (e.g., Dun & Bradstreet proprietary scores)
- Aggregator sites with unclear primary sources
- Databases requiring account creation or "request demo" (not truly public)
- Soft signal sources (LinkedIn, Crunchbase, ZoomInfo)

---

## Data Availability Report Template

After executing 15-20 queries, synthesize findings into this format:

```
DATA AVAILABILITY REPORT FOR [COMPANY NAME]

GOVERNMENT DATA (HIGH feasibility sources):
1. [Database Name]
   - URL: [access point]
   - Fields: [actual field names]
   - Access: [API/portal/download]
   - Update: [frequency]
   - Feasibility: HIGH

2. [Database Name]
   - ...

COMPETITIVE INTELLIGENCE (HIGH/MEDIUM feasibility sources):
1. [Method/Tool]
   - Data points: [what can be extracted]
   - Tools: [scraping libs/APIs]
   - Legal: [ToS considerations]
   - Feasibility: MEDIUM

2. [Method/Tool]
   - ...

VELOCITY SIGNALS (HIGH feasibility sources):
1. [API/Platform]
   - Metrics: [review velocity, traffic, hiring]
   - Fields: [timestamp fields]
   - Limits: [rate limits, historical depth]
   - Feasibility: HIGH

2. [API/Platform]
   - ...

TECH/OPERATIONAL SIGNALS (MEDIUM feasibility sources):
1. [Detection Method]
   - Signals: [tech stack, integrations, compliance]
   - Detection: [method]
   - Feasibility: MEDIUM

---

REJECTED SOURCES (LOW feasibility or soft signals):
- [Source Name]: [reason for rejection]
- [Source Name]: [reason for rejection]

---

RECOMMENDED APPROACH:
- Tier 1 (Pure Government): [Y/N - explain]
- Tier 2 (Hybrid): [Y/N - explain which combinations]
- Tier 3 (Pure Competitive/Velocity): [Y/N - explain]

CONFIDENCE LEVEL FOR [COMPANY] USE CASE: [60-95%]
```

---

This template ensures systematic data discovery across all categories, feeding into the Sequential Thinking synthesis phase with ACTUAL available data sources (not assumptions).
