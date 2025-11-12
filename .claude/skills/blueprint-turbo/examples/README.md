# Blueprint GTM Example Playbooks

This directory contains real-world example HTML playbooks demonstrating Blueprint GTM methodology across different data confidence tiers.

---

## Available Examples

### 1. [example-playbook-owner-com.html](./example-playbook-owner-com.html)

**Company:** Owner.com (Restaurant operations & financial management platform)

**Industry:** Restaurant Technology / Food Service

**Data Confidence Tier:** Tier 2 (Hybrid Approach - 65-75% confidence)

**Why This Example:**
- Demonstrates how to handle industries with LIMITED government data
- Restaurant operational pain (manual inventory, pricing inconsistencies) doesn't create EPA violations or OSHA citations
- Shows Tier 2 hybrid approach: public data (health inspections, review velocity) + competitive intelligence (menu pricing scraping, order volume estimation)
- Calculation worksheets show hedged language and disclosed methodology

**Key Plays:**
- **PQS 1:** Multi-Platform Pricing Arbitrage Detector (DoorDash vs. website menu pricing gaps)
- **PQS 2:** Review Velocity Surge Detector (185% Google Maps review increase = 3x traffic signal)
- **PVP 1:** Pre-Built Competitive Menu Pricing Analysis (top 20 items vs. 3 competitors)
- **PVP 2:** Health Inspection Score Trend Analysis (recurring violation pattern identification)

**What You'll Learn:**
- How to combine multiple data sources when pure government data isn't available
- Proper hedging language for estimated calculations ("estimated," "based on," "suggests")
- Building calculation worksheets for competitive intelligence (review velocity, pricing arbitrage)
- Delivering permissionless value when you can't cite EPA violation #XYZ

**Best For:** SaaS companies, retail tech, e-commerce platforms, consulting firms—any business targeting industries without rich regulatory data.

---

### 2. [example-playbook-healthcare.html](./example-playbook-healthcare.html)

**Company:** Healthcare Provider (Example for any healthcare tech vendor)

**Industry:** Healthcare / Hospitals

**Data Confidence Tier:** Tier 1 (Pure Government Data - 90-95% confidence)

**Why This Example:**
- Demonstrates the GOLD STANDARD: pure CMS government data with provider IDs
- Healthcare has comprehensive public databases (star ratings, readmission rates, patient experience scores)
- Shows direct statements with zero hedging (no "estimated" or "suggests")
- Every claim verifiable in 30 seconds via Medicare.gov lookup

**Key Plays:**
- **PQS 1:** Low CMS Star Rating Detector (2 stars, 1.4 below state average, -$2.1M VBP penalty)
- **PQS 2:** High Readmission Rate Detector (Heart failure 25.8% vs. 21.9% national, 27 excess readmissions)
- **PVP 1:** Pre-Built CMS Penalty Forecast (Q1-Q4 2026 calendar with -$5.1M total impact)
- **PVP 2:** Pre-Built Peer Comparison Report (8 similar TX hospitals, ranked 7th out of 8)

**What You'll Learn:**
- How to leverage government databases with record-level precision
- Direct messaging language (no hedging when confidence is 90-95%)
- Building calculation worksheets for Tier 1 data (CMS provider IDs, star ratings, penalty formulas)
- Delivering permissionless value with pre-built financial forecasts and peer comparisons

**Best For:** Healthcare tech vendors, regulatory compliance software, environmental services (EPA/OSHA), transportation (FMCSA), manufacturing—any business targeting highly regulated industries with rich government databases.

---

## How to Use These Examples

### For Learning:
1. **Start with the healthcare example** if your industry has government databases
   - Study the direct language ("Your facility has a 2-star rating")
   - Note how every claim includes Provider ID or record number
   - See how calculation worksheets cite specific CMS database fields

2. **Move to the owner.com example** if your industry lacks government data
   - Study the hedged language ("estimated," "based on," "suggests")
   - Note how hybrid approaches combine multiple data sources
   - See how calculation worksheets disclose estimation methodology and confidence levels

### For Adaptation:
1. **Identify your data tier:**
   - Do prospects have EPA violations, OSHA citations, CMS ratings? → Use healthcare example as template (Tier 1)
   - Do prospects have health inspections + competitive presence? → Use owner.com example as template (Tier 2)
   - Do prospects have zero government footprint? → Extend owner.com approach with more competitive intelligence (Tier 3)

2. **Swap industry-specific data sources:**
   - Healthcare example: Replace CMS with your database (EPA ECHO, OSHA, FMCSA, state licensing boards)
   - Owner.com example: Replace menu pricing/review velocity with your hybrid data (tech stack detection, pricing, traffic estimation)

3. **Maintain calculation worksheet rigor:**
   - Always cite exact database URLs and field names
   - Always disclose confidence levels (50-95%)
   - Always include limitations section
   - Always use appropriate hedging language for your tier

### For Pitching Blueprint GTM Internally:
- Show these examples to your sales leadership to demonstrate what intelligence-driven outreach looks like
- Compare "The Old Way" sections to your current SDR email templates (be brutally honest)
- Calculate potential reply rate improvement: Tier 1 messages typically get 15-25% reply rates vs. 1-3% for generic outreach
- Use calculation worksheets as proof points for "we actually do the research"

---

## Example Comparison Matrix

| Feature | Owner.com (Tier 2) | Healthcare (Tier 1) |
|---------|-------------------|---------------------|
| **Data Sources** | Health inspections + menu pricing + review velocity | CMS star ratings + readmission rates + penalty data |
| **Confidence Level** | 65-75% (hybrid estimation) | 90-95% (pure government data) |
| **Language Style** | Hedged ("estimated," "suggests") | Direct ("Your facility has") |
| **Record Identifiers** | Restaurant name + health permit ID | CMS Provider ID 450123 |
| **Calculation Complexity** | Multi-step estimation (review velocity × industry benchmark) | Direct extraction (CMS field values) |
| **Verifiability** | Moderate (requires scraping to replicate) | High (30-second Medicare.gov lookup) |
| **Typical Reply Rate** | 8-12% (Tier 2 messages) | 15-25% (Tier 1 messages) |
| **Best Use Case** | Industries without regulatory pain | Highly regulated industries |

---

## File Sizes & Load Times

Both example files are self-contained HTML (no external dependencies):

- **example-playbook-owner-com.html:** ~35 KB, loads instantly on any device
- **example-playbook-healthcare.html:** ~42 KB, loads instantly on any device

Mobile-responsive design works on phones, tablets, and desktops. Print-friendly if executives want hard copies for board meetings.

---

## Viewing the Examples

### Option 1: Open Locally
```bash
# Navigate to examples directory
cd /path/to/.claude/skills/blueprint-turbo/examples/

# Open in default browser (macOS)
open example-playbook-owner-com.html
open example-playbook-healthcare.html

# Open in default browser (Linux)
xdg-open example-playbook-owner-com.html
xdg-open example-playbook-healthcare.html

# Open in default browser (Windows)
start example-playbook-owner-com.html
start example-playbook-healthcare.html
```

### Option 2: Drag & Drop
- Drag the HTML file directly into your browser window
- No server required—works offline

### Option 3: Host on Simple Web Server (Optional)
```bash
# Python 3
python3 -m http.server 8000

# Then visit: http://localhost:8000/example-playbook-owner-com.html
```

---

## Creating Your Own Example Playbooks

### Step 1: Choose a Target Company
Pick a real company in your ICP to analyze (don't use in production outreach without permission—this is for learning).

### Step 2: Run Blueprint Turbo
```bash
/blueprint-turbo https://target-company.com
```

Wait 12-15 minutes for the full 4-wave execution.

### Step 3: Review the Generated HTML
Blueprint Turbo outputs: `blueprint-gtm-playbook-[company-name].html`

Compare it to these examples:
- Does it match the quality bar? (8.0+/10 buyer scores)
- Are calculation worksheets complete?
- Is data confidence tier appropriate?

### Step 4: Document Learnings
If the generated playbook is good, consider adding it to this examples/ directory:
- Rename to `example-playbook-[company-name].html`
- Add entry to this README
- Commit to your Blueprint Turbo repository

---

## Common Questions

**Q: Can I send these example playbooks to prospects?**
A: NO. These are educational examples with generic/placeholder data. Always generate fresh playbooks for real prospects using `/blueprint-turbo <url>`.

**Q: Why don't the examples have real company names?**
A: Healthcare example uses "[Hospital Name]" and Provider ID 450123 (a fictitious ID) to avoid citing real hospitals without consent. Owner.com example references the actual company but with fabricated data (menu pricing, review counts) for illustration purposes only.

**Q: How do I know which example to follow for my industry?**
A: Use the Database Selection Framework in [common-databases.md](../references/common-databases.md):
- Regulated industry (healthcare, manufacturing, food, transportation) → Healthcare example (Tier 1)
- Physical locations with local data (restaurants, retail, real estate) → Owner.com example (Tier 2)
- Zero regulatory footprint (SaaS, consulting) → Extend Owner.com approach (Tier 2-3)

**Q: The healthcare example seems too detailed. Do I really need that much calculation?**
A: YES. The calculation worksheets are what differentiate Blueprint GTM from "I Googled your company." Prospects can dismiss claims without worksheets as "made up." With worksheets, they can verify your math and trust your synthesis.

**Q: Can I simplify the HTML template for faster creation?**
A: You can, but don't sacrifice mobile responsiveness or calculation worksheet sections. The Blueprint branding (colors, fonts) and structure are optimized for credibility with C-suite executives. Simplifying too much makes it look like a Google Doc instead of consulting-grade deliverable.

---

## Next Steps

After reviewing these examples:

1. **Try generating your own playbook:**
   ```bash
   /blueprint-turbo https://your-target-company.com
   ```

2. **Compare your output to these examples:**
   - Are your calculation worksheets as detailed?
   - Is your data confidence tier appropriate?
   - Do your messages pass the Texada Test? (Hyper-specific, factually grounded, non-obvious)

3. **Refine your approach:**
   - See [methodology.md](../prompts/methodology.md) for buyer critique rubric
   - See [calculation-worksheets.md](../prompts/calculation-worksheets.md) for templates
   - See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) if messages score <8.0/10

4. **Study the data sources:**
   - Healthcare example → Explore CMS Care Compare yourself
   - Owner.com example → Try scraping menu pricing for a local restaurant
   - Get comfortable with the underlying databases before generating messages at scale

---

## Related Documentation

- [README.md](../README.md) - Blueprint Turbo overview and quick start
- [SKILL.md](../SKILL.md) - Full methodology documentation
- [methodology.md](../prompts/methodology.md) - Buyer critique rubric, Texada Test, message formats
- [calculation-worksheets.md](../prompts/calculation-worksheets.md) - Calculation worksheet templates and examples
- [common-databases.md](../references/common-databases.md) - Industry database catalog
- [data-discovery-queries.md](../prompts/data-discovery-queries.md) - Search query templates for Wave 2

---

**Version:** 1.0.0 (November 2025)

**Feedback:** If you generate a playbook that significantly outperforms these examples (higher buyer scores, better reply rates), consider contributing it as an additional example.
