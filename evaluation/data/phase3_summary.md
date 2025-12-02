# Phase 3: Evaluation Pipeline - Summary

Generated: 2025-11-28

## Overview

Phase 3 implemented and ran the evaluation pipeline to test contact finding against ground truth data.

## Components Delivered

1. **Evaluation Runner Script** (`evaluation/scripts/run_evaluation.py`)
   - Domain resolver evaluation (pending full setup)
   - Blitz contact finder evaluation
   - Metrics calculation and reporting
   - Support for data splits (cal_dev, validation, blind)

2. **Blitz API Integration Fixes**
   - Fixed API parameter names per OpenAPI spec:
     - `company_linkedin_url` (not `linkedin_company_url`)
     - `cascade` array with `include_title` (not `cascade_filters.titles`)
   - Fixed response field mappings:
     - `full_name` → `name`
     - `job_title` → `title`
     - `person_linkedin_url` → `linkedin_url`

## Evaluation Results

### CAL/DEV Split (208 companies with LinkedIn)
- **Persona:** owner_operator only
- **Hit Rate:** 22.1% (46/208)
- **Total Contacts Found:** 198
- **Credits Used:** 198

### VALIDATION Split (82 companies with LinkedIn)
- **Personas:** owner_operator, vp_marketing, vp_sales
- **Total Queries:** 246 (82 × 3 personas)
- **Hit Rate:** 10.6% (26/246)
  - owner_operator: 12.2%
  - vp_marketing: 8.5%
  - vp_sales: 11.0%
- **Total Contacts Found:** 134
- **Credits Used:** 134
- **Cost per Hit:** 5.15 credits

### vs Targets

| Metric | Actual | Target | Status |
|--------|--------|--------|--------|
| Persona Recall | 10.6% | 70% | FAIL |
| Cost per Contact | 5.15 credits | <0.5 credits | FAIL |

## Key Observations

1. **SMB Coverage Gap**: Blitz has better coverage for larger enterprises (hospitals, enterprises) than owner-operated SMBs which are our target market.

2. **Persona Type Impact**: Owner/Founder searches perform better (12.2%) than VP-level searches (8-11%), likely because SMBs often have visible founders but rarely have formal VP titles.

3. **Healthcare Bias**: The sample with LinkedIn URLs is skewed toward healthcare (large organizations) which have better data coverage than restaurants, services, etc.

4. **Cost Efficiency**: At 5.15 credits per persona hit, the current approach needs optimization. The target of <0.5 credits/contact would require ~10x improvement in hit rate or alternative data sources.

## Files Generated

- `evaluation/scripts/run_evaluation.py` - Main evaluation runner
- `evaluation/data/contact_results_cal_dev.parquet` - CAL/DEV results
- `evaluation/data/contact_results_validation.parquet` - Validation results
- `evaluation/data/evaluation_report_cal_dev.md` - CAL/DEV report
- `evaluation/data/evaluation_report_validation.md` - Validation report

## Cache Statistics

| API | Cached Entries |
|-----|---------------|
| Ocean.io | 411 |
| Blitz waterfall-icp | 450 |

## Next Steps

1. **Domain Resolver Evaluation**: Set up full domain resolver with API keys to evaluate domain accuracy

2. **Alternative Contact Sources**: Evaluate other contact finding APIs (Scrapin, Leadmagic) for SMB coverage

3. **Title Pattern Tuning**: Adjust title patterns for SMB context (e.g., "Owner" vs "CEO")

4. **Industry-Specific Analysis**: Analyze hit rates by industry to identify best use cases

5. **Cost Optimization**: Explore caching, filtering, and API selection strategies to reduce cost per hit
