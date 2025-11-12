# Blueprint GTM Skills System v1.1.0 - Distribution Package

**Transform company URLs into data-driven GTM intelligence using hard government data sources.**

This package contains 6 Claude Code skills that implement the Blueprint GTM methodology.

---

## What's Included

### Individual Skills (Individual-Skills/)

1. **blueprint-turbo.zip** (12-15 min execution)
   - Fast workflow optimized for sales calls
   - 4-wave parallel architecture
   - Requires: Browser MCP + Sequential Thinking MCP
   - Output: HTML playbook with validated messages

2. **blueprint-company-research.zip** (Stage 1)
   - Live website analysis
   - ICP and persona research
   - 3-5 pain segment hypotheses
   - Hard data emphasis

3. **blueprint-data-research.zip** (Stage 2)
   - Government database discovery
   - Field-level documentation
   - Feasibility ratings
   - Alternative segment suggestions

4. **blueprint-message-generation.zip** (Stage 3)
   - Message variant generation
   - Buyer role-play critique
   - Texada Test validation
   - TRUE PVP (8.5+) vs Strong PQS (7.0-8.4) classification

5. **blueprint-explainer-builder.zip** (Stage 4)
   - Mobile-responsive HTML generation
   - Before/after comparison
   - Data source citations
   - Blueprint branding

6. **blueprint-gtm-complete.zip** (All-in-one)
   - Chains all 4 stages automatically
   - 30-45 minute execution
   - No MCP servers required
   - Complete workflow

### Complete Bundle (Complete-Bundle/)

**blueprint-skills-bundle-v1.1.0.zip** - All 6 skills in one package

---

## Installation Instructions

### Option 1: Claude Desktop (App) Installation

**For individual skills:**

1. Open **Claude Desktop** application
2. Go to **Settings** → **Capabilities** → **Skills**
3. Click **"Upload skill"** button
4. Navigate to `Individual-Skills/` folder
5. Select a .zip file (e.g., `blueprint-turbo.zip`)
6. Click **Open** - skill installs automatically
7. Repeat for each skill you want to install

**For bundle installation:**

1. **Unzip** `blueprint-skills-bundle-v1.1.0.zip` first
2. Upload each skill folder individually (Claude Desktop uploads one at a time)

**Verification:**
- Installed skills appear in Settings → Skills list
- Skills are immediately available for use

---

### Option 2: Claude Code (CLI) Installation

**For individual skills:**

1. **Unzip** the skill file:
   ```bash
   cd ~/Downloads
   unzip blueprint-turbo.zip
   ```

2. **Copy to skills directory:**
   ```bash
   mkdir -p ~/.claude/skills
   cp -r blueprint-turbo ~/.claude/skills/
   ```

3. **Verify installation:**
   ```bash
   ls ~/.claude/skills/blueprint-turbo
   # Should show: SKILL.md, LICENSE.md, and subfolders
   ```

4. **Restart Claude Code** (if running)

**For bundle installation:**

1. **Unzip the bundle:**
   ```bash
   cd ~/Downloads
   unzip blueprint-skills-bundle-v1.1.0.zip -d blueprint-bundle
   ```

2. **Copy all skills at once:**
   ```bash
   mkdir -p ~/.claude/skills
   cp -r blueprint-bundle/blueprint-* ~/.claude/skills/
   ```

3. **Verify installation:**
   ```bash
   ls ~/.claude/skills
   # Should show all 6 skill directories
   ```

**Verification:**
- Open a terminal in any project directory
- Claude Code automatically discovers skills in `~/.claude/skills/`
- Skills are ready to use immediately

---

## Quick Start Guide

### Blueprint Turbo (Fast Workflow)

**Requirements:**
- Browser MCP server installed
- Sequential Thinking MCP server installed
- See `.claude/skills/blueprint-turbo/docs/MCP_SETUP.md` after installation

**Usage:**
```bash
/blueprint-turbo https://company.com
```

**Output:** HTML playbook in 12-15 minutes

---

### Original Skills (Thorough Workflow)

**Requirements:**
- No MCP servers needed
- Internet access for WebFetch/WebSearch

**Usage:**
```bash
"Run Blueprint GTM analysis for https://company.com"
```

**What happens:**
1. Claude invokes `blueprint-company-research` skill
2. Upon completion, auto-invokes `blueprint-data-research`
3. Upon finding HIGH feasibility segments, auto-invokes `blueprint-message-generation`
4. Upon validation, auto-invokes `blueprint-explainer-builder`
5. Delivers HTML playbook

**Output:** HTML playbook in 30-45 minutes

---

## What's New in v1.1.0

### Major Update: PVP vs Strong PQS Classification

**Key Changes:**

1. **TRUE PVP threshold raised**: 8.0+ → 8.5+
   - Must include complete actionable information (names, contacts, prices, dates)
   - Passes "Independently Useful Test" (recipient can act WITHOUT replying)

2. **Strong PQS range defined**: 7.0-8.4
   - Excellent pain identification with specificity
   - Requires reply to be valuable (starts conversation)

3. **Realistic expectations**: Most segments generate Strong PQS (7.0-8.4) - this is success!

4. **Action Extraction Phase**: New validation before buyer critique

5. **Updated examples**: TRUE PVP examples added (Floorzap, Skimmer)

**Why this matters:**
- Previous version called all 8.0+ messages "PVPs"
- v1.1.0 distinguishes between TRUE PVPs (8.5+, independently useful) and Strong PQS (7.0-8.4, conversation starters)
- Both are valuable - don't be disappointed by Strong PQS scores!

---

## Workflow Comparison

| Factor | Blueprint Turbo | Original Skills |
|--------|----------------|-----------------|
| **Speed** | 12-15 minutes | 30-45 minutes |
| **Execution** | `/blueprint-turbo URL` | Auto-chains 4 stages |
| **Parallelization** | 15-20 calls per wave | Sequential |
| **MCP Required** | Yes (2 servers) | No |
| **Quality** | Same (buyer-validated) | Same (buyer-validated) |
| **Use Case** | Sales calls, fast turnaround | Strategic analysis, depth |

**Choose based on:**
- Need it during a sales call? → **Turbo**
- Want maximum thoroughness? → **Original Skills**
- Don't have MCP servers? → **Original Skills**

---

## Support and Documentation

### After Installation

**Full documentation available in installed skills:**

- **Blueprint Turbo**: `~/.claude/skills/blueprint-turbo/README.md`
- **Methodology Reference**: `~/.claude/skills/blueprint-turbo/prompts/methodology.md`
- **Troubleshooting**: `~/.claude/skills/blueprint-turbo/docs/TROUBLESHOOTING.md`
- **MCP Setup**: `~/.claude/skills/blueprint-turbo/docs/MCP_SETUP.md`

### Key Resources

**Understanding the Methodology:**
- Every skill includes `references/methodology.md` with complete v1.1.0 methodology
- Covers PVP vs Strong PQS, scoring rubrics, Texada Test, data tier framework

**Examples:**
- Blueprint Turbo includes example playbooks in `examples/` folder
- See real-world outputs for Owner.com and healthcare provider

**Troubleshooting:**
- Common issues and solutions in `docs/TROUBLESHOOTING.md`
- Performance optimization tips
- Fallback strategies

---

## License Information

**Copyright © 2025 Jordan Crawford. All rights reserved.**

Each skill includes a `LICENSE.md` file with:
- Permitted use terms
- Redistribution restrictions
- Attribution requirements
- Data compliance guidelines

**Key Terms:**
- ✅ Use for your own GTM analysis and client projects
- ✅ Share HTML playbooks with clients
- ✅ Modify for internal use
- ❌ No redistribution without authorization
- ❌ No commercial resale of skills
- ❌ Attribution required for public discussion

**Full license:** See `LICENSE.md` in each skill folder

---

## Philosophy

This system embodies Jordan Crawford's Blueprint GTM methodology:

> "The message isn't the problem. The LIST is the message."

**Core Principles:**
- Hard data beats clever copy
- Government databases with record numbers
- Buyer role-play validation required
- Realistic expectations: Strong PQS (7.0-8.4) is success
- TRUE PVPs (8.5+) are rare and require specific data

---

## Version History

**v1.1.0** (November 2025)
- PVP vs Strong PQS classification system
- Independently Useful Test added
- Action Extraction phase implemented
- Realistic expectations documented
- methodology.md updated across all skills

**v1.0.0** (October 2025)
- Initial release
- 4-stage workflow established
- Blueprint Turbo parallel architecture
- Hard data emphasis throughout

---

## Getting Started

1. **Install skills** using instructions above
2. **Choose your workflow:**
   - Fast: `/blueprint-turbo https://company.com`
   - Thorough: `"Run Blueprint GTM analysis for https://company.com"`
3. **Review the HTML playbook** delivered
4. **Iterate** on segments or messages as needed
5. **Deploy** with confidence

**Remember:** Most excellent messages are Strong PQS (7.0-8.4), not TRUE PVPs (8.5+). Both are valuable. Celebrate Strong PQS as success!

---

## Questions?

Refer to documentation in installed skills:
- README files in each skill
- `references/methodology.md` for complete methodology
- `docs/TROUBLESHOOTING.md` for common issues

**Contact:** [Your contact information]

---

**That's Blueprint GTM v1.1.0.**
