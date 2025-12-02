# Contact Finder

Multi-source contact discovery system for finding decision-makers at companies. Optimized for both SMB owner discovery and enterprise executive search.

## Overview

Contact Finder provides **two distinct pipelines**:

| Pipeline | Target | Validation | Cost/Contact | Best For |
|----------|--------|------------|--------------|----------|
| **SMB Pipeline** | Small businesses (plumbers, electricians, etc.) | Rule-based | $0.01-0.02 | Owners with sparse LinkedIn |
| **Enterprise Pipeline** | Fortune 1000 companies | LLM-based | $0.50-4.00 | Executives with rich LinkedIn |

---

## Quick Start

### SMB Pipeline (Recommended for small businesses)

```python
import asyncio
from contact_finder.modules.pipeline.smb_pipeline import SMBContactPipeline

async def find_smb_owners():
    pipeline = SMBContactPipeline(
        rapidapi_key="your_rapidapi_key",      # OpenWeb Ninja
        serper_api_key="your_serper_key",      # Google OSINT
        concurrency=10
    )

    try:
        result = await pipeline.run("companies.csv", limit=100)

        for company in result.results:
            if company.contacts:
                best = company.contacts[0]
                print(f"{company.company_name}: {best.name} ({best.title})")
                print(f"  Email: {best.email}")
                print(f"  Phone: {best.phone}")
    finally:
        await pipeline.close()

asyncio.run(find_smb_owners())
```

### Enterprise Pipeline

```python
import asyncio
from contact_finder.contact_finder import ContactFinder

async def find_enterprise_contact():
    finder = ContactFinder.from_config("config.yaml")

    try:
        result = await finder.find_contacts(
            company_name="Acme Corporation",
            domain="acme.com",
            target_titles=["CEO", "President", "Owner"]
        )

        if result.best_contact:
            c = result.best_contact
            print(f"Found: {c.name} ({c.title})")
            print(f"Email: {c.email} (confidence: {c.email_confidence}%)")
            print(f"LinkedIn: {c.linkedin_url}")
    finally:
        await finder.close()

asyncio.run(find_enterprise_contact())
```

---

## Architecture

### SMB Pipeline (`modules/pipeline/smb_pipeline.py`)

Optimized for finding owners at small businesses where LinkedIn presence may be sparse.

```
INPUT (CSV/JSON)
    |
    v
+-------------------+
| 1. Input Analysis |  CSVExplorer: detect fields, map columns
+-------------------+
    |
    v
+------------------------+
| 2. Google Maps Search  |  OpenWeb Ninja ($0.002)
|    (PRIMARY)           |  -> owner_name, phone, email, website
+------------------------+
    |
    v
+------------------------+
| 3. Website Contacts    |  OpenWeb Ninja ($0.002)
|    (PRIMARY)           |  -> emails, phones, social links
+------------------------+
    |
    v
+-------------------+
| 4. Data Fill      |  Serper ($0.001) - FALLBACK
|    (FALLBACK)     |  -> domain, phone, owner if missing
+-------------------+
    |
    v
+-------------------+
| 5. Website Scrape |  ZenRows - FALLBACK
|    (FALLBACK)     |  -> Schema.org, page content
+-------------------+
    |
    v
+-------------------+
| 6. Serper OSINT   |  Serper ($0.001) - FALLBACK
|    (FALLBACK)     |  -> owner name from search
+-------------------+
    |
    v
+------------------------+
| 7. Social Links Search |  OpenWeb Ninja ($0.002)
|                        |  -> LinkedIn URL for names
+------------------------+
    |
    v
+-------------------+
| 8. Email Enrich   |  LeadMagic ($0.01)
|    (OPTIONAL)     |  -> email to LinkedIn
+-------------------+
    |
    v
+-------------------+
| 9. Validation     |  SimpleValidator (no LLM)
|    (RULES-BASED)  |  -> score, confidence, valid/invalid
+-------------------+
    |
    v
OUTPUT (ContactResult[])
```

**Cost breakdown (SMB Pipeline):**
- Google Maps: $0.002
- Website Contacts: $0.002
- Social Links: $0.002 (if needed)
- Serper fallback: $0.001 (if needed)
- **Total: $0.006-0.01 per company**

### Enterprise Pipeline (`contact_finder.py`)

Optimized for finding executives at large companies with LinkedIn presence.

```
INPUT (company_name, domain)
    |
    v
+---------------------+
| 1. Input Validation |
+---------------------+
    |
    v
+------------------------+
| 2. LinkedIn Discovery  |  Serper + Scrapin
|                        |  -> company LinkedIn URL
+------------------------+
    |
    v
+------------------------+
| 3. Contact Discovery   |  Parallel sources:
|                        |  - Blitz waterfall-icp
|                        |  - Scrapin search
|                        |  - Website scraping
+------------------------+
    |
    v
+------------------------+
| 4. Enrichment Waterfall|  Scrapin -> Blitz -> LeadMagic
|                        |  -> email, phone, full profile
+------------------------+
    |
    v
+------------------------+
| 5. LLM Validation      |  GPT-4o-mini
|                        |  -> confidence, reasoning
+------------------------+
    |
    v
OUTPUT (ContactResult[])
```

**Cost breakdown (Enterprise Pipeline):**
- LinkedIn Discovery: $0.001-0.05
- Blitz waterfall: $0.50-4.00
- LLM validation: $0.001
- **Total: $0.50-4.00 per company**

---

## Modules Reference

### Discovery (`modules/discovery/`)

| Module | Description | Cost | Use Case |
|--------|-------------|------|----------|
| `openweb_ninja.py` | 3 RapidAPI endpoints: Local Business, Website Contacts, Social Links | $0.002/query | SMB discovery |
| `serper_osint.py` | Google search OSINT for executives | $0.001/query | Real-time exec search |
| `serper_filler.py` | Fill missing domain, phone, owner | $0.001/query | Data enrichment |
| `website_extractor.py` | ZenRows-based contact extraction | ~$0.01/page | Website scraping |
| `multi_source_finder.py` | Serper + Blitz with LLM reconciliation | $0.50-4/query | Enterprise |
| `linkedin_company.py` | Find company LinkedIn URLs | $0.001/query | LinkedIn discovery |
| `contact_search.py` | Main search orchestration | Varies | Pipeline component |

### Enrichment (`modules/enrichment/`)

| Module | Description | Cost | Accuracy | Recommendation |
|--------|-------------|------|----------|----------------|
| `blitz.py` | LinkedIn → email/phone | $0.50-4/query | 91% | **RECOMMENDED** for enterprise |
| `scrapin.py` | LinkedIn profile enrichment | FREE | 35% | Backup/free tier |
| `leadmagic.py` | Email finder | $22/hit | 8.9% | **NOT RECOMMENDED** |
| `waterfall.py` | Multi-source orchestration | Varies | Best of sources | Pipeline component |
| `exa.py` | Semantic search | ~$0.01/query | Varies | Research/discovery |
| `site_scraper.py` | Direct website scraping | ~$0.01/page | Varies | Fallback |

### Validation (`modules/validation/`)

| Module | Description | Use Case |
|--------|-------------|----------|
| `simple_validator.py` | Rule-based SMB validation (no LLM) | SMB pipeline |
| `contact_judge.py` | LLM-based validation (GPT-4o-mini) | Enterprise pipeline |
| `email_validator.py` | Email validation with catch-all detection | Both pipelines |
| `linkedin_normalizer.py` | LinkedIn URL standardization | Both pipelines |

### Pipeline (`modules/pipeline/`)

| Module | Description |
|--------|-------------|
| `smb_pipeline.py` | Full SMB contact discovery pipeline |

### Input (`modules/input/`)

| Module | Description |
|--------|-------------|
| `csv_explorer.py` | Dynamic CSV/JSON field detection and mapping |

### LLM (`modules/llm/`)

| Module | Description |
|--------|-------------|
| `provider.py` | LLM provider factory |
| `openai_provider.py` | OpenAI GPT integration |
| `anthropic_provider.py` | Anthropic Claude integration |

---

## Validation Scoring (SMB Pipeline)

The `SimpleContactValidator` uses rule-based scoring:

### Source Scores
| Source | Points | Notes |
|--------|--------|-------|
| `google_maps_owner` | +40 | Explicit owner field from Google Maps |
| `google_maps` | +35 | General Google Maps data |
| `openweb_contacts` | +25 | Website contact scraper |
| `website_schema` | +25 | Schema.org structured data |
| `input_csv` | +20 | From input file |
| `website_scrape` | +15 | Page content extraction |
| `serper_osint` | +10 | Text extraction from search |

### Title Scores
| Title Type | Points |
|------------|--------|
| Strong owner (Owner, CEO, Founder, President) | +40 |
| Owner-related (Director, Manager, GM) | +30 |
| Any title | +10 |

### SMB Bonuses
| Condition | Points |
|-----------|--------|
| Has phone number | +15 |
| Google Maps 50+ reviews | +10 |
| Has Facebook/Instagram | +10 |
| Email matches domain | +20 |
| Full name (first + last) | +5 |

**Threshold: 50 points = valid contact**

---

## Provider Comparison

| Provider | Cost | Accuracy | Lag | Best For |
|----------|------|----------|-----|----------|
| **OpenWeb Ninja** | $0.002/query | TBD | Real-time | SMB discovery via Google Maps |
| **Serper** | $0.001/query | 100% | Real-time | OSINT, recent job changes |
| **Blitz** | $0.50-4/query | 91% | 1-2 weeks | Enterprise with LinkedIn URL |
| **Scrapin** | FREE | 35% | Unknown | Backup, free tier |
| **LeadMagic** | $22/hit | 8.9% | 4+ days | **NOT RECOMMENDED** |

**Recommendation**: Use **Serper OSINT + Blitz** for enterprise, **OpenWeb Ninja** for SMBs.

---

## Configuration

### Environment Variables

```bash
# Primary (SMB Pipeline)
export RAPIDAPI_KEY="your_rapidapi_key"    # OpenWeb Ninja
export SERPER_API_KEY="your_serper_key"    # Google OSINT

# Enterprise Pipeline
export BLITZ_API_KEY="your_blitz_key"      # Blitz waterfall
export SCRAPIN_API_KEY="your_scrapin_key"  # LinkedIn enrichment
export OPENAI_API_KEY="your_openai_key"    # LLM validation

# Optional
export ZENROWS_API_KEY="your_zenrows_key"  # Website scraping
export LEADMAGIC_API_KEY="your_leadmagic_key"  # Email enrichment (not recommended)
export EXA_API_KEY="your_exa_key"          # Semantic search
```

### config.yaml Example

```yaml
# API Keys
api_keys:
  serper: "your_serper_key"
  blitz: "your_blitz_key"
  scrapin: "your_scrapin_key"
  zenrows: "your_zenrows_key"

# LLM Configuration
llm:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.1

# Pipeline Settings
target_titles:
  - Owner
  - CEO
  - President
  - Founder
  - General Manager

max_contacts_per_company: 3
min_confidence: 50
include_phone: true
use_llm_judge: true

# Scraping
scraping:
  max_pages: 5
```

---

## Testing

### Run SMB Pipeline Test

```bash
export RAPIDAPI_KEY="your_key"
export SERPER_API_KEY="your_key"
export OPENAI_API_KEY="your_key"

python -u -m evaluation.scripts.run_smb_pipeline_test \
  --input evaluation/data/smb_sample.json \
  --output evaluation/results/smb_test.json \
  --concurrency 10 \
  --delay 0.3
```

### Run Enterprise Pipeline Test

```bash
python -m evaluation.scripts.run_pipeline_test \
  --linkedin-export ~/Downloads/LinkedInExport.zip \
  --sources rapidapi scrapin \
  --sample 100 \
  --concurrency 3
```

### Run Provider Comparison

```bash
python -m evaluation.scripts.compare_enrichment_sources \
  --contacts evaluation/data/contacts_truth.parquet \
  --sources scrapin blitz \
  --output evaluation/data/comparison.md
```

---

## Input Formats

### CSV Format
```csv
company_name,domain,city,state,vertical
"Joe's Plumbing","joesplumbing.com","Denver","CO","plumbing"
"ABC Electric","abcelectric.net","Austin","TX","electrical"
```

### JSON Format
```json
[
  {
    "company_name": "Joe's Plumbing",
    "domain": "joesplumbing.com",
    "city": "Denver",
    "state": "CO",
    "vertical": "plumbing"
  }
]
```

The `CSVExplorer` automatically detects and maps columns - you don't need exact column names.

---

## Output Format

```python
@dataclass
class ContactResult:
    name: str | None
    email: str | None
    phone: str | None
    title: str | None
    linkedin_url: str | None
    sources: list[str]         # Where contact was found
    validation: ValidationResult  # Score and reasons
```

```python
@dataclass
class ValidationResult:
    is_valid: bool
    confidence: float           # 0-100
    score_breakdown: dict       # Points per category
    reasons: list[str]          # Human-readable explanations
```

---

## Performance Tips

1. **Use concurrency wisely**: Set `concurrency=10` for SMB, `concurrency=50` for enterprise
2. **Add delays for rate limits**: `delay=0.3` seconds between requests
3. **Use checkpoints**: For large batches, set `checkpoint_every=100`
4. **Skip expensive stages**: Pass `skip_stages=["enrichment"]` to skip LeadMagic
5. **Prefer OpenWeb Ninja**: At $0.002/query, it's 70-95% cheaper than alternatives

---

## Evaluation Framework

See `evaluation/scripts/README.md` for full evaluation framework documentation.

Key scripts:
- `run_smb_pipeline_test.py` - Test SMB pipeline
- `run_pipeline_test.py` - Test enterprise pipeline
- `compare_enrichment_sources.py` - Provider comparison
- `build_contact_truth.py` - Build ground truth dataset
