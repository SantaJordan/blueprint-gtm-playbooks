# Contact Finder Evaluation Scripts

This directory contains scripts for evaluating the contact finder pipeline against multi-source verified ground truth.

## Overview

The evaluation framework has three phases:

1. **Phase A**: Build multi-source contact ground truth
2. **Phase B**: Evaluate contact finder pipeline
3. **Phase C**: Compare individual enrichment sources

## Scripts

### 1. build_contact_truth.py

Builds verified contact ground truth by cross-referencing multiple sources:
- Ocean.io people search
- Blitz waterfall-icp
- ZoomInfo page scraping
- News/funding search

**Usage:**
```bash
# Set API keys
export OCEAN_API_KEY=your_key
export BLITZ_API_KEY=your_key
export ZENROWS_API_KEY=your_key
export SERPER_API_KEY=your_key

# Run truth builder
python evaluation/scripts/build_contact_truth.py \
  --companies ./evaluation/data/companies_truth.parquet \
  --output ./evaluation/data/contacts_truth.parquet \
  --max-companies 100  # Limit for testing
```

**Output:**
- `contacts_truth.parquet`: Verified contacts with tier labels (gold/silver/bronze)

### 2. evaluate_contact_finder.py

Evaluates the full contact finder pipeline against ground truth:
- Runs Serper + ZenRows + multi-source discovery + LLM judgment
- Measures discovery rate, person accuracy, email accuracy
- Calculates LLM calibration (Expected Calibration Error)

**Usage:**
```bash
python evaluation/scripts/evaluate_contact_finder.py \
  --contacts ./evaluation/data/contacts_truth.parquet \
  --config contact-finder/config.yaml \
  --output ./evaluation/data/pipeline_eval_report.md \
  --max-companies 50
```

**Metrics:**
| Metric | Target | Description |
|--------|--------|-------------|
| Discovery Rate | ≥60% | Found any contact for persona |
| Person Accuracy | ≥40% | Found correct person |
| Email Accuracy | ≥80% | Email matches ground truth |
| LLM Calibration (ECE) | <0.15 | Confidence predicts accuracy |

### 3. compare_enrichment_sources.py

Compares individual enrichment sources:
- Scrapin
- Blitz
- Ocean.io

**Usage:**
```bash
python evaluation/scripts/compare_enrichment_sources.py \
  --contacts ./evaluation/data/contacts_truth.parquet \
  --output ./evaluation/data/source_comparison.md \
  --sources scrapin blitz ocean
```

**Metrics per source:**
- Coverage: % of companies with any data
- Person Match Rate: % finding correct person
- Email Match Rate: % with correct email
- Cost per Hit: Credits / successful finds

### 4. minimal_config_test.py

Tests minimal cost configuration:
- Scrapin (FREE)
- ZenRows (web scraping)
- LLM judgment (GPT-4o-mini)

**Usage:**
```bash
python evaluation/scripts/minimal_config_test.py \
  --contacts ./evaluation/data/contacts_truth.parquet \
  --output ./evaluation/data/minimal_config_report.md
```

**Metrics:**
- LLM Precision: Correct / Accepted
- LLM Recall: Accepted Correct / Total Correct
- Cost per Correct: Total cost / correct contacts

---

## SMB Pipeline Scripts (NEW)

These scripts test the SMB-focused pipeline using OpenWeb Ninja and Serper.

### 5. run_smb_pipeline_test.py

Tests the full SMB pipeline (OpenWeb Ninja + Serper + Simple Validation):

**Usage:**
```bash
export RAPIDAPI_KEY=your_key
export SERPER_API_KEY=your_key
export OPENAI_API_KEY=your_key  # Optional, for email enrichment

python -u -m evaluation.scripts.run_smb_pipeline_test \
  --input evaluation/data/smb_sample.json \
  --output evaluation/results/smb_test.json \
  --concurrency 10 \
  --delay 0.3 \
  --checkpoint-every 100
```

**Metrics:**
- Find Rate: % of companies with contacts found
- Validation Rate: % of contacts passing simple validation
- Cost per Company: OpenWeb Ninja + Serper costs

### 6. run_pipeline_test.py

Tests LinkedIn profile enrichment across providers:

**Usage:**
```bash
python -m evaluation.scripts.run_pipeline_test \
  --linkedin-export ~/Downloads/LinkedInExport.zip \
  --sources rapidapi scrapin leadmagic \
  --sample 100 \
  --concurrency 3
```

**Metrics:**
- Name Match Rate: Enriched name matches ground truth
- Company Match Rate: Current company matches
- Provider comparison on same profiles

### 7. run_discovery_test.py

Tests contact discovery from name + company:

**Usage:**
```bash
python -m evaluation.scripts.run_discovery_test \
  --csv people_all_dedup.csv \
  --sample 200 \
  --concurrency 3
```

### 8. prepare_smb_sample.py

Prepares SMB test samples from raw data:

**Usage:**
```bash
python evaluation/scripts/prepare_smb_sample.py \
  --input raw_companies.csv \
  --output evaluation/data/smb_sample.json \
  --limit 1000
```

---

## Data Files

| File | Description |
|------|-------------|
| `companies_truth.parquet` | 1013 companies with domains |
| `contacts_truth.parquet` | Multi-source verified contacts |
| `cache.db` | SQLite cache for API responses |

## Ground Truth Tiers

Contacts are classified by verification level:

- **GOLD**: 3+ sources agree OR 2 sources + manual verification
- **SILVER**: 2 sources agree
- **BRONZE**: 1 source only (unverified)

Only gold and silver tier contacts are used for evaluation.

## Workflow

1. **Build Ground Truth** (once):
   ```bash
   python evaluation/scripts/build_contact_truth.py
   ```

2. **Evaluate Pipeline** (after any changes):
   ```bash
   python evaluation/scripts/evaluate_contact_finder.py
   ```

3. **Compare Sources** (to find best source):
   ```bash
   python evaluation/scripts/compare_enrichment_sources.py
   ```

4. **Test Minimal Config** (cost optimization):
   ```bash
   python evaluation/scripts/minimal_config_test.py
   ```

## Environment Variables

```bash
# SMB Pipeline (primary)
export RAPIDAPI_KEY=your_rapidapi_key      # OpenWeb Ninja ($0.002/query)
export SERPER_API_KEY=your_serper_key      # Google OSINT ($0.001/query)

# Enterprise Pipeline
export BLITZ_API_KEY=your_blitz_key        # LinkedIn waterfall ($0.50-4/query)
export SCRAPIN_API_KEY=your_scrapin_key    # LinkedIn profiles (FREE)
export OPENAI_API_KEY=your_openai_key      # LLM validation

# Optional
export ZENROWS_API_KEY=your_zenrows_key    # Website scraping
export LEADMAGIC_API_KEY=your_leadmagic_key  # NOT recommended (8.9% accuracy)
export EXA_API_KEY=your_exa_key            # Semantic search
export OCEAN_API_KEY=your_ocean_key        # Legacy
```

## Caching

All API responses are cached in `cache.db` with TTLs:
- Blitz: 90 days
- Ocean: 30 days
- Scrapin: 30 days
- Serper: 7 days
- Exa: 24 hours

View cache stats:
```python
from evaluation.harness.cache import EvaluationCache
cache = EvaluationCache("./evaluation/data/cache.db")
print(cache.stats())
```

## Key Questions Answered

1. **How well does the full pipeline work?**
   - Discovery rate, person accuracy, email accuracy

2. **Which enrichment source is best for SMBs?**
   - Scrapin vs Blitz vs Ocean comparison

3. **Can Scrapin + ZenRows + LLM work alone?**
   - Minimal cost configuration test

4. **Where does the pipeline fail?**
   - Failure attribution: search, scrape, wrong person, LLM rejection

5. **Is the LLM well-calibrated?**
   - Expected Calibration Error analysis
