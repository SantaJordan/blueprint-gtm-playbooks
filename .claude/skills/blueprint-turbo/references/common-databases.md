# Common Government & Public Databases for Blueprint GTM

This catalog provides industry-specific database references for Wave 2: Multi-Modal Data Discovery. Use these as starting points for finding pain-qualified segments backed by government data.

---

## How to Use This Catalog

**During Wave 2 Data Discovery:**
1. Identify the target company's industry
2. Reference the relevant section below
3. Execute search queries from [data-discovery-queries.md](../prompts/data-discovery-queries.md)
4. Document actual field names and access methods in your Data Availability Report
5. Use HIGH feasibility sources for Tier 1 segments

**Field Name Documentation:**
For each database, we provide:
- **Database Name & URL**: Official access point
- **Key Fields**: Actual field names (not assumptions)
- **Access Method**: Web portal, API, bulk download, or scraping required
- **Update Frequency**: How often data is refreshed
- **Feasibility Rating**: HIGH (ready to use), MEDIUM (requires work), LOW (avoid)

---

## Healthcare & Medical Facilities

### 1. CMS Care Compare (Hospital Quality Ratings)

**URL:** https://www.medicare.gov/care-compare/

**Purpose:** Medicare quality star ratings, hospital readmission rates, patient safety scores

**Key Fields:**
- `provider_id` (6-digit facility identifier, e.g., "450123")
- `hospital_overall_rating` (1-5 stars)
- `hospital_type` ("Acute Care Hospital", "Critical Access Hospital")
- `readmission_national_comparison` ("Above", "Same as", "Below" national average)
- `mortality_national_comparison` ("Above", "Same as", "Below" national average)
- `safety_of_care_national_comparison` ("Above", "Same as", "Below" national average)
- `patient_experience_national_comparison_footnote` (HCAHPS score context)

**Access Method:**
- Web Portal: Search by facility name or zip code
- API: CMS Data API (https://data.cms.gov/provider-data/)
- Bulk Download: CSV files available monthly

**Update Frequency:** Quarterly (January, April, July, October)

**Feasibility:** HIGH - Direct API access, field-level data, updated quarterly

**Example Query:**
```
SELECT provider_id, hospital_name, hospital_overall_rating, state
FROM cms_care_compare
WHERE state = 'TX' AND hospital_overall_rating <= 2
```

**Pain Segment Use Cases:**
- Hospitals with <3 stars (quality improvement pressure)
- Facilities "Above" national average on readmission rates (CMS penalty risk)
- Critical Access Hospitals with declining patient experience scores

---

### 2. CMS Nursing Home Compare

**URL:** https://www.medicare.gov/care-compare/

**Purpose:** Nursing home quality ratings, staffing levels, inspection violations

**Key Fields:**
- `federal_provider_number` (6-digit facility ID)
- `overall_rating` (1-5 stars)
- `health_inspection_rating` (1-5 stars)
- `staffing_rating` (1-5 stars)
- `quality_measure_rating` (1-5 stars)
- `total_number_of_health_deficiencies` (count of violations)
- `total_weighted_health_survey_score` (severity-weighted violation score)
- `registered_nurse_staffing_hours_per_resident_per_day`
- `reported_nurse_aide_staffing_hours_per_resident_per_day`

**Access Method:**
- Web Portal: Search by facility name or location
- API: CMS Data API
- Bulk Download: Monthly CSV files

**Update Frequency:** Monthly

**Feasibility:** HIGH - Comprehensive data, monthly updates, direct API

**Pain Segment Use Cases:**
- Facilities with <3 overall stars (referral risk, family scrutiny)
- Nursing homes with staffing ratings <3 (turnover, compliance issues)
- Facilities with 10+ health deficiencies in last inspection

---

### 3. State Health Department Inspection Databases

**Example: California CDPH Healthcare Facility Search**
**URL:** https://www.cdph.ca.gov/Programs/CHCQ/LCP/Pages/Search.aspx

**Purpose:** State-level facility inspections, complaint investigations, enforcement actions

**Key Fields (California):**
- `facility_number` (unique state ID)
- `inspection_date`
- `inspection_type` ("Complaint Investigation", "Routine Survey", "Follow-up")
- `deficiency_tag` (federal deficiency code, e.g., "F689" for infection control)
- `scope_severity` ("A" to "L", where "J"+ = immediate jeopardy)
- `plan_of_correction_date`
- `revisit_required` (yes/no)

**Access Method:**
- Web Portal: Facility-by-facility search
- API: Limited or none (varies by state)
- Bulk Download: Some states provide quarterly reports

**Update Frequency:** Weekly to monthly (varies by state)

**Feasibility:** MEDIUM - Data exists but access methods vary by state

**Pain Segment Use Cases:**
- Facilities with "Immediate Jeopardy" findings (scope/severity J-L)
- Repeat deficiencies (same tag cited in multiple inspections)
- Complaint investigations with substantiated findings

**State-by-State Resources:**
- **California:** https://www.cdph.ca.gov/Programs/CHCQ/LCP/Pages/Search.aspx
- **Texas:** https://www.hhs.texas.gov/doing-business-hhs/provider-portals/health-facilities-regulation
- **Florida:** https://www.ahca.myflorida.com/MCHQ/Health_Facility_Regulation/index.shtml
- **New York:** https://health.data.ny.gov/Health/Health-Facility-General-Information/vn5v-hh5r

---

## Environmental & Manufacturing

### 4. EPA ECHO (Enforcement & Compliance History Online)

**URL:** https://echo.epa.gov/

**Purpose:** Environmental violations, penalties, permits, inspections for facilities

**Key Fields:**
- `registry_id` (unique facility ID)
- `frs_id` (Facility Registry Service ID)
- `enforcement_action_id` (specific case number, e.g., "CAA-05-2024-1234")
- `violation_type` ("Clean Air Act", "Clean Water Act", "RCRA", "TSCA")
- `violation_date`
- `penalty_amount` (dollars assessed)
- `case_status` ("Penalty Paid", "Under Appeal", "Settlement Reached")
- `nc_status` ("In Noncompliance", "Compliance Schedule", "In Compliance")
- `formal_enforcement_action_count` (number of formal actions in last 5 years)
- `informal_enforcement_action_count`
- `permit_expiration_date`

**Access Method:**
- Web Portal: Search by facility name, location, or ID
- API: ECHO API (https://echo.epa.gov/tools/web-services)
- Bulk Download: CSV exports available

**Update Frequency:** Weekly

**Feasibility:** HIGH - Excellent API, comprehensive data, weekly updates

**Example Query:**
```
GET https://echo.epa.gov/facilities/facility-search
?p_fa=Y (formal enforcement actions)
&p_pv=Y (permit violations)
&p_st=TX (state filter)
&responseset=facility_details
```

**Pain Segment Use Cases:**
- Facilities with formal enforcement actions in last 12 months
- Sites with permits expiring in next 90 days
- Manufacturers in noncompliance status (nc_status = "In Noncompliance")

---

### 5. OSHA Inspection Database

**URL:** https://www.osha.gov/pls/imis/establishment.html

**Purpose:** Workplace safety inspections, violations, citations, penalties

**Key Fields:**
- `establishment_name`
- `inspection_number` (unique case ID)
- `inspection_open_date`
- `inspection_close_date`
- `inspection_type` ("Complaint", "Accident", "Programmed", "Referral")
- `citation_id`
- `citation_type` ("Serious", "Willful", "Repeat", "Other-than-Serious")
- `standard_violated` (OSHA regulation code, e.g., "1910.147" for lockout/tagout)
- `initial_penalty` (dollars assessed)
- `current_penalty` (after reductions/settlements)
- `abatement_date` (deadline to fix violation)
- `contested` (yes/no)

**Access Method:**
- Web Portal: Establishment search form
- API: Limited (OSHA Data & Statistics page has CSVs)
- Bulk Download: Quarterly data files available

**Update Frequency:** Monthly

**Feasibility:** HIGH - Searchable database, quarterly bulk files

**Pain Segment Use Cases:**
- Facilities with "Serious" or "Willful" citations in last 12 months
- Repeat violations of same standard (indicates systemic issue)
- High penalty amounts (>$50K suggests significant hazards)

---

### 6. State Environmental Agency Databases

**Example: Texas TCEQ (Texas Commission on Environmental Quality)**
**URL:** https://www15.tceq.texas.gov/crpub/

**Purpose:** State-level permits, violations, enforcement actions (supplements EPA)

**Key Fields (Texas):**
- `regulated_entity_number` (RN number, unique state ID)
- `permit_number`
- `permit_type` ("Air Quality", "Waste Management", "Water Quality")
- `permit_status` ("Active", "Expired", "Under Review")
- `violation_date`
- `enforcement_order_number`
- `penalty_amount`
- `compliance_due_date`

**Access Method:**
- Web Portal: Central Registry search
- API: Limited
- Bulk Download: Some data available via Texas Open Data Portal

**Update Frequency:** Weekly to monthly

**Feasibility:** MEDIUM - Data exists but portals vary by state

**State-by-State Resources:**
- **Texas:** https://www15.tceq.texas.gov/crpub/
- **California:** https://calepa.ca.gov/enforcement/
- **Illinois:** https://www.epa.illinois.gov/topics/compliance-enforcement.html
- **Pennsylvania:** https://www.dep.pa.gov/DataandTools/Pages/Compliance-and-Enforcement.aspx

---

## Food Service & Restaurants

### 7. Local Health Department Restaurant Inspections

**Example: Los Angeles County Restaurant Inspections**
**URL:** https://ehservices.publichealth.lacounty.gov/

**Purpose:** Health code violations, inspection scores, closure orders

**Key Fields (LA County):**
- `facility_id` (unique health permit ID)
- `facility_name`
- `inspection_date`
- `inspection_score` (0-100, where 90+ = "A" grade)
- `grade` ("A", "B", "C", or "Closed")
- `violation_code` (e.g., "1A" = vermin infestation, "7" = hot/cold holding temps)
- `violation_description`
- `violation_severity` ("Major", "Minor")
- `closure_reason` (if applicable)
- `reinspection_required` (yes/no)

**Access Method:**
- Web Portal: Facility search by name or address
- API: LA County provides JSON API
- Bulk Download: Some jurisdictions provide monthly CSVs

**Update Frequency:** Daily to weekly (varies by jurisdiction)

**Feasibility:** HIGH for major cities, MEDIUM for rural areas

**Example Query (LA County API):**
```
GET http://publichealth.lacounty.gov/eh/api/facilitySearch
?facilityName=Restaurant+Name
&format=json
```

**Pain Segment Use Cases:**
- Restaurants with scores <85 (B or C grade = customer scrutiny)
- Facilities with "Major" violations (health hazards)
- Restaurants with recent closure orders (reputational damage)

**Major City Resources:**
- **Los Angeles:** https://ehservices.publichealth.lacounty.gov/
- **New York City:** https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j
- **Chicago:** https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5
- **San Francisco:** https://data.sfgov.org/Health-and-Social-Services/Restaurant-Scores-LIVES-Standard/pyih-qa8i

---

### 8. State Licensing Boards (Food Service)

**Example: Florida DBPR (Dept. of Business & Professional Regulation)**
**URL:** https://www.myfloridalicense.com/intentions2.asp

**Purpose:** License status, disciplinary actions, administrative complaints

**Key Fields (Florida):**
- `license_number`
- `license_type` ("Food Service", "Mobile Food Dispensing Vehicle")
- `license_status` ("Active", "Delinquent", "Inactive", "Expired")
- `expiration_date`
- `complaint_number` (if disciplinary action taken)
- `complaint_date`
- `violation_description`
- `fine_amount`
- `license_suspension_dates`

**Access Method:**
- Web Portal: License verification search
- API: Limited
- Bulk Download: Some states provide monthly files

**Update Frequency:** Weekly

**Feasibility:** MEDIUM - Data exists but portals vary by state

**Pain Segment Use Cases:**
- Facilities with "Delinquent" license status (compliance risk)
- Restaurants with recent disciplinary actions (fines, suspensions)
- Licenses expiring in next 30 days (renewal process pain)

---

## Transportation & Logistics

### 9. FMCSA SAFER (Federal Motor Carrier Safety Administration)

**URL:** https://safer.fmcsa.dot.gov/

**Purpose:** Trucking company safety ratings, violations, inspections, crashes

**Key Fields:**
- `usdot_number` (unique carrier ID)
- `mc_mx_ff_number` (operating authority number)
- `safety_rating` ("Satisfactory", "Conditional", "Unsatisfactory")
- `out_of_service_date` (if shut down)
- `mcs_150_form_date` (last biennial update)
- `total_power_units` (number of trucks)
- `total_drivers`
- `inspection_total` (last 24 months)
- `out_of_service_percent` (vehicles/drivers placed out of service)
- `crash_total` (last 24 months)
- `fatal_crash` (count)
- `injury_crash` (count)
- `hazmat_inspections`
- `vehicle_maintenance_violation_rate`
- `unsafe_driving_violation_rate`
- `hos_compliance_violation_rate` (hours of service)

**Access Method:**
- Web Portal: Company search by name or USDOT number
- API: FMCSA Web Services (https://mobile.fmcsa.dot.gov/developer/)
- Bulk Download: Census files available monthly

**Update Frequency:** Daily (inspections), Monthly (safety ratings)

**Feasibility:** HIGH - Excellent API, comprehensive data

**Example Query:**
```
GET https://mobile.fmcsa.dot.gov/qc/services/carriers/{usdot_number}
?webKey=YOUR_API_KEY
```

**Pain Segment Use Cases:**
- Carriers with "Conditional" or "Unsatisfactory" safety ratings
- Companies with out-of-service rates >10% (indicates systemic issues)
- Fleets with overdue MCS-150 updates (compliance deadlines)
- Carriers with increasing crash rates year-over-year

---

### 10. FAA Part 135 Certificate Holders (Air Carrier)

**URL:** https://av-info.faa.gov/

**Purpose:** Air carrier operating certificates, aircraft registrations, airworthiness

**Key Fields:**
- `certificate_number` (e.g., "ABCD1234")
- `operator_name`
- `certificate_type` ("Part 135 On-Demand", "Part 121 Scheduled")
- `operation_specifications` (authorized operations)
- `aircraft_count`
- `tail_number` (N-number for each aircraft)
- `aircraft_make_model`
- `year_manufactured`
- `airworthiness_certificate_date`
- `registration_expiration_date`

**Access Method:**
- Web Portal: FAA Registry search
- API: Limited (some data via FAA Data & Research portal)
- Bulk Download: Aircraft registry releasable database (monthly)

**Update Frequency:** Monthly (registry), Quarterly (certificates)

**Feasibility:** MEDIUM - Data exists but requires multiple lookups

**Pain Segment Use Cases:**
- Operators with mixed fleet (multiple aircraft types = maintenance complexity)
- Carriers with aircraft nearing airworthiness renewal (compliance deadlines)
- Part 135 operators with aging fleet (high maintenance burden)

**Note:** FAA data shows WHO operates WHAT aircraft, but NOT operational pain points (no violation database for maintenance tracking).

---

## Technology & SaaS

**Important:** Technology/SaaS industries have ZERO government database coverage. No EPA, OSHA, CMS, FDA equivalents exist for software companies.

**Available Data Sources (All Tier 3):**

### 11. G2 Reviews & Ratings

**URL:** https://www.g2.com/

**Purpose:** User reviews, ratings, feature satisfaction scores

**Accessible Data:**
- Overall star rating (out of 5)
- Number of reviews
- Category rankings ("Leader", "High Performer", "Niche")
- Individual review text and ratings
- Feature satisfaction scores (e.g., "Ease of Use: 8.5/10")

**Access Method:**
- Web Scraping: Manual or automated (no official API for reviews)
- Manual Research: Read reviews for qualitative insights

**Update Frequency:** Real-time (reviews added continuously)

**Feasibility:** MEDIUM - Scraping required, no official API

**Pain Segment Use Cases:**
- Products with declining ratings (e.g., 4.5 → 3.8 over 12 months)
- Software with low "Ease of Use" scores (<7/10)
- Tools with high "Likelihood to Recommend" drop-off

**Confidence Level:** 50-70% (competitive intelligence, not government data)

---

### 12. BuiltWith / Wappalyzer (Technology Stack Detection)

**URL:** https://builtwith.com/ | https://www.wappalyzer.com/

**Purpose:** Detect what technologies a website uses (CMS, analytics, e-commerce platform)

**Accessible Data:**
- CMS platform (WordPress, Shopify, custom)
- Analytics tools (Google Analytics, Mixpanel)
- Payment processors (Stripe, PayPal)
- Marketing tools (HubSpot, Marketo)
- Hosting provider (AWS, Azure, self-hosted)

**Access Method:**
- API: BuiltWith API (paid), Wappalyzer API (paid)
- Manual: Browser extension for individual site checks

**Update Frequency:** Real-time (on-demand checks)

**Feasibility:** MEDIUM - Requires paid API for scale

**Pain Segment Use Cases:**
- Companies using outdated CMS (e.g., Drupal 7 EOL)
- Sites without HTTPS (security vulnerability)
- Businesses using legacy payment processors (PCI compliance risk)

**Confidence Level:** 70-80% (detection is accurate but doesn't prove pain)

---

## Education

### 13. State Department of Education School Performance Data

**Example: Texas Academic Performance Reports (TAPR)**
**URL:** https://rptsvr1.tea.texas.gov/perfreport/tapr/

**Purpose:** School ratings, test scores, accountability statuses

**Key Fields (Texas):**
- `campus_id` (unique school ID)
- `accountability_rating` ("A", "B", "C", "D", "F")
- `state_percentile` (e.g., "35th percentile in state")
- `student_achievement_score` (0-100)
- `school_progress_score` (0-100)
- `closing_the_gaps_score` (equity measure)
- `distinction_designations` (count of special recognitions)

**Access Method:**
- Web Portal: School-by-school lookup
- Bulk Download: CSV files available annually

**Update Frequency:** Annually (released each December)

**Feasibility:** HIGH - Comprehensive data, consistent structure

**Pain Segment Use Cases:**
- Schools with "D" or "F" accountability ratings (improvement pressure)
- Campuses in the bottom quartile of state percentile rankings
- Schools with declining progress scores year-over-year

---

## Financial Services & Insurance

**Important:** Financial services have regulatory data, but it's often NOT public due to privacy laws.

### 14. FINRA BrokerCheck

**URL:** https://brokercheck.finra.org/

**Purpose:** Broker/advisor disciplinary history, registrations, disclosures

**Accessible Data:**
- Registration status (active, inactive, expelled)
- Firm affiliations
- Disciplinary events (customer complaints, regulatory actions)
- Disclosure details (settlements, arbitrations)

**Access Method:**
- Web Portal: Individual lookup by name or CRD number
- API: None (manual research required)

**Update Frequency:** Real-time

**Feasibility:** MEDIUM - Manual lookup only, no bulk access

**Pain Segment Use Cases:**
- Advisors with recent disciplinary actions (compliance issues)
- Brokers with multiple customer complaints (reputational risk)
- Firms with high advisor turnover (check registration changes)

**Confidence Level:** 90% (government data) but LOW feasibility (manual only)

---

## Real Estate & Property Management

### 15. Local Building Department Violations

**Example: NYC Housing Maintenance Code Violations**
**URL:** https://data.cityofnewyork.us/Housing-Development/Housing-Maintenance-Code-Violations/wvxf-dwi5

**Purpose:** Building code violations, open violations, hazardous conditions

**Key Fields (NYC):**
- `violation_id`
- `building_id` (unique property ID)
- `violation_date`
- `violation_type` ("Heat/Hot Water", "Elevator", "Lead Paint", "Pests")
- `violation_class` ("A" = Non-hazardous, "B" = Hazardous, "C" = Immediately Hazardous)
- `violation_status` ("Open", "Closed")
- `inspection_date`
- `certified_date` (when fixed)
- `penalty_amount`

**Access Method:**
- Web Portal: NYC Open Data portal
- API: Socrata Open Data API
- Bulk Download: CSV files available

**Update Frequency:** Daily

**Feasibility:** HIGH for major cities, LOW for rural areas

**Pain Segment Use Cases:**
- Properties with Class B or C violations (safety hazards)
- Buildings with 10+ open violations (neglect, management issues)
- Properties with repeated violations (systemic failures)

---

## Cannabis (Legal Markets)

### 16. State Cannabis Licensing Boards

**Example: California Bureau of Cannabis Control**
**URL:** https://cannabis.ca.gov/

**Purpose:** License status, disciplinary actions, compliance violations

**Key Fields (California):**
- `license_number`
- `license_type` ("Retailer", "Distributor", "Manufacturer", "Cultivator")
- `license_status` ("Active", "Suspended", "Revoked", "Expired")
- `issue_date`
- `expiration_date`
- `disciplinary_actions` (fines, suspensions, notices)
- `violation_description`
- `fine_amount`

**Access Method:**
- Web Portal: License verification search
- API: Limited or none
- Bulk Download: Some states provide monthly lists

**Update Frequency:** Weekly

**Feasibility:** MEDIUM - Varies by state (CA, CO, WA have good portals)

**Pain Segment Use Cases:**
- Licensees with recent disciplinary actions (compliance failures)
- Businesses with "Suspended" status (operational disruption)
- Licenses expiring in next 60 days (renewal stress)

---

## General Business Databases (Low Feasibility)

**These databases exist but are LOW feasibility for Blueprint GTM due to soft signals or paywalls:**

### ❌ Dun & Bradstreet (Credit Scores)
- **Why LOW:** Proprietary data, expensive, no public access
- **Soft Signal:** Credit scores don't prove operational pain

### ❌ Secretary of State Business Filings
- **Why LOW:** Only shows entity status (active, dissolved), no operational data
- **Soft Signal:** Knowing a business is "Active" doesn't indicate pain points

### ❌ BBB Complaints
- **Why LOW:** Complaints are anecdotal, not systematic
- **Soft Signal:** Complaint volume is directional but not calculable

### ❌ LinkedIn (Employee Count, Job Postings)
- **Why LOW:** Requires scraping, data quality varies
- **Soft Signal:** Hiring velocity is interesting but doesn't prove pain

### ❌ Crunchbase (Funding, Valuation)
- **Why LOW:** Funding is a signal of growth, not pain
- **Soft Signal:** Knowing a company raised $10M doesn't indicate problem areas

---

## Database Selection Framework

Use this decision tree during Wave 2:

```
START: What industry is the target company in?

├─ Regulated Industry? (Healthcare, Manufacturing, Food, Transportation)
│  ├─ YES → Search for government databases (EPA, OSHA, CMS, FMCSA, health depts)
│  │         Feasibility: HIGH
│  │         Confidence: 90-95% (Tier 1)
│  └─ NO → Go to next question
│
├─ Physical Locations? (Restaurants, Retail, Real Estate)
│  ├─ YES → Search for local databases (health inspections, building violations)
│  │         Feasibility: MEDIUM (varies by city)
│  │         Confidence: 85-90% (Tier 1 if available)
│  └─ NO → Go to next question
│
└─ Zero Regulatory Footprint? (SaaS, Consulting, E-commerce)
   └─ YES → Use competitive intelligence (G2, pricing, reviews, traffic)
             Feasibility: MEDIUM (scraping required)
             Confidence: 50-70% (Tier 3)
```

---

## Quick Reference: Feasibility by Industry

| Industry | Best Database | Feasibility | Confidence Tier |
|----------|---------------|-------------|-----------------|
| **Hospitals** | CMS Care Compare | HIGH | Tier 1 (90-95%) |
| **Nursing Homes** | CMS Nursing Home Compare | HIGH | Tier 1 (90-95%) |
| **Manufacturing** | EPA ECHO, OSHA | HIGH | Tier 1 (90-95%) |
| **Restaurants** | Local Health Inspections | HIGH (major cities) | Tier 1 (85-90%) |
| **Trucking** | FMCSA SAFER | HIGH | Tier 1 (90-95%) |
| **Aviation** | FAA Registry | MEDIUM | Tier 2 (75-80%) |
| **SaaS** | G2, Competitive Intel | MEDIUM | Tier 3 (50-70%) |
| **Retail** | Building Violations | MEDIUM (major cities) | Tier 1 (85-90%) |
| **Cannabis** | State Licensing Boards | MEDIUM | Tier 1 (85-90%) |
| **Financial Services** | FINRA BrokerCheck | MEDIUM (manual only) | Tier 1 but LOW feasibility |
| **Consulting** | None | LOW | Tier 3 (50-60%) |

---

## Adding New Databases to This Catalog

When you discover a new high-value database during Wave 2, document it here:

**Template:**
```markdown
### [Database Number]. [Database Name]

**URL:** [access point]

**Purpose:** [what pain points this database reveals]

**Key Fields:**
- `field_name_1` (description)
- `field_name_2` (description)
- `field_name_3` (description)

**Access Method:**
- Web Portal: [details]
- API: [details]
- Bulk Download: [details]

**Update Frequency:** [daily/weekly/monthly/annually]

**Feasibility:** [HIGH/MEDIUM/LOW - explain]

**Pain Segment Use Cases:**
- [Example use case 1]
- [Example use case 2]

**Confidence Level:** [50-95% with reasoning]
```

---

## Related Documentation

- [data-discovery-queries.md](../prompts/data-discovery-queries.md) - Search query templates for finding these databases
- [methodology.md](../prompts/methodology.md) - Data confidence tiers (Tier 1, 2, 3)
- [calculation-worksheets.md](../prompts/calculation-worksheets.md) - How to document database field usage

---

**Version:** 1.0.0 (November 2025)

**Maintained By:** Blueprint GTM Community

**Contributions Welcome:** Submit new databases via pull request with completed template above.
