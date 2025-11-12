# Blueprint Turbo Troubleshooting Guide

This guide provides real-world debugging scenarios with actual error messages and solutions from Blueprint Turbo executions.

---

## Quick Diagnosis Flowchart

```
START: Blueprint Turbo execution fails or produces low-quality output

├─ Execution fails immediately (<1 minute)?
│  ├─ "Sequential Thinking MCP not found" → See Section 1.1
│  └─ "URL not accessible" / "Cannot fetch" → See Section 1.2
│
├─ Execution completes but takes 20-25 minutes (vs. 12-15)?
│  └─ Browser MCP missing or not working → See Section 2.1
│
├─ Synthesis phase fails ("zero HIGH feasibility segments")?
│  ├─ Target industry has no government data → See Section 3.1
│  └─ Data discovery found nothing → See Section 3.2
│
├─ All messages score <8.0/10?
│  ├─ Messages fail "non-obvious synthesis" → See Section 4.1
│  ├─ Messages fail "factually grounded" → See Section 4.2
│  └─ Wrong persona targeting → See Section 4.3
│
└─ HTML generation fails or looks broken?
   ├─ Template file missing/corrupted → See Section 5.1
   └─ Calculation worksheets incomplete → See Section 5.2
```

---

## Section 1: Immediate Failures (Execution <1 Minute)

### 1.1 Error: "Sequential Thinking MCP not found"

**Full Error Message:**
```
ERROR: Sequential Thinking MCP server is required but not found.
Blueprint Turbo cannot proceed without this dependency.

The Sequential Thinking MCP is used in the Synthesis phase to generate
pain segment hypotheses from available data sources. This is a REQUIRED
component and cannot be bypassed.

Please install Sequential Thinking MCP:
npm install -g @sequentialthinking/mcp-server

Then restart Claude and try again.
```

**Why This Happens:**
- Sequential Thinking MCP server is not installed
- MCP server is installed but not configured in Claude settings
- MCP server crashed on startup (check Claude logs)

**Solution:**

1. **Install Sequential Thinking MCP:**
   ```bash
   npm install -g @sequentialthinking/mcp-server
   ```

2. **Configure in Claude:**

   Edit your `claude_desktop_config.json` or `.claude/mcp.json`:
   ```json
   {
     "mcpServers": {
       "sequential-thinking": {
         "command": "npx",
         "args": [
           "@sequentialthinking/mcp-server"
         ]
       }
     }
   }
   ```

3. **Restart Claude** (critical step—config changes require restart)

4. **Verify Installation:**
   Ask Claude: "Can you list available MCP tools?"

   You should see: `mcp__sequential-thinking__sequentialthinking`

5. **If Still Failing:**
   - Check Node.js is installed: `node --version` (requires 18+)
   - Check npm packages: `npm list -g` (look for @sequentialthinking/mcp-server)
   - Check Claude logs for MCP startup errors (see [MCP_SETUP.md](./MCP_SETUP.md#troubleshooting))

**Full Fix Guide:** See [MCP_SETUP.md](./MCP_SETUP.md#sequential-thinking-mcp)

---

### 1.2 Error: "URL not accessible" / "Cannot fetch company website"

**Full Error Message:**
```
ERROR: Unable to fetch https://example-company.com/
HTTP Status: 403 Forbidden
User-Agent blocked or IP rate-limited.

Blueprint Turbo cannot proceed without company website access for Wave 1
intelligence gathering.
```

**Why This Happens:**
- Website blocks automated requests (Cloudflare, bot detection)
- Website requires JavaScript rendering (single-page app)
- Website is behind authentication/paywall
- Temporary network issue or DNS failure

**Solution:**

1. **Check if website is accessible manually:**
   - Open the URL in your browser
   - Does it load without login?
   - Does it redirect to a different domain?

2. **Try alternative URLs:**
   - If `https://company.com` fails, try `https://www.company.com`
   - Try `/about`, `/products`, or `/solutions` pages instead of homepage
   - Try company blog or documentation site

3. **For heavily protected sites:**
   - Use Browser MCP (can handle JavaScript + Cloudflare)
   - Ensure Browser MCP is installed (see [MCP_SETUP.md](./MCP_SETUP.md))
   - Browser MCP uses real Chromium browser, less likely to be blocked

4. **For paywalled/auth-required sites:**
   - Use publicly accessible pages only (blog, marketing pages)
   - OR manually extract company info and provide it inline:
     ```
     /blueprint-turbo https://company.com --override-intel
     ```
     (Then paste company description, ICP, value prop when prompted)

5. **Last Resort - Manual Intelligence Gathering:**
   If automation fails completely, gather Wave 1 intelligence manually:
   - Company offering (from About page, press releases)
   - ICP (from case studies, customer testimonials)
   - Personas (from blog, job postings mentioning roles)
   - Then proceed to data discovery: `/blueprint-data-research`

---

## Section 2: Performance Issues (Slow Execution)

### 2.1 Issue: Execution takes 20-25 minutes instead of 12-15 minutes

**Symptom:**
- Blueprint Turbo completes successfully
- Output quality is good (messages score 8.0+)
- But execution time is 50-70% slower than advertised

**Why This Happens:**
Browser MCP is not installed or not working. Blueprint Turbo falls back to sequential WebFetch calls instead of parallel Browser MCP calls.

**Performance Impact:**
- Wave 1: 0-4 min → 0-7 min (15-20 sequential WebFetch calls)
- Wave 2: 4-9 min → 7-14 min (15-20 sequential WebFetch calls)
- Total: 12-15 min → 20-25 min

**Solution:**

1. **Install Browser MCP:**
   ```bash
   npx @modelcontextprotocol/server-browser
   ```

2. **Configure in Claude:**
   ```json
   {
     "mcpServers": {
       "browser": {
         "command": "npx",
         "args": [
           "@modelcontextprotocol/server-browser"
         ]
       }
     }
   }
   ```

3. **Restart Claude and verify:**
   Ask Claude: "List available MCP tools"

   You should see: `mcp__browser__navigate`, `mcp__browser__get_content`

4. **Re-run Blueprint Turbo:**
   Execution should now complete in 12-15 minutes with parallel calls.

**Note:** Slow execution is non-critical—output quality is identical. Browser MCP is only for speed optimization.

**Full Fix Guide:** See [MCP_SETUP.md](./MCP_SETUP.md#browser-mcp)

---

## Section 3: Synthesis Phase Failures

### 3.1 Error: "Zero HIGH feasibility segments found"

**Full Error Message:**
```
SYNTHESIS PHASE: Zero HIGH feasibility pain segments generated.

After analyzing available data sources from Wave 2, no segments
were rated HIGH feasibility (90-95% confidence with government data).

Data Availability Report Summary:
- Government Data (HIGH feasibility): 0 sources
- Competitive Intelligence (MEDIUM feasibility): 4 sources
- Velocity Signals (MEDIUM feasibility): 2 sources

FALLBACK 1: Attempting MEDIUM feasibility segments (Tier 2 hybrid)...
```

**Why This Happens:**
- Target company's industry has NO government database coverage
- Examples: SaaS, consulting, e-commerce, general B2B services
- Government databases exist primarily for regulated industries (healthcare, manufacturing, food, transportation)

**What Happens Next:**
Blueprint Turbo automatically attempts 3 fallback strategies:

**Fallback 1: MEDIUM Feasibility Segments (Tier 2 Hybrid)**
- Uses competitive intelligence + velocity signals
- Lower confidence (65-75% instead of 90-95%)
- Messages will use hedged language ("estimated," "based on," "suggests")
- Calculation worksheets will disclose estimation methodology

**Fallback 2: Extended Synthesis (+3 minutes)**
- If Fallback 1 fails to generate ≥1 MEDIUM segment, runs additional Sequential Thinking rounds
- Widens search to adjacent industries or hybrid approaches
- May combine multiple MEDIUM sources for stronger segments

**Fallback 3: Adjacent Industry Databases**
- If Fallback 2 fails, searches for tangential government data
- Example: SaaS company → Check if customers (healthcare, manufacturing) have pain points
- Example: Consulting firm → Check if they have physical offices (building violations)

**Expected Outcome:**
- 70% of cases: Fallback 1 succeeds, generates 2-3 MEDIUM segments, continues to Wave 3
- 25% of cases: Fallback 2 succeeds, generates 1-2 MEDIUM segments after extended synthesis
- 5% of cases: All fallbacks fail → See Section 3.2

**When to Expect This:**
- **Always** for: SaaS, consulting, e-commerce, marketing agencies, general B2B
- **Sometimes** for: Retail tech (depends on physical locations), logistics tech (depends on customer industry)
- **Never** for: Healthcare tech, environmental services, manufacturing tech, food service tech

**No Action Needed:** Blueprint Turbo handles this automatically.

---

### 3.2 Error: "All fallbacks exhausted—cannot generate viable segments"

**Full Error Message:**
```
CRITICAL: All synthesis fallbacks exhausted.

After 3 fallback attempts, Blueprint Turbo could not generate ANY
viable pain segments (HIGH or MEDIUM feasibility) for this company.

This typically happens when:
1. Target company operates in an industry with zero public data footprint
2. Company website provides insufficient information about their offering/ICP
3. Company is too early-stage (no customers, no case studies, no public presence)

RECOMMENDATION: This use case is NOT suitable for Blueprint GTM methodology.
Consider alternative GTM approaches (product-led growth, inbound content, partnerships).
```

**Why This Happens:**
- Company is too generic (no specific industry pain points)
- Company is too early-stage (no customer data, no case studies)
- Website provides zero information about ICP/customers
- Industry is completely unregulated with zero competitive intelligence opportunities

**Real-World Examples:**
- Generic "business consulting" firm (no vertical focus)
- Stealth-mode startup (website is just a landing page with email signup)
- Holding company / private equity firm (no operational business)
- Personal brand / individual consultant (no systematic data sources)

**Solution:**

**Option 1: Use Original Blueprint Skills (Manual Stages)**
- Run `/blueprint-company-research <url>` and manually review output
- If Wave 1 intelligence is sufficient, proceed to manual data discovery
- This gives you MORE control to identify creative data approaches

**Option 2: Switch to Different Target Company**
- Blueprint GTM works best with:
  - Clear ICP (vertical, company size, role)
  - Regulated industries OR competitive presence
  - Public customer base (case studies, testimonials)
- Try a different company in your ICP that meets these criteria

**Option 3: Acknowledge This Is Not a Blueprint GTM Use Case**
- Some businesses genuinely don't fit Blueprint methodology
- Consider alternative GTM motions:
  - **Product-Led Growth:** Free tier, self-serve onboarding
  - **Inbound Content:** SEO, thought leadership, community building
  - **Partnerships:** Co-selling with complementary vendors
  - **Traditional Outbound:** Feature-based pitching (yes, the old way)

**When to Pivot:**
If you're getting this error for 3+ companies in your ICP consecutively, Blueprint GTM may not be the right methodology for your market. Reassess your GTM strategy.

---

## Section 4: Message Generation Issues (Wave 3)

### 4.1 Error: "All messages score <8.0/10 - Non-obvious synthesis failure"

**Full Error Message:**
```
WAVE 3 CRITIQUE: All generated messages scored below 8.0/10 threshold.

Primary failure mode: "Non-obvious synthesis" criterion (Texada Test)

Buyer critique summary:
- PQS Message 1: 6.2/10 → "Tells me things I already know about my business"
- PQS Message 2: 5.8/10 → "States obvious facts without connecting dots"
- PVP Message 1: 6.5/10 → "Just describes a situation, doesn't synthesize insight"
- PVP Message 2: 4.9/10 → "This is literally on our About page"

ATTEMPTING REVISION: Generating 2 additional message variants per segment...
```

**Why This Happens:**
The "non-obvious synthesis" criterion from the Texada Test failed. Messages describe facts the prospect already knows instead of synthesizing new insights.

**Common Patterns:**

**❌ Bad (Obvious):**
```
Subject: Your facility has 7 aircraft across 4 manufacturer types

Hi [First Name],

I noticed your Part 135 operation flies:
• 2 Cessna Citation aircraft
• 2 Beechcraft King Air aircraft
• 2 Pilatus PC-12 aircraft
• 1 Embraer Phenom aircraft

This mixed fleet creates maintenance tracking complexity...
```

**Why It Fails:** The operator KNOWS they have a mixed fleet. You're just listing facts from the FAA registry they could pull themselves.

**✅ Good (Non-obvious):**
```
Subject: 5,338 mechanic shortage + your 7-aircraft/4-OEM mix

Hi [First Name],

ATEC projects a 5,338 A&P mechanic shortage by 2026 (only 9,000
new certificates issued vs. 31,000 retiring). Your operation faces
this crisis at 2.5x intensity due to mixed-fleet maintenance:

4 different OEM type certificates = 4 separate parts inventories,
4 training programs, 4 inspection schedules.

Most Part 135 operators simplify to 2 OEMs max. Your 4-OEM mix means
when that mechanic shortage hits, you can't share mechanics across
aircraft—each needs type-specific certification...
```

**Why It Works:** Connects external crisis (mechanic shortage) to specific internal circumstance (4 OEMs) in a way the operator hasn't fully internalized. The synthesis: "2.5x intensity due to mixed-fleet" is non-obvious.

**Solution:**

1. **Identify what the prospect ALREADY knows:**
   - Their own operational details (fleet size, locations, employee count)
   - Industry-wide problems everyone talks about (labor shortages, compliance burden)
   - Their own public data (health inspection scores, CMS ratings they see quarterly)

2. **Find what they DON'T know:**
   - How their specific circumstance amplifies an industry-wide crisis
   - Quantified impact of their situation vs. peers ("2.5x intensity")
   - Non-obvious connections between external events and internal complexity

3. **Revise messages to focus on synthesis:**
   - Stop: "You have X" (they know)
   - Start: "X puts you at 2.5x risk because Y" (synthesis)

   - Stop: "Industry faces Z shortage" (everyone knows)
   - Start: "Z shortage hits your 4-OEM operation harder than single-OEM peers" (synthesis)

4. **Use the Texada Test checklist:**
   - [ ] Hyper-specific (not generic to all prospects)
   - [ ] Factually grounded (verifiable data sources)
   - [ ] **Non-obvious synthesis** (connects dots the prospect hasn't connected)

**Auto-Retry:** Blueprint Turbo automatically generates 2 additional variants and re-critiques. If still failing, manually revise following the patterns above.

**Reference:** See [methodology.md](./prompts/methodology.md) for full Texada Test criteria.

---

### 4.2 Error: "Messages score <8.0/10 - Factually grounded failure"

**Full Error Message:**
```
WAVE 3 CRITIQUE: Messages fail "factually grounded" criterion.

Buyer critique summary:
- PQS Message 1: 6.8/10 → "Claims are unverifiable / feel made up"
- PQS Message 2: 7.2/10 → "Where did the '$312K' number come from?"
- PVP Message 1: 5.5/10 → "No data sources cited, can't verify"
- PVP Message 2: 6.0/10 → "Calculation worksheet missing"
```

**Why This Happens:**
Messages make quantified claims without showing calculation worksheets or citing data sources. Prospects dismiss claims as "made up" when they can't verify your math.

**Common Patterns:**

**❌ Bad (Ungrounded):**
```
Subject: Your DoorDash pricing is costing you $4,200/month

Hi [First Name],

I analyzed your menu pricing and found significant discrepancies
between your website and DoorDash. This is costing you approximately
$4,200 per month in lost revenue.

Happy to explain how I calculated this. Want to chat?
```

**Why It Fails:**
- No data sources cited (which menus? when accessed?)
- No calculation shown (how did you get $4,200?)
- No confidence level disclosed (is this a guess or verifiable?)
- Prospect thinks: "They made this number up to scare me"

**✅ Good (Factually Grounded):**
```
Subject: $4,200/mo menu pricing gap (DoorDash vs. your website)

Hi [First Name],

I compared menu pricing for [Restaurant Name] and noticed your
DoorDash prices are running significantly lower than your website menu.

Top 10 items average $2.15 lower on DoorDash:
• Chicken Parmesan: $14.99 DoorDash vs $17.49 website (-$2.50)
• Margherita Pizza: $12.99 DoorDash vs $14.99 website (-$2.00)
[Continue for 8 more items...]

Based on your Yelp review velocity (18 reviews in last 30 days), I
estimate ~900 monthly DoorDash orders. At $2.15/item average gap,
this represents approximately $4,200/month in lost revenue.

I've attached a calculation worksheet showing exactly how I arrived
at this number—you can verify every step yourself.

---

CALCULATION WORKSHEET: Menu Pricing Revenue Leak

DATA SOURCES:
1. [Restaurant Name] Website Menu (accessed Nov 8, 2025)
   URL: https://[restaurant].com/menu
2. DoorDash Pricing (accessed Nov 8, 2025)
   URL: https://doordash.com/store/[restaurant]
3. Order Volume Estimation
   Source: Yelp review velocity + industry benchmarks

CALCULATION:
Step 1: Pricing gap = $2.15/item average (website vs. DoorDash)
Step 2: Monthly orders = 18 reviews × 50 (Toast 2024 benchmark)
Step 3: Revenue leak = $2.15 × 900 × 1.4 adjustment = $4,200/month

CONFIDENCE LEVEL: 65%
- Hard data: Menu pricing gap (95%)
- Estimation: Order volume (60%)

LIMITATIONS:
- Review velocity may not perfectly correlate with orders
- Does not account for seasonal fluctuations
```

**Why It Works:**
- Data sources cited with URLs and access dates
- Calculation worksheet shows multi-step math
- Confidence level disclosed (65%, not 95%)
- Limitations explicitly stated
- Prospect can verify pricing themselves in 5 minutes

**Solution:**

1. **Always include calculation worksheets for quantified claims:**
   - See [calculation-worksheets.md](./prompts/calculation-worksheets.md) for templates
   - Every number needs a source and formula
   - No shortcuts—show ALL intermediate steps

2. **Cite exact data sources:**
   - Not: "EPA database"
   - Yes: "EPA ECHO (https://echo.epa.gov/), Record ID CAA-05-2024-1234"

   - Not: "Industry benchmarks"
   - Yes: "Toast Restaurant Success Report 2024, page 47"

3. **Disclose confidence levels:**
   - Tier 1 (90-95%): Pure government data
   - Tier 2 (65-75%): Hybrid approaches
   - Tier 3 (50-70%): Pure competitive intelligence
   - Include in every calculation worksheet

4. **Add limitations sections:**
   - What could make your estimate wrong?
   - What assumptions did you make?
   - What's the margin of error?

**Auto-Retry:** Blueprint Turbo detects missing calculation worksheets and regenerates messages with full worksheets included.

**Reference:** See [calculation-worksheets.md](./prompts/calculation-worksheets.md) for all templates.

---

### 4.3 Error: "Messages score <8.0/10 - Wrong persona targeting"

**Full Error Message:**
```
WAVE 3 CRITIQUE: Persona mismatch detected.

Buyer critique summary:
- PQS Message 1: 7.0/10 → "CFO doesn't care about operational details"
- PQS Message 2: 6.5/10 → "Sending asset value message to Dir. of Maintenance?"
- PVP Message 1: 7.3/10 → "Quality metrics, but sent to CMO not CQO"
- PVP Message 2: 6.8/10 → "Technical compliance details for executive audience"
```

**Why This Happens:**
Message content is high-quality, but targeted at the wrong persona. CFOs care about financial impact, not operational details. Directors of Maintenance care about compliance, not asset valuation.

**Persona-Content Mismatch Examples:**

| Persona | ❌ Wrong Content | ✅ Right Content |
|---------|------------------|------------------|
| **CFO** | "Your maintenance tracking is manual" | "Estimated -$2.1M annual VBP penalty" |
| **Dir. of Maintenance** | "Your assets are depreciating" | "2 of 3 inspections cited Violation 7" |
| **Chief Quality Officer** | "Your patient satisfaction is low" | "2-star CMS rating = -$5.1M penalties" |
| **CMO** | "Here are your readmission rates" | "Star rating affects referral pipeline" |

**Solution:**

1. **Match pain point to persona:**

   **Financial Pain → CFO, Finance Director**
   - CMS penalties, VBP reductions, HRRP penalties
   - Menu pricing arbitrage, revenue leaks
   - Compliance fines, settlement costs

   **Operational Pain → Director of Maintenance, Ops Manager**
   - Inspection violations, recurring deficiencies
   - Mechanic shortage impact on mixed fleets
   - Equipment maintenance tracking gaps

   **Compliance/Quality Pain → Chief Quality Officer, Compliance Director**
   - Star rating gaps, readmission rates
   - Deficiency patterns, re-inspection risk
   - Peer comparison (ranked 7th out of 8)

   **Reputation Pain → CMO, CEO**
   - Public star ratings, review declines
   - App store rating drops, sentiment analysis
   - Referral pipeline impact from quality scores

2. **Revise message targeting:**
   - Identify the pain point type (financial, operational, compliance, reputation)
   - Map to appropriate persona
   - Regenerate message with persona-appropriate framing

3. **Use persona-specific language:**
   - CFO: "$2.1M penalty," "0.8% Medicare reimbursement reduction," "cash flow impact"
   - Dir. of Maintenance: "Violation 7 cited 2 of 3 inspections," "recurring deficiency pattern"
   - CQO: "2-star rating," "below state average," "HRRP penalty risk"
   - CMO: "public star rating," "referral pipeline," "competitive disadvantage"

**Auto-Retry:** Blueprint Turbo regenerates messages with corrected persona targeting and appropriate framing.

---

## Section 5: HTML Generation Issues (Wave 4)

### 5.1 Error: "Template file missing or corrupted"

**Full Error Message:**
```
WAVE 4 HTML GENERATION ERROR:

Cannot read template file:
/path/to/.claude/skills/blueprint-turbo/templates/html-template.html

File not found or permissions denied.
```

**Why This Happens:**
- Blueprint Turbo template file was moved/deleted
- File permissions issue (template file not readable)
- Blueprint Turbo installation is incomplete

**Solution:**

1. **Verify template file exists:**
   ```bash
   ls -la /path/to/.claude/skills/blueprint-turbo/templates/
   ```

   You should see: `html-template.html` (approximately 10-15 KB)

2. **If missing, restore from repository:**
   - Re-download Blueprint Turbo skill
   - Or manually copy template from examples directory

3. **Check file permissions:**
   ```bash
   chmod 644 /path/to/.claude/skills/blueprint-turbo/templates/html-template.html
   ```

4. **Re-run Wave 4 only:**
   If Waves 1-3 completed successfully, you can regenerate just the HTML:
   ```
   Please generate the HTML playbook using the messages we just created.
   ```

---

### 5.2 Issue: "Calculation worksheets incomplete or missing from HTML"

**Symptom:**
- HTML playbook generates successfully
- Messages are present
- But calculation worksheets are truncated, missing, or show "[CALCULATION WORKSHEET]" placeholder text

**Why This Happens:**
- Wave 3 messages were generated without full calculation worksheets
- Template population skipped worksheet sections
- Character encoding issue (special characters in worksheets)

**Solution:**

1. **Verify Wave 3 output had complete worksheets:**
   - Scroll through Wave 3 output
   - Each message should have a "CALCULATION WORKSHEET" section with:
     - DATA SOURCES (with URLs)
     - CALCULATION (multi-step)
     - CONFIDENCE LEVEL
     - LIMITATIONS

2. **If worksheets were incomplete in Wave 3:**
   - Regenerate Wave 3 messages:
     ```
     The calculation worksheets are incomplete. Please regenerate the
     messages with full calculation worksheets following the templates
     in calculation-worksheets.md.
     ```

3. **If worksheets exist but didn't populate HTML:**
   - Manually copy worksheets into HTML
   - Edit the generated HTML file
   - Find `[CALCULATION WORKSHEET]` placeholders
   - Replace with actual worksheet content from Wave 3 output

4. **Character encoding issues:**
   - Check for special characters (curly quotes, em dashes, non-ASCII)
   - Replace with ASCII equivalents:
     - "" → "" (straight quotes)
     - — → - (hyphens)
     - × → x (multiplication)

**Prevention:** Always review Wave 3 output BEFORE proceeding to Wave 4. If calculation worksheets are incomplete, fix them before HTML generation.

---

## Section 6: Miscellaneous Issues

### 6.1 Issue: "Blueprint Turbo generates good messages but for wrong ICP"

**Symptom:**
- Execution completes successfully
- Messages score 8.0+/10
- But messages target personas/segments not in your ICP

**Example:**
- You sell to enterprise hospitals (500+ beds)
- Blueprint Turbo generates messages for small rural hospitals (50-100 beds)

**Why This Happens:**
Wave 1 intelligence gathering didn't identify your ICP constraints. Blueprint Turbo defaults to generating messages for ANY prospect with relevant pain points.

**Solution:**

1. **Manually specify ICP constraints when invoking:**
   ```
   /blueprint-turbo https://your-company.com --icp="Enterprise hospitals, 500+ beds, teaching facilities only"
   ```

2. **Review Wave 1 output and correct:**
   - After Wave 1 completes, review the ICP extraction
   - If incorrect, manually provide correct ICP:
     ```
     The ICP should be: [Enterprise hospitals, 500+ beds, teaching facilities]
     Please regenerate data discovery queries for this ICP.
     ```

3. **Filter data sources by ICP in Wave 2:**
   - Some databases allow filtering by facility size
   - Example: CMS Care Compare → Filter for hospitals with 400+ beds
   - Ensure Data Availability Report reflects ICP-specific sources

---

### 6.2 Issue: "Messages are too technical for executive audience"

**Symptom:**
- Messages score well on data credibility and factual grounding
- But language is too technical/jargon-heavy for C-suite

**Example:**
```
Subject: PSI-90 composite score 1.2 standard deviations above AHRQ benchmark

Hi [CFO First Name],

Your facility's Patient Safety Indicator (PSI-90) composite score
of 0.87 is 1.2 standard deviations above the AHRQ national benchmark
of 0.73, indicating elevated adverse event rates across 10 safety domains...
```

**Why It's a Problem:**
CFOs don't speak PSI-90 language. They speak dollars and percentages.

**Solution:**

1. **Translate technical metrics to business impact:**

   Before:
   ```
   PSI-90 composite score 0.87 vs. 0.73 benchmark
   ```

   After:
   ```
   Safety score 18% above national average → Estimated -$1.2M HVBP penalty
   ```

2. **Lead with dollars, add technical details in footnote:**

   ```
   Subject: -$1.2M safety penalty risk (PSI-90 score)

   Hi [CFO First Name],

   Your facility's safety metrics are tracking 18% above the national
   average, which puts you at risk for a -$1.2M HVBP penalty in Q4 2026.

   Specifically, your PSI-90 composite score of 0.87 (vs. 0.73 national
   benchmark) indicates elevated adverse event rates...
   ```

3. **Use executive-friendly calculation worksheets:**
   - Start with bottom-line impact
   - Then show technical calculation
   - Don't assume familiarity with CMS acronyms

**Reference:** See [methodology.md](./prompts/methodology.md) for persona-appropriate language guidance.

---

## Getting Additional Help

**If your issue isn't covered here:**

1. **Check other documentation:**
   - [README.md](./README.md) - Quick start and overview
   - [SKILL.md](./SKILL.md) - Full methodology documentation
   - [MCP_SETUP.md](./MCP_SETUP.md) - MCP server troubleshooting
   - [methodology.md](./prompts/methodology.md) - Message critique rubric
   - [calculation-worksheets.md](./prompts/calculation-worksheets.md) - Worksheet templates

2. **Review example playbooks:**
   - [examples/example-playbook-healthcare.html](./examples/example-playbook-healthcare.html) - Tier 1 (government data)
   - [examples/example-playbook-owner-com.html](./examples/example-playbook-owner-com.html) - Tier 2 (hybrid)
   - Compare your output to these benchmarks

3. **Enable debug mode:**
   ```
   /blueprint-turbo https://company.com --debug
   ```
   This outputs additional diagnostic information at each wave.

4. **File an issue:**
   - Repository: [Your Blueprint Turbo Repo]
   - Include:
     - Full error message
     - Company URL you were analyzing
     - MCP server status (installed/not installed)
     - Execution time (to diagnose performance issues)
     - Wave where failure occurred (1, 2, Synthesis, 3, or 4)

---

## Diagnostic Checklist

Before filing an issue, run through this checklist:

**MCP Servers:**
- [ ] Sequential Thinking MCP installed and verified
- [ ] Browser MCP installed (optional but recommended)
- [ ] Claude restarted after MCP configuration changes

**Target Company:**
- [ ] URL is publicly accessible (no auth required)
- [ ] Website contains information about offering/ICP
- [ ] Company operates in an industry with some public data footprint

**Execution Environment:**
- [ ] Node.js 18+ installed
- [ ] Internet connectivity working
- [ ] Sufficient execution time allowed (12-15 minutes minimum)

**Output Quality:**
- [ ] Messages include calculation worksheets
- [ ] Data sources cited with URLs
- [ ] Confidence levels disclosed
- [ ] Persona targeting is appropriate

**If all checkboxes pass and issue persists:**
File a detailed bug report with error messages and diagnostic output.

---

**Version:** 1.0.0 (November 2025)

**Last Updated:** November 2025

**Maintainer:** Blueprint GTM
