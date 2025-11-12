# Calculation Worksheets for Blueprint GTM Messages

Every data claim in a PQS or PVP message MUST include a calculation worksheet showing how the number was derived. This document provides templates and examples for all three data confidence tiers.

---

## Why Calculation Worksheets Matter

**The Blueprint Philosophy:** "Show your work, not just your answer."

Calculation worksheets serve three purposes:
1. **Credibility**: Prospects can verify your math instead of dismissing claims as "made up"
2. **Transparency**: Discloses confidence levels and data sources explicitly
3. **Non-obviousness**: Shows synthesis work that goes beyond Googling the company

**Rule:** If you can't build a calculation worksheet for a claim, don't make the claim.

---

## Tier 1: Pure Government Data Worksheets (90-95% Confidence)

Use this template when claims are derived ENTIRELY from government databases with record-level precision.

### Template: Tier 1 Calculation Worksheet

```
CALCULATION WORKSHEET: [Claim Description]

DATA SOURCE:
- Database: [Official name, e.g., EPA ECHO, OSHA Inspection Database]
- URL: [Direct link to database or record]
- Record ID: [Specific violation/inspection ID if applicable]
- Access Date: [Date data was retrieved]

CALCULATION:
Step 1: [First data point extraction]
  → Source: [Field name, e.g., "violation_date"]
  → Value: [Exact value from database]

Step 2: [Second data point extraction]
  → Source: [Field name, e.g., "penalty_amount"]
  → Value: [Exact value]

Step 3: [Mathematical operation]
  → Formula: [e.g., penalty_amount × compliance_multiplier]
  → Result: [Final number]

CONFIDENCE LEVEL: 90-95%
- Hard data: Record-level government enforcement data
- No estimation: All values directly from database fields
- Verifiable: Prospect can look up Record ID themselves

LIMITATIONS:
[Any caveats, e.g., "Penalty may be appealed, final amount subject to settlement"]
```

### Example 1: EPA Violation Penalty Calculation

```
CALCULATION WORKSHEET: "$47,500 Penalty for Clean Air Act Violation"

DATA SOURCE:
- Database: EPA Enforcement and Compliance History Online (ECHO)
- URL: https://echo.epa.gov/detailed-facility-report?fid=110000521987
- Record ID: CAA-05-2024-1234
- Access Date: November 8, 2025

CALCULATION:
Step 1: Identify violation record
  → Source: ECHO "Enforcement Actions" table, Field: "case_number"
  → Value: CAA-05-2024-1234 (Clean Air Act violation, March 15, 2024)

Step 2: Extract penalty amount
  → Source: ECHO "Penalties Assessed" field
  → Value: $47,500 (assessed penalty)

Step 3: Verify payment status
  → Source: ECHO "Case Status" field
  → Value: "Penalty Paid in Full" (June 1, 2024)

CONFIDENCE LEVEL: 95%
- Hard data: EPA enforcement record with case number
- No estimation: Penalty amount directly from database
- Verifiable: Prospect can search CAA-05-2024-1234 in ECHO

LIMITATIONS:
- This penalty is for a single violation; facility may have additional violations not yet resolved
- Penalty reflects violation severity as assessed by EPA Region 5
```

### Example 2: CMS Hospital Quality Rating

```
CALCULATION WORKSHEET: "2-Star CMS Quality Rating (Below State Average of 3.4 Stars)"

DATA SOURCE:
- Database: CMS Care Compare (Medicare.gov)
- URL: https://www.medicare.gov/care-compare/details/hospital/450123
- Facility ID: 450123
- Access Date: November 8, 2025

CALCULATION:
Step 1: Extract facility rating
  → Source: CMS "Overall Hospital Quality Star Rating" field
  → Value: 2 stars (updated October 2025)

Step 2: Extract state average
  → Source: CMS "State Average Star Rating" for Texas hospitals
  → Value: 3.4 stars (October 2025)

Step 3: Calculate gap
  → Formula: State Average - Facility Rating
  → Result: 3.4 - 2.0 = 1.4 stars below average

CONFIDENCE LEVEL: 95%
- Hard data: CMS official quality ratings, updated quarterly
- No estimation: Star ratings directly from Care Compare
- Verifiable: Prospect can search Facility ID 450123

LIMITATIONS:
- Star ratings lag by 1-2 quarters (reflects care delivered 12-18 months ago)
- Ratings may improve in next quarterly update (January 2026)
```

---

## Tier 2: Hybrid Approach Worksheets (60-75% Confidence)

Use this template when combining public data with reasonable estimations or competitive intelligence.

### Template: Tier 2 Calculation Worksheet

```
CALCULATION WORKSHEET: [Claim Description]

DATA SOURCES:
1. [Primary source - government/public data]
   - URL: [link]
   - Field: [specific field name]
   - Value: [extracted value]

2. [Secondary source - competitive intel or estimation]
   - Method: [scraping, API, manual research]
   - Source: [platform, e.g., Yelp, DoorDash, Google Maps]
   - Access Date: [date]

CALCULATION:
Step 1: [Extract hard data point]
  → Source: [database/API]
  → Value: [exact value]

Step 2: [Extract estimated data point]
  → Source: [competitive site, review platform]
  → Value: [estimated value]
  → Confidence: [60-75%]
  → Reasoning: [why this estimation is reasonable]

Step 3: [Combine data points]
  → Formula: [mathematical operation]
  → Result: [final number]

CONFIDENCE LEVEL: 60-75%
- Hard data: [which parts are verifiable]
- Estimation: [which parts are estimated, with disclosed method]
- Hedged language: [how claim is worded to reflect uncertainty]

LIMITATIONS:
[Specific caveats about data quality, estimation method, or time lag]
```

### Example 3: Menu Pricing Arbitrage

```
CALCULATION WORKSHEET: "Estimated $4,200/Month Revenue Leak from DoorDash Pricing Mismatch"

DATA SOURCES:
1. Your Restaurant's Website Menu
   - URL: https://yourrestaurant.com/menu
   - Method: Manual pricing extraction
   - Access Date: November 8, 2025

2. DoorDash Pricing Data
   - URL: https://doordash.com/store/your-restaurant
   - Method: Manual pricing extraction
   - Access Date: November 8, 2025

3. Order Volume Estimation
   - Source: Yelp review velocity + industry benchmarks
   - Method: See "Order Volume Estimation" section below

CALCULATION:
Step 1: Identify pricing discrepancies
  → Source: Website menu vs. DoorDash menu (top 10 items)
  → Average Price Gap: $2.15 per item (DoorDash lower than website)
  → Confidence: 95% (hard data from public menus)

Step 2: Estimate monthly DoorDash order volume
  → Source: Yelp review velocity (18 reviews in last 30 days)
  → Industry Benchmark: 1 review per 50 orders (Source: Toast Restaurant Success Report 2024)
  → Estimated Monthly Orders: 18 × 50 = 900 orders
  → Confidence: 60% (estimation based on industry benchmark)

Step 3: Calculate revenue leak
  → Formula: Price Gap × Estimated Monthly Orders
  → Result: $2.15 × 900 = $1,935/month
  → But: Accounts for only top 10 items (estimated 65% of total orders)
  → Adjusted Result: $1,935 ÷ 0.65 = $2,977/month
  → Conservative Multiplier: Add 40% for items not tracked
  → Final Estimate: $2,977 × 1.4 = $4,168/month ≈ $4,200/month

CONFIDENCE LEVEL: 65%
- Hard data: Menu pricing gap ($2.15 average) is verifiable
- Estimation: Order volume based on review velocity + industry benchmark
- Hedged language: "Estimated $4,200/month" (not "$4,200/month")

LIMITATIONS:
- Review velocity may not perfectly correlate with order volume for this specific restaurant
- Price gaps may be intentional (reflecting DoorDash commission structure)
- Does not account for seasonal fluctuations in order volume

ORDER VOLUME ESTIMATION DETAIL:
Source: Yelp API (https://www.yelp.com/biz/your-restaurant)
- Reviews in last 30 days: 18 reviews
- Review Rate Assumption: 1 review per 50 orders (Toast 2024 data, page 47)
- Calculation: 18 ÷ (1/50) = 900 estimated monthly orders
```

### Example 4: Review Velocity + Traffic Surge

```
CALCULATION WORKSHEET: "185% Review Velocity Increase (Jan-Oct 2025) Signals 3x Traffic Growth"

DATA SOURCES:
1. Google Maps Review Timestamps
   - URL: https://maps.google.com/place/your-business
   - Method: Google Places API (review.time field)
   - Access Date: November 8, 2025

2. Industry Benchmark (Review-to-Visit Ratio)
   - Source: BrightLocal "Local Consumer Review Survey 2024"
   - URL: https://www.brightlocal.com/research/review-survey-2024
   - Page: 23 (Chart: "How Often Consumers Leave Reviews")

CALCULATION:
Step 1: Extract review velocity (Jan-May 2025 baseline)
  → Source: Google Places API, filter: review.time >= 2025-01-01 AND review.time <= 2025-05-31
  → Result: 47 reviews over 5 months = 9.4 reviews/month (baseline)

Step 2: Extract review velocity (Jun-Oct 2025 recent)
  → Source: Google Places API, filter: review.time >= 2025-06-01 AND review.time <= 2025-10-31
  → Result: 134 reviews over 5 months = 26.8 reviews/month (recent)

Step 3: Calculate velocity increase
  → Formula: (Recent - Baseline) ÷ Baseline × 100%
  → Result: (26.8 - 9.4) ÷ 9.4 × 100% = 185% increase

Step 4: Estimate traffic multiplier from review velocity
  → Industry Benchmark: 1 review per 20 visits (BrightLocal 2024, p. 23)
  → Assumption: Review-to-visit ratio remains constant
  → Traffic Multiplier: 26.8 ÷ 9.4 = 2.85x ≈ 3x traffic growth

CONFIDENCE LEVEL: 70%
- Hard data: Review timestamps from Google API (95% confidence)
- Estimation: Traffic multiplier assumes constant review-to-visit ratio (60% confidence)
- Hedged language: "Signals 3x traffic growth" (not "You have 3x traffic growth")

LIMITATIONS:
- Review velocity may be influenced by factors other than traffic (e.g., review solicitation campaigns)
- Industry benchmark may not apply to this specific business type
- Does not account for seasonal patterns (e.g., summer tourism surge)
```

---

## Tier 3: Pure Competitive/Velocity Worksheets (50-70% Confidence)

Use this template when NO government data is available and claims rely entirely on competitive intelligence or velocity signals.

### Template: Tier 3 Calculation Worksheet

```
CALCULATION WORKSHEET: [Claim Description]

DATA SOURCES:
1. [Competitive platform data]
   - Platform: [e.g., G2, Capterra, App Store]
   - URL: [link]
   - Method: [scraping, API, manual]
   - Access Date: [date]

2. [Estimation methodology]
   - Benchmark Source: [industry report, academic study]
   - Assumption: [key assumption being made]
   - Confidence: [50-70%]

CALCULATION:
Step 1: [Extract competitive data]
  → Source: [platform]
  → Value: [scraped/extracted value]
  → Confidence: [70-80% - data is public but not official]

Step 2: [Apply estimation method]
  → Benchmark: [industry average or proxy metric]
  → Formula: [how benchmark is applied]
  → Result: [estimated value]
  → Confidence: [50-60% - estimation layer]

Step 3: [Synthesize final claim]
  → Combined Confidence: [overall 50-70%]
  → Hedging: [how language reflects uncertainty]

CONFIDENCE LEVEL: 50-70%
- Competitive data: [describe data quality]
- Heavy estimation: [acknowledge estimation layers]
- Transparent methodology: [disclose all assumptions]

LIMITATIONS:
[Be very explicit about what could make this estimate wrong]
```

### Example 5: SaaS Pricing Comparison

```
CALCULATION WORKSHEET: "Your Competitor's Pricing Is 22% Lower for Comparable Feature Set"

DATA SOURCES:
1. Your Company's Pricing Page
   - URL: https://yourcompany.com/pricing
   - Plan: Professional ($99/user/month)
   - Features: 10 integrations, 50GB storage, SSO
   - Access Date: November 8, 2025

2. Competitor's Pricing Page
   - URL: https://competitor.com/pricing
   - Plan: Business ($77/user/month)
   - Features: 12 integrations, 50GB storage, SSO, API access
   - Access Date: November 8, 2025

CALCULATION:
Step 1: Extract base pricing
  → Your Pricing: $99/user/month (Professional plan)
  → Competitor Pricing: $77/user/month (Business plan)
  → Price Difference: $99 - $77 = $22/user/month

Step 2: Normalize for feature parity
  → Your Features: 10 integrations, 50GB storage, SSO
  → Competitor Features: 12 integrations, 50GB storage, SSO, API access
  → Assessment: Competitor offers MORE features at lower price
  → Adjustment: None needed (competitor advantage is even greater)

Step 3: Calculate percentage difference
  → Formula: (Your Price - Competitor Price) ÷ Your Price × 100%
  → Result: ($99 - $77) ÷ $99 × 100% = 22% lower

CONFIDENCE LEVEL: 70%
- Hard data: Pricing is public on both websites (90% confidence)
- Estimation: Feature parity assessment is subjective (60% confidence)
- Hedged language: "22% lower for comparable feature set" (acknowledges subjectivity)

LIMITATIONS:
- Pricing may not reflect actual contract rates (discounts, volume pricing not public)
- Feature comparison is simplified (some features may not be directly comparable)
- Does not account for hidden costs (implementation, support, add-ons)
- Competitor pricing could change without notice
```

### Example 6: App Store Rating Decline

```
CALCULATION WORKSHEET: "Your App Store Rating Declined from 4.2 to 3.1 Stars (73% of Reviews Since June Mention 'Crashing')"

DATA SOURCES:
1. iOS App Store Review Data
   - App: [Your Company App]
   - URL: https://apps.apple.com/app/id123456789
   - Method: Manual scraping (App Store does not provide official API)
   - Access Date: November 8, 2025

2. Review Content Analysis
   - Method: Manual keyword search for "crash," "crashing," "freezes"
   - Sample Size: 200 most recent reviews (June-Nov 2025)
   - Access Date: November 8, 2025

CALCULATION:
Step 1: Extract historical rating (Jan-May 2025)
  → Source: Wayback Machine snapshot of App Store page (May 31, 2025)
  → URL: https://web.archive.org/web/20250531/[app store URL]
  → Rating: 4.2 stars (based on 1,847 reviews)

Step 2: Extract current rating (November 2025)
  → Source: Live App Store page
  → Rating: 3.1 stars (based on 2,403 reviews)
  → Rating Decline: 4.2 - 3.1 = 1.1 stars

Step 3: Analyze recent review content (June-Nov 2025)
  → Sample: 200 most recent reviews
  → Keyword Search: "crash," "crashing," "freezes," "won't load"
  → Reviews Mentioning Keywords: 146 out of 200
  → Percentage: 146 ÷ 200 = 73%

CONFIDENCE LEVEL: 60%
- Hard data: Current rating is verifiable (80% confidence)
- Estimation: Historical rating from Wayback Machine snapshot (70% confidence)
- Manual scraping: Keyword analysis is manual, not automated (50% confidence)
- Hedged language: "73% of reviews mention 'crashing'" (not "73% of users experience crashes")

LIMITATIONS:
- Historical rating based on Wayback Machine snapshot (may not be perfectly accurate)
- Manual scraping is error-prone (could have missed reviews or misclassified keywords)
- Keyword search is simplistic (does not account for context, sarcasm, or negations like "NOT crashing")
- Sample size of 200 reviews may not be representative of all 2,403 reviews
- Does not prove causation (rating decline could be due to other factors beyond crashes)
```

---

## Best Practices for All Tiers

### 1. Always Include:
- **Data Source URL**: Must be a working link the prospect can verify
- **Access Date**: Data can change; timestamp when you retrieved it
- **Confidence Level**: 50-95% range with clear reasoning
- **Limitations**: What could make your estimate wrong

### 2. Hedge Language by Tier:
- **Tier 1 (90-95%)**: Direct statements ("Your facility received a $47,500 penalty...")
- **Tier 2 (60-75%)**: Estimated language ("Based on menu pricing analysis, I estimate...")
- **Tier 3 (50-70%)**: Heavy hedging ("Industry benchmarks suggest..." / "Competitive analysis indicates...")

### 3. Show Multiple Steps:
- Don't jump straight to the final number
- Break down into 3-5 intermediate steps
- Cite sources for each step

### 4. Disclose Assumptions:
- If you assume a review-to-visit ratio, state it explicitly
- If you use an industry benchmark, cite the report (with page number)
- If you estimate order volume, explain the methodology

### 5. Make It Verifiable:
- Provide Record IDs for government databases
- Link to specific competitor pricing pages
- Include timestamps for scraped data
- Reference exact field names from databases

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Vague Data Sources

**Bad:**
```
DATA SOURCE: EPA database
```

**Good:**
```
DATA SOURCE:
- Database: EPA Enforcement and Compliance History Online (ECHO)
- URL: https://echo.epa.gov/detailed-facility-report?fid=110000521987
- Record ID: CAA-05-2024-1234
- Field: "Penalties Assessed" = $47,500
```

### ❌ Mistake 2: Missing Calculation Steps

**Bad:**
```
CALCULATION:
Your DoorDash pricing is costing you $4,200/month.
```

**Good:**
```
CALCULATION:
Step 1: Menu price gap = $2.15/item (website vs. DoorDash)
Step 2: Estimated monthly orders = 900 (Yelp review velocity × 50)
Step 3: Revenue leak = $2.15 × 900 × 1.4 adjustment = $4,200/month
```

### ❌ Mistake 3: Overstating Confidence

**Bad:**
```
CONFIDENCE LEVEL: 95%
- Based on review velocity and traffic estimates
```

**Good:**
```
CONFIDENCE LEVEL: 65%
- Hard data: Review timestamps (95% confidence)
- Estimation: Traffic multiplier assumption (60% confidence)
- Combined: 65% confidence due to estimation layer
```

### ❌ Mistake 4: No Limitations Section

**Bad:**
```
[No limitations disclosed]
```

**Good:**
```
LIMITATIONS:
- Historical rating from Wayback Machine (may have archival gaps)
- Manual scraping subject to human error
- Keyword search does not account for context or sarcasm
```

---

## Calculation Worksheet Checklist

Before including a calculation worksheet in a message, verify:

- [ ] Data source URL is included and working
- [ ] Access date is specified
- [ ] Calculation has 3+ intermediate steps (not just final number)
- [ ] Each step cites a specific source or field name
- [ ] Confidence level is stated (50-95%) with reasoning
- [ ] Limitations are explicitly disclosed
- [ ] Language hedging matches confidence level (Tier 1 = direct, Tier 3 = heavy hedging)
- [ ] Prospect can replicate your work by following the worksheet
- [ ] No unsupported leaps (every number is traceable to a source)
- [ ] Assumptions are stated explicitly, not hidden

---

## Integration with Messages

Calculation worksheets appear in two places:

### 1. Inline (Brief Version)
In the message body, include a 2-3 line calculation teaser:

**Example (PQS Message):**
```
Your DoorDash menu pricing is $2.15/item lower than your website on average.
With an estimated 900 monthly DoorDash orders, this represents approximately
$4,200/month in lost revenue. [See calculation worksheet below]
```

### 2. Appendix (Full Version)
At the end of the message, include the complete calculation worksheet:

**Example:**
```
---

CALCULATION WORKSHEET: Menu Pricing Revenue Leak

[Full worksheet with all steps, sources, confidence levels, limitations]
```

---

## When NOT to Include a Calculation Worksheet

Skip the worksheet for:
- **Qualitative claims**: "Your website loads slowly" (no number to calculate)
- **Common knowledge**: "Part 135 operators require A&P mechanics" (no calculation needed)
- **Directional statements**: "Your review velocity is increasing" (trend, not specific number)

But if you make a quantitative claim ("Your website loads 4.2 seconds slower than competitors"), you MUST include a worksheet.

---

## Examples by Industry

### Healthcare (Tier 1)
- CMS quality star ratings
- Hospital readmission rate calculations
- Medicare penalty assessments
- State inspection violation counts

### Manufacturing (Tier 1)
- EPA emissions violations
- OSHA citation penalty totals
- Permit expiration date tracking
- Consent decree milestone compliance

### Food Service (Tier 2)
- Menu pricing arbitrage calculations
- Health inspection score trends
- Review velocity + traffic estimation
- Delivery platform commission analysis

### SaaS (Tier 3)
- Competitor pricing comparisons
- G2/Capterra rating trend analysis
- Feature parity assessments
- App store review sentiment analysis

---

## References

**Industry Benchmarks:**
- Toast Restaurant Success Report 2024: https://pos.toasttab.com/restaurant-success-report
- BrightLocal Review Survey 2024: https://www.brightlocal.com/research/review-survey-2024
- Gartner SaaS Pricing Analysis 2024: [proprietary, cite if accessible]

**Government Databases:**
- EPA ECHO: https://echo.epa.gov/
- OSHA Inspection Database: https://www.osha.gov/pls/imis/establishment.html
- CMS Care Compare: https://www.medicare.gov/care-compare/
- FAA Safety Data: https://www.faa.gov/data_research/

**Competitive Intelligence Tools:**
- Google Places API: https://developers.google.com/maps/documentation/places/web-service/overview
- Yelp Fusion API: https://www.yelp.com/developers/documentation/v3
- BuiltWith API: https://api.builtwith.com/

---

**Version:** 1.0.0 (November 2025)

**Related Documentation:**
- [methodology.md](./methodology.md) - Buyer critique rubric, Texada Test
- [data-discovery-queries.md](./data-discovery-queries.md) - Search query templates
- [common-databases.md](../references/common-databases.md) - Industry database catalog
