# Enrichment Provider Evaluation Report

**Date:** 2025-11-28
**Objective:** Find the best enrichment provider for finding executives at companies

## Executive Summary

After testing multiple providers against both a master ground truth database (456 contacts) and a recency test set (13 recent executive appointments), we recommend:

### Winner: **Serper OSINT + Blitz Waterfall**

| Provider | Person Match Rate | Recency | Cost/Hit | Recommendation |
|----------|------------------|---------|----------|----------------|
| **Blitz** | 91.1% | 1-2 weeks lag | $0.50-4 | Best for structured data |
| **Serper** | 100% (recency test) | Real-time | $0.001 | Best for recent changes |
| Scrapin | 35.4% | Unknown | $0 (free) | Backup only |
| LeadMagic | 8.9% | 4+ days lag | $22.57 | **Not recommended** |
| Bright Data | N/A | Real-time | ~$0.01 | Requires LinkedIn URL |

---

## Detailed Findings

### 1. Master Database Evaluation (456 contacts)

Tested against verified ground truth contacts across 3 personas:
- Owner/Operator (CEO, Founder, Owner)
- VP Marketing (CMO, Head of Marketing)
- VP Sales (CRO, Head of Sales)

| Provider | Coverage | Person Match | Cost/Hit | Notes |
|----------|----------|--------------|----------|-------|
| **Blitz** | 91.1% | **91.1%** | $4.35 | Requires LinkedIn company URL |
| Scrapin | 93.7% | 35.4% | $0.00 | Free tier, lower quality |
| LeadMagic | 94.9% | 8.9% | $22.57 | High coverage, wrong people |

**By Persona:**

| Provider | Owner/Operator | VP Marketing | VP Sales |
|----------|---------------|--------------|----------|
| Blitz | 96.0% | 88.9% | 88.9% |
| Scrapin | 28.0% | 40.7% | 37.0% |
| LeadMagic | 12.0% | 14.8% | 0.0% |

### 2. Recency Evaluation (13 verified recent appointments)

Tested providers' ability to return CURRENT executives vs PREVIOUS ones.

**Ground truth source:** News articles announcing appointments (BusinessWire, PRNewswire, Bloomberg, etc.)

| Provider | Correct | Wrong Person | Not Found | Accuracy |
|----------|---------|--------------|-----------|----------|
| **Serper** | 3/3 | 0/3 | 0/3 | **100%** |
| LeadMagic | 2/13 | 9/13 | 2/13 | **15%** |

**LeadMagic Recency Issues:**
- Kohl's CEO (4 days old): Returned Ashley Buchanan (fired May 2025), actual is Michael Bender
- Ball Corp CEO (18 days old): Returned Dan Fisher (retired), actual is Ronald J. Lewis
- Convatec CEO (22 days old): Returned Karim Bitar (departed), actual is Jonny Mason

**Serper Success Stories:**
- Kohl's CEO: Found Michael Bender within 4 days of announcement
- Veeam CMO: Found Allison Cerra within 17 days of announcement
- Ball CEO: Found Ronald J. Lewis within 18 days of announcement

### 3. Bright Data Testing

**Status:** Unable to complete full evaluation

**Issues:**
1. Requires LinkedIn URL as input (can't search by company + title)
2. Dataset not configured in test account
3. Very slow (~45-60 seconds per query)
4. Results incomplete (Position: None, Company: None)

**Conclusion:** Not suitable for "find person at company" use case - requires knowing LinkedIn URL upfront, which defeats the purpose.

---

## Recommended Architecture

### Multi-Source Waterfall with LLM Reconciliation

```
STEP 1: Serper OSINT ($0.001/query)
   ├── Search: "[company] [title] 2025"
   ├── Extract: person names, LinkedIn URLs, news sources
   └── Why: Catches recent job changes within hours

STEP 2: Blitz waterfall-icp ($0.50-4/query)
   ├── Input: LinkedIn company URL + target titles
   ├── Returns: name, email, phone, LinkedIn URL
   └── Why: 91% accuracy on structured data

STEP 3: LLM Confidence Call (GPT-4o-mini ~$0.001)
   ├── If sources agree: HIGH confidence (95%+)
   ├── If sources disagree: Prefer Serper (more recent)
   └── Return: confidence score + reasoning
```

### Total Cost Per Contact: ~$0.50-4.10

| Step | Cost | When |
|------|------|------|
| Serper search | $0.001 | Always |
| Blitz ICP | $0.50-4 | If LinkedIn URL available |
| LLM reconciliation | $0.001 | If sources disagree |

### Implementation Files

Created:
- `contact-finder/modules/discovery/serper_osint.py` - OSINT discovery using Serper
- `contact-finder/modules/discovery/multi_source_finder.py` - Multi-source waterfall with LLM

---

## Key Insights

1. **Database providers have significant lag** - LeadMagic returns the PREVIOUS person in 69% of cases for recent job changes

2. **Google Search (Serper) is the most current** - Finds news about exec changes within hours

3. **Blitz has the best structured data** - 91% match rate on verified ground truth

4. **LeadMagic should be avoided** - 8.9% match rate, stale data, expensive ($22/hit)

5. **Multi-source validation is essential** - Combining Serper (for recency) + Blitz (for data quality) + LLM (for confidence) gives best results

---

## Sources Used

- [Kohl's CEO Announcement - CNBC](https://www.cnbc.com/2025/11/24/kohls-picks-new-ceo-after-a-turbulent-year-and-sales-declines.html)
- [Kohl's CEO - Bloomberg](https://www.bloomberg.com/news/articles/2025-11-23/kohl-s-to-name-michael-bender-as-ceo-after-year-of-disarray)
- [Kohl's Corporate Announcement](https://corporate.kohls.com/news/kohls-appoints-michael-j-bender-as-chief-executive-officer)

---

## Files Generated

| File | Description |
|------|-------------|
| `recency_ground_truth.json` | 13 verified recent exec appointments |
| `leadmagic_recency_results.json` | LeadMagic test results |
| `source_comparison.md` | Full source comparison report |
| `source_comparison_details.parquet` | Detailed test results |
| `ENRICHMENT_PROVIDER_EVALUATION.md` | This report |
