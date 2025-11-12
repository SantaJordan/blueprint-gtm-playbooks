# Blueprint GTM Skills - Licensed Copy

## License Information

**Licensed to:** [CUSTOMER_NAME]
**Email:** [CUSTOMER_EMAIL]
**License Key:** [LICENSE_KEY]
**Issue Date:** [ISSUE_DATE]

---

## Installation Instructions

### For Claude Code Desktop App (macOS/Windows)

#### macOS:

1. Open **Finder**
2. Press `Cmd + Shift + .` to show hidden files
3. Navigate to your home directory (`~` or `/Users/yourusername`)
4. Look for the `.claude` folder
   - If it doesn't exist, create it: `mkdir ~/.claude`
5. Open the `.claude` folder
6. Look for a `skills` folder inside
   - If it doesn't exist, create it: `mkdir ~/.claude/skills`
7. Copy the `skills` folder contents from this download into `~/.claude/skills/`
8. Your directory structure should look like:
   ```
   ~/.claude/skills/
   ├── blueprint-company-research/
   ├── blueprint-data-research/
   ├── blueprint-message-generation/
   └── blueprint-explainer-builder/
   ```
9. **Restart Claude Code** completely
10. Skills are now available! 🎉

#### Windows:

1. Open **File Explorer**
2. Type `%USERPROFILE%` in the address bar and press Enter
3. Look for the `.claude` folder
   - If it doesn't exist, create it
4. Open the `.claude` folder
5. Look for a `skills` folder inside
   - If it doesn't exist, create it
6. Copy the `skills` folder contents from this download into `.claude\skills\`
7. **Restart Claude Code** completely
8. Skills are now available! 🎉

### For Claude Code CLI

```bash
# Copy skills to your home directory
cp -r .claude/skills/* ~/.claude/skills/

# Verify installation
ls -la ~/.claude/skills/

# You should see:
# blueprint-company-research/
# blueprint-data-research/
# blueprint-message-generation/
# blueprint-explainer-builder/

# Restart your CLI session
# Skills are now available!
```

### Verifying Installation

Open Claude Code and type:
```
Can you list the available skills?
```

You should see all 4 Blueprint GTM skills listed.

---

## Available Skills

### 1. 🔍 Blueprint Company Research

**Purpose:** Research companies to identify pain-qualified segments, ideal customer profile, and target personas.

**When to use:** Starting a new GTM analysis for a company

**What it does:**
- Visits live company website
- Analyzes products/services
- Identifies ideal customer profile (ICP)
- Maps pain-qualified segments
- Generates target personas
- Outputs structured research report

**How to invoke:**
```
I need to research [Company Name] at [company-url.com] for GTM intelligence.
```

**Example output:**
- Company overview
- Product/service analysis
- ICP definition
- 5-7 pain-qualified segments
- Target personas with pain points
- Next steps for data validation

---

### 2. 📊 Blueprint Data Research

**Purpose:** Validate pain-qualified segments with hard public data sources (EPA ECHO, OSHA, FDA, FMCSA, permits, violations).

**When to use:** After completing company research

**What it does:**
- Takes pain segments from company research
- Identifies relevant public data sources
- Creates field-level data recipes
- Shows exactly how to identify companies in painful situations
- Validates segment viability with real data
- Outputs actionable targeting criteria

**How to invoke:**
```
I want to validate the pain segments we identified for [Company Name] with public data sources.
```

**Example output:**
- Data source recommendations per segment
- Field-level recipes (which fields = pain)
- SQL/API query examples
- Data quality assessment
- Segment prioritization
- Implementation roadmap

---

### 3. ✍️ Blueprint Message Generation

**Purpose:** Generate and validate PQS/PVP outreach messages using buyer role-play critique.

**When to use:** After completing data research

**What it does:**
- Takes validated pain segments
- Generates 5-7 message variants per type (PQS & PVP)
- Critiques each message from buyer perspective
- Scores messages on relevance, specificity, value
- Returns only top 2-3 messages scoring 8+/10
- Outputs ready-to-use outreach copy

**How to invoke:**
```
I need to generate outreach messages for the pain segments we validated for [Company Name].
```

**Example output:**
- Pain-Qualified Statement (PQS) messages
- Painful Value Proposition (PVP) messages
- Buyer critique for each variant
- Scores and rankings
- Final top messages ready to deploy
- A/B testing recommendations

---

### 4. 📄 Blueprint Explainer Builder

**Purpose:** Create mobile-responsive HTML explainer document that teaches Blueprint GTM methodology through company-specific examples.

**When to use:** After completing message generation (final step)

**What it does:**
- Synthesizes all previous research
- Creates beautiful HTML document
- Shows transformation from generic → data-driven
- Includes company-specific PQS/PVP examples
- Mobile-responsive design
- Ready to share with stakeholders

**How to invoke:**
```
I want to create an explainer document for the Blueprint GTM analysis we completed for [Company Name].
```

**Example output:**
- Standalone HTML file
- Methodology overview
- Company-specific examples
- Before/after comparisons
- Visual design elements
- Shareable with clients/team

---

## Skill Workflow

**Recommended sequence:**

```
1. Company Research
   ↓
2. Data Research
   ↓
3. Message Generation
   ↓
4. Explainer Builder
```

Each skill builds on the output of the previous one. Follow this order for best results.

**Time investment:**
- Company Research: 15-30 minutes
- Data Research: 20-40 minutes
- Message Generation: 15-25 minutes
- Explainer Builder: 10-15 minutes

**Total:** 60-110 minutes for complete Blueprint GTM analysis

---

## Tips for Best Results

### General Best Practices

1. **Be specific:** Provide company URLs, not just names
2. **Provide context:** Share what you already know about the company
3. **Review outputs:** Skills provide starting points, refine with your expertise
4. **Iterate:** You can re-run skills with different parameters
5. **Save outputs:** Copy results to your notes/CRM

### Company Research Tips

- Provide the actual company website URL
- Mention the specific product/service you're targeting (if multi-product company)
- Share any existing knowledge about their customers
- Let the skill visit the live website for current info

### Data Research Tips

- Review the pain segments from Company Research first
- Focus on 2-3 top segments (not all 7)
- Verify data source availability in your region
- Consider data acquisition costs in your decision

### Message Generation Tips

- Be patient - the skill generates and critiques multiple variants
- Pay attention to the buyer critique reasoning
- Test the top 2-3 messages in real campaigns
- A/B test to find your winner
- Adapt the language to your brand voice

### Explainer Builder Tips

- Run this last, after all other skills
- Review the HTML output in a browser
- Customize colors/branding if needed (edit HTML)
- Use this to pitch clients or educate your team
- Great for case studies and testimonials

---

## Troubleshooting

### Skills Not Appearing

**Problem:** Claude Code doesn't recognize the skills

**Solutions:**
1. Verify files are in correct location: `~/.claude/skills/`
2. Check that each skill folder has a `SKILL.md` file
3. Restart Claude Code completely (quit and reopen)
4. Check Claude Code logs for errors:
   - macOS: `~/Library/Logs/Claude Code/`
   - Windows: `%APPDATA%\Claude Code\logs\`

### Skill Execution Errors

**Problem:** Skill starts but encounters errors

**Solutions:**
1. Check that you provided all required information
2. Verify company URL is accessible (not behind auth)
3. Try re-running with more specific instructions
4. Check Claude Code has internet access (for website visits)

### Installation Path Issues

**Problem:** Can't find `.claude` folder

**Solutions:**

**macOS:**
```bash
# Show hidden files in Finder
defaults write com.apple.finder AppleShowAllFiles YES
killall Finder

# Or use terminal
cd ~
mkdir -p .claude/skills
```

**Windows:**
```powershell
# Show hidden files in File Explorer
# View → Show → Hidden items (checkbox)

# Or use Command Prompt
cd %USERPROFILE%
mkdir .claude\skills
```

### Permission Errors

**Problem:** Can't copy files to `.claude/skills/`

**Solutions:**

**macOS:**
```bash
# Fix permissions
chmod -R 755 ~/.claude/skills/
```

**Windows:**
Run as Administrator or check folder permissions in Properties

### Skill Updates Not Showing

**Problem:** Downloaded new version but seeing old skill

**Solutions:**
1. Delete old skill folder completely
2. Copy new skill folder
3. Restart Claude Code
4. Verify by checking skill version (if mentioned in SKILL.md)

---

## License Terms (Summary)

### ✅ You MAY:

- ✅ Use these skills on unlimited personal devices (laptop, desktop, etc.)
- ✅ Create unlimited outputs and deliverables for your clients
- ✅ Reference the Blueprint GTM methodology in your work
- ✅ Request support via email (see below)
- ✅ Receive free updates for 12 months from purchase date

### ❌ You MAY NOT:

- ❌ Share these skills with team members (separate licenses required)
- ❌ Post these skills publicly (GitHub, forums, websites, etc.)
- ❌ Modify and redistribute these skills
- ❌ Remove or alter license watermarks
- ❌ Resell or sublicense these skills
- ❌ Use these skills to create competing products

### 📧 Team Licenses Available

Need licenses for your team? We offer significant discounts:

**Team Pricing:**
- **3-person team:** $997 (save $194 vs. individual licenses)
- **5-person team:** $1,497 (save $488)
- **Unlimited agency:** $2,997 (unlimited users)

Contact us to upgrade: **support@blueprintgtm.com**

---

## Support & Updates

### Getting Help

**Email Support:** support@blueprintgtm.com

**Response Time:** Within 24 hours (Monday-Friday, business hours)

**What to include in support requests:**
- Your license key (found at top of this README)
- Detailed description of issue
- Screenshots if applicable
- Operating system and Claude Code version

### Updates

You're entitled to **free updates for 12 months** from purchase date.

**Update notifications:**
- Sent via email to [CUSTOMER_EMAIL]
- Check your dashboard at [platform URL]
- Download latest version using same link

**What gets updated:**
- Bug fixes and improvements
- New features and capabilities
- Additional skills (as bonuses)
- Documentation updates

**How to update:**
1. Download latest version
2. Delete old skill folders
3. Copy new skill folders to `~/.claude/skills/`
4. Restart Claude Code

### Feature Requests

Have ideas for improvements? We'd love to hear them!

Email us at: **support@blueprintgtm.com**

Subject: "Feature Request - [Your Idea]"

We review all requests and prioritize based on customer demand.

---

## Community & Resources

### Private Community (Course Members Only)

If you purchased the Blueprint GTM Masterclass, you have access to:

- **Private Slack/Discord channel**
- **Monthly office hours** (live Q&A)
- **Implementation workshops**
- **Peer support** from other GTM professionals
- **Early access** to new skills and features

Access link: [provided in course dashboard]

### Resources

- **Video Tutorials:** [link to course videos if applicable]
- **Case Studies:** [link to examples]
- **Methodology Guide:** [link to full methodology]
- **Data Source Directory:** [link to public data resources]

---

## Legal Notice

These skills contain proprietary methodology and are protected by copyright law.

**Copyright © 2025 Blueprint GTM. All rights reserved.**

Unauthorized distribution is prohibited and traceable. Each file contains unique identifiers linked to your license: **[LICENSE_KEY]**

Any violations may result in:
- Immediate license termination (no refund)
- Legal action for damages
- Public notice to community

We monitor for unauthorized sharing via automated systems and Google Alerts.

**Questions about licensing?** Contact: support@blueprintgtm.com

---

## Feedback & Testimonials

We'd love to hear about your experience using Blueprint GTM skills!

**Share your results:**
- Email: support@blueprintgtm.com
- Subject: "Success Story"

**What to share:**
- Company/industry you targeted
- Results achieved (meetings booked, revenue generated, etc.)
- Specific ways the skills helped
- Permission to use as testimonial (optional)

**Incentive:** Best success stories receive:
- Feature on our website
- Free upgrade to next tier
- Exclusive bonus skills
- Priority support for life

---

## Quick Reference Card

**Installation Path:**
- macOS: `~/.claude/skills/`
- Windows: `%USERPROFILE%\.claude\skills\`

**Skill Sequence:**
1. Company Research → 2. Data Research → 3. Message Generation → 4. Explainer Builder

**Support Email:** support@blueprintgtm.com

**Your License Key:** [LICENSE_KEY]

**Update Check:** [Platform dashboard URL]

**Documentation:** [Your website URL]

---

## Thank You! 🎉

Thank you for purchasing Blueprint GTM Skills!

We're excited to see how you transform your go-to-market strategy with AI-powered intelligence. These skills represent years of GTM experience distilled into actionable tools.

**Don't hesitate to reach out** if you need any help. We're here to make sure you succeed.

**Ready to get started?** Install the skills following the instructions above, then open Claude Code and invoke your first skill:

```
I need to research [Company Name] at [company-url.com] for GTM intelligence.
```

Let's build something amazing together!

---

**Questions?** support@blueprintgtm.com

*© 2025 Blueprint GTM. All rights reserved.*
*Licensed to: [CUSTOMER_NAME] ([LICENSE_KEY])*
