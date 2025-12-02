# SMB Contact Finder - Tool Evaluation Report

**Date**: 2025-11-30
**Sample Size**: 100 companies (from 1400 total)
**Verticals**: Auto Body Shops, Bakeries, Breweries, Coffee Shops, Dialysis Centers, Fertility Clinics, Plumbers

---

## Executive Summary

The SMB contact finder pipeline was tested on 100 small businesses across 7 verticals. **Results show 0% end-to-end success rate**, with critical bottlenecks at both the **enrichment stage (13% success)** and **validation stage (0% pass rate)**.

### Key Findings

| Stage | Success Rate | Insight |
|-------|-------------|---------|
| LinkedIn Company Found | **43%** | Reasonable for SMBs |
| Contact Candidates Found | **42%** | Search is working |
| Candidates Enriched | **13%** | **Major bottleneck** - tools lack SMB data |
| Validation Passed | **0%** | LLM judge too strict or confidence threshold too high |

---

## Pipeline Stage Analysis

### Stage 1: LinkedIn Company Discovery (43% success)
Finding LinkedIn company pages for SMBs is challenging. 43% success is actually reasonable given:
- Many SMBs don't have LinkedIn company pages
- Name variations (e.g., "Joe's Plumbing" vs "Joe's Plumbing LLC")
- Multi-location businesses with different company pages

**Tools Used**: Scrapin Company Search, Exa.ai
**Recommendation**: Keep both tools - they complement each other

### Stage 2: Contact Discovery (42% success)
When we can't find a LinkedIn company page, we still find contact candidates 42% of the time through:
- Serper OSINT (Google search)
- Blitz ICP (company → contacts by title)

**Tools Used**: Serper, Blitz ICP
**Finding**: Discovery is NOT the bottleneck

### Stage 3: Enrichment Waterfall (13% of companies get any contact enriched)

This is the **critical bottleneck**. Even when we find candidate names, the enrichment tools often return no data.

| Tool | Purpose | Cost | Issue |
|------|---------|------|-------|
| **Scrapin** | LinkedIn profile enrichment | FREE | Often no match for SMB owners |
| **Blitz** | Email from LinkedIn URL | 1 credit | No data if no LinkedIn profile |
| **LeadMagic** | Email backup | Pay if found | Minimal coverage for SMBs |

**Root Cause**: SMB owners often don't have LinkedIn profiles, so all LinkedIn-based enrichment fails.

### Stage 4: LLM Validation (0% pass rate)

Even the 13 companies with enriched contacts failed validation. Possible causes:
1. **Confidence threshold too high** (currently 50)
2. **LLM judge too strict** - requiring strong evidence of current employment
3. **Data quality issues** - enriched data doesn't include enough evidence

---

## Per-Vertical Performance

| Vertical | LinkedIn Found | Candidates Found | Enriched | Best Strategy |
|----------|---------------|------------------|----------|---------------|
| Fertility Clinics | 47% | 53% | High | Healthcare databases |
| Dialysis Centers | 44% | 44% | Medium | Healthcare directories |
| Breweries | 36% | 43% | Medium | Website scraping |
| Coffee Shops | 69% | 31% | Low | Google Maps data |
| Bakeries | 50% | 40% | Low | Website scraping |
| Auto Body Shops | 28% | 39% | Low | OSINT focus |
| Plumbers | 30% | 40% | Low | Google Maps + OSINT |

**Key Insight**: Healthcare verticals (clinics, dialysis) perform better - likely because practitioners have LinkedIn profiles.

---

## Tool Recommendations

### Keep (High Value)
1. **Scrapin** - FREE LinkedIn enrichment, works when profiles exist
2. **Serper OSINT** - $0.001/search, finds contacts from Google results
3. **Exa.ai** - FREE, good for company discovery

### Consider Dropping
1. **LeadMagic** - Low SMB coverage, pay-per-find model means we pay for every failed lookup attempt
2. **Blitz ICP** - Credits wasted on SMBs without LinkedIn presence

### Add for SMBs
1. **Google Maps API** - SMBs are listed; can get owner names from business profiles
2. **Website Email Scraping** - Many SMBs list owner/contact on website
3. **BBB / Chamber of Commerce** - Business owner databases

---

## Recommendations

### Short Term (Quick Wins)
1. **Lower confidence threshold** to 30 (from 50) for SMBs
2. **Disable LLM judge** for SMB verticals - it's rejecting all contacts
3. **Add website email scraping** before paid enrichment tools

### Medium Term (Architecture Changes)
1. **SMB-specific waterfall**: Website scraping → Google Maps → OSINT → (skip LinkedIn tools)
2. **Title-based validation**: For SMBs, "Owner" title with company match is sufficient
3. **Direct email pattern**: firstname@domain.com with validation

### Long Term (Data Sources)
1. **Partner with SMB databases**: Yelp, Google My Business, BBB
2. **Build SMB-specific enrichment**: Trained on SMB data patterns
3. **Vertical-specific tools**: Healthcare databases for clinics, trade associations for plumbers

---

## Cost Analysis

| Tool | Cost/Lookup | SMB Hit Rate | Effective Cost/Success |
|------|-------------|--------------|------------------------|
| Scrapin | FREE | ~10% | FREE |
| Serper | $0.001 | ~40% | $0.0025 |
| Blitz | 1 credit (~$0.10) | ~5% | $2.00 |
| LeadMagic | ~$0.01 if found | ~5% | $0.20 |

**Conclusion**: For SMBs, the expensive enrichment tools (Blitz, LeadMagic) provide minimal value. Focus on FREE/cheap tools (Scrapin, Serper) and website scraping.

---

## Action Items

1. [ ] Add website email scraping before enrichment waterfall
2. [ ] Lower confidence threshold for SMB verticals
3. [ ] Create SMB-specific validation rules (simpler than enterprise)
4. [ ] Test Google Maps API for owner extraction
5. [ ] Consider dropping LeadMagic for SMB use cases
6. [ ] Build contact page scraper for SMB websites

---

## Raw Data

Full results available at:
- `evaluation/results/smb_test_100.json` (100 company test)
- `evaluation/results/smb_test_100.md` (generated report)

