## Contact Finder - Quick Reference

See `contact-finder/README.md` for full documentation.

### Two Pipelines

| Pipeline | Target | Cost | Validation |
|----------|--------|------|------------|
| **SMB Pipeline** | Small businesses (plumbers, electricians) | $0.01/company | Rule-based |
| **Enterprise Pipeline** | Fortune 1000 executives | $0.50-4/company | LLM-based |

### SMB Pipeline Architecture (Recommended for small businesses)

```
Input (CSV/JSON)
    ↓
1. Google Maps Discovery (OpenWeb Ninja $0.002) → owner, phone, email
    ↓
2. Website Contacts (OpenWeb Ninja $0.002) → emails, social links
    ↓
3. Data Fill (Serper $0.001) → fallback for missing data
    ↓
4. Social Links Search (OpenWeb Ninja $0.002) → LinkedIn for names
    ↓
5. Simple Validation (no LLM) → rule-based scoring
    ↓
Output (ContactResult[])
```

### Provider Recommendations

| Provider | Cost | Accuracy | Use |
|----------|------|----------|-----|
| **OpenWeb Ninja** | $0.002/query | TBD | SMB discovery (Google Maps, contacts) |
| **Serper** | $0.001/query | 100% recent | Real-time OSINT |
| **Blitz** | $0.50-4/query | 91% | Enterprise with LinkedIn |
| **Scrapin** | FREE | 35% | Backup only |
| **LeadMagic** | $22/hit | 8.9% | **NOT RECOMMENDED** |

---

## API Keys

```bash
# Primary (SMB Pipeline)
export RAPIDAPI_KEY="0cd58ac4edmshf140736785d2e6fp13d33djsnc6c9a79c08b6"
export SERPER_API_KEY="e69a4729139f6830beb880fc9ce91b78d3021c64"

# Enterprise Pipeline
export SCRAPIN_API_KEY="sk_9df5eef5fda9a32a2d9488d08dac6bc451d9cfdd"
export LEADMAGIC_API_KEY="14be553dd06530684ab92a2ef97cc0ae"
```

---

## Quick Start

### SMB Pipeline
```python
from contact_finder.modules.pipeline.smb_pipeline import SMBContactPipeline

pipeline = SMBContactPipeline(concurrency=10)
result = await pipeline.run("companies.csv", limit=100)
```

### Enterprise Pipeline
```python
from contact_finder.contact_finder import ContactFinder

finder = ContactFinder.from_config("config.yaml")
result = await finder.find_contacts("Acme Corp", "acme.com")
```

---

## Testing Commands

### SMB Pipeline Test
```bash
RAPIDAPI_KEY="..." SERPER_API_KEY="..." \
python -u -m evaluation.scripts.run_smb_pipeline_test \
  --input evaluation/data/smb_sample.json \
  --output evaluation/results/smb_test.json \
  --concurrency 10
```

### Enterprise Pipeline Test
```bash
python -m evaluation.scripts.run_pipeline_test \
  --linkedin-export ~/Downloads/LinkedInExport.zip \
  --sources rapidapi scrapin \
  --sample 100
```

---

## Key Modules

### Discovery
- `openweb_ninja.py` - Google Maps + Website Contacts ($0.002/query)
- `serper_osint.py` - Google search OSINT ($0.001/query)
- `serper_filler.py` - Fill missing domain/phone/owner

### Enrichment
- `blitz.py` - LinkedIn email/phone (91% accuracy)
- `scrapin.py` - LinkedIn profiles (FREE, 35% accuracy)

### Validation
- `simple_validator.py` - Rule-based SMB validation (no LLM)
- `contact_judge.py` - LLM validation (GPT-4o-mini)

### Pipeline
- `smb_pipeline.py` - Full SMB contact discovery

---

## Validation Scoring (SMB)

| Source | Points |
|--------|--------|
| google_maps_owner | +40 |
| google_maps | +35 |
| openweb_contacts | +25 |
| Strong owner title (Owner, CEO, Founder) | +40 |
| Has phone | +15 |
| Email matches domain | +20 |

**Threshold: 50 points = valid contact**
