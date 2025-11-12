# Blueprint GTM Skills - Distribution Guide

## Table of Contents

1. [Quick Start (Recommended: Podia)](#quick-start-podia)
2. [Alternative: Gumroad Setup](#alternative-gumroad)
3. [Alternative: GitHub Private + Stripe](#alternative-github-stripe)
4. [Watermarking Process](#watermarking-process)
5. [Pricing Recommendations](#pricing-recommendations)
6. [Legal Protection](#legal-protection)
7. [Handling Piracy](#handling-piracy)

---

## Quick Start: Podia (Recommended)

**Why Podia?** Best balance of features, pricing, and protection for course + downloadable skills.

### Setup (30-60 minutes)

#### Step 1: Create Account

1. Go to [podia.com](https://podia.com)
2. Sign up for **Shaker Plan** ($89/month, 0% transaction fees)
3. Complete profile setup

#### Step 2: Create Your Product

**Option A: Full Course (Recommended - $997)**

1. Click "Products" → "New Course"
2. Enter details:
   - **Name:** "Blueprint GTM Masterclass"
   - **Price:** $997
   - **Description:** Your sales page copy
3. Create modules:
   - Module 1: Blueprint Methodology Overview
   - Module 2: Company Research (+ skill download)
   - Module 3: Data Research (+ skill download)
   - Module 4: Message Generation (+ skill download)
   - Module 5: Explainer Builder (+ skill download)
   - Module 6: Implementation Labs

**Option B: Digital Downloads Only ($397)**

1. Click "Products" → "New Digital Download"
2. Enter details:
   - **Name:** "Blueprint GTM Skills Bundle"
   - **Price:** $397
   - **Description:** What's included
3. Attach your watermarked ZIP files

#### Step 3: Configure Downloads

1. Go to product settings
2. Set **Download Limit:** 5 attempts
3. Enable **Unique Download Links:** Yes
4. Set **Link Expiration:** 7 days (optional)

#### Step 4: Add Watermarked Files

**Per Customer Watermarking:**

1. When customer purchases, you'll receive email notification
2. Run watermarking script:
   ```bash
   ./watermark-skills.sh customer@email.com "Customer Name" BPGTM-2025-XXXXX
   ```
3. Upload watermarked ZIPs to that customer's order in Podia
4. Customer receives download link

**Bulk Processing (Advanced):**
- Set up Zapier integration
- Auto-generate license keys
- Trigger watermarking script via webhook
- Upload to customer's order automatically

#### Step 5: Create Sales Page

1. Add compelling headline
2. Explain Blueprint GTM methodology value
3. Show example outputs
4. Add testimonials (after first cohort)
5. Include FAQ section
6. Add clear CTA button

#### Step 6: Set Up Email Sequences

**Purchase Confirmation:**
```
Subject: Welcome to Blueprint GTM Masterclass! 🎉

Hi [Name],

Thank you for enrolling in Blueprint GTM Masterclass!

Your skills are ready to download:
[Download Link - Expires in 7 days]

Installation instructions:
1. Download the bundle
2. Follow the README.md instructions
3. Restart Claude Code

Need help? Reply to this email.

Best,
[Your Name]
```

**Day 3 Follow-up:**
```
Subject: How are the skills working for you?

Hi [Name],

Just checking in! Have you had a chance to install the Blueprint GTM skills?

If you're stuck, here are common solutions:
[Link to troubleshooting guide]

Reply with any questions - I'm here to help!

Best,
[Your Name]
```

**Week 2: Upsell Implementation Services:**
```
Subject: Ready to accelerate your results?

Hi [Name],

I've been working with clients to implement Blueprint GTM and seeing
amazing results...

Would you be interested in a done-with-you implementation session?

[Book a call]

Best,
[Your Name]
```

### Monthly Costs: $89

### Expected Revenue Protection: 60-70%

---

## Alternative: Gumroad

**Why Gumroad?** Fastest setup, lowest barrier to entry, creator-friendly.

### Setup (10-20 minutes)

#### Step 1: Create Account

1. Go to [gumroad.com](https://gumroad.com)
2. Sign up (free, no monthly fee)
3. Connect bank account for payouts

#### Step 2: Create Products

**Individual Skills:**

1. Click "Create" → "Product"
2. Enter details:
   - **blueprint-company-research** - $97
   - **blueprint-data-research** - $147
   - **blueprint-message-generation** - $147
   - **blueprint-explainer-builder** - $97
3. Upload non-watermarked ZIPs (you'll watermark per-order)
4. Write product descriptions
5. Add cover images

**Bundle:**

1. Create new product: "Blueprint GTM Skills Bundle"
2. Price: $397 (save $91)
3. Include all 4 skills
4. Upload bundle ZIP

#### Step 3: Configure Settings

1. Enable **File Protection:** Unique download links
2. Set **Download Limit:** 3 attempts
3. Add **License Terms** to product description
4. Create customer README with license info

#### Step 4: Manual Watermarking Process

**Per Order:**

1. Receive purchase notification email
2. Extract customer details (email, name)
3. Generate license key: `BPGTM-2025-[RANDOM]`
4. Run watermarking script:
   ```bash
   ./watermark-skills.sh customer@email.com "Name" BPGTM-2025-XXXXX
   ```
5. Go to Gumroad order page
6. Replace uploaded file with watermarked version
7. Customer gets new download link automatically

**Automation Option:**
- Use Gumroad webhooks
- Trigger serverless function (AWS Lambda, Vercel)
- Auto-generate watermarks
- Update download link via API

#### Step 5: Create Product Pages

**Effective Gumroad Copy Structure:**

```markdown
# Blueprint GTM Skills - [Skill Name]

Transform your GTM strategy with AI-powered intelligence.

## What You Get
- Claude Code skill (ready to install)
- Installation guide
- Example outputs
- Video walkthrough

## Who This Is For
- GTM consultants
- Sales leaders
- Growth teams

## How It Works
[Brief explanation]

## Installation
Works with Claude Code desktop app and CLI.
Full instructions included.

## License
Personal license - single user.
Team licenses available.

## Support
Email support included.
Response within 24 hours.
```

### Monthly Costs: $0 (9% transaction fee)

### Expected Revenue Protection: 40-50%

---

## Alternative: GitHub Private + Stripe

**Why This?** Developer audience, git-based updates, lowest transaction fees.

### Setup (2-4 hours technical work)

#### Step 1: Create Private GitHub Repository

1. Go to GitHub
2. Create new **private repository**: `blueprint-gtm-skills`
3. Push your skills:
   ```bash
   cd .claude/skills
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin git@github.com:yourusername/blueprint-gtm-skills.git
   git push -u origin main
   ```

#### Step 2: Set Up Stripe

1. Create [Stripe account](https://stripe.com)
2. Create product: "Blueprint GTM Skills"
3. Set price: $397
4. Enable payment links or use Stripe Checkout

#### Step 3: Automate Access Control

**Option A: Manual (Simple)**

1. Customer pays via Stripe
2. You receive webhook notification
3. Manually invite customer to GitHub repo
4. Customer clones repository

**Option B: Automated (Advanced)**

Create serverless function (Vercel/Netlify):

```javascript
// api/grant-access.js
import Stripe from 'stripe';
import { Octokit } from '@octokit/rest';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

export default async function handler(req, res) {
  // Verify Stripe webhook
  const sig = req.headers['stripe-signature'];
  const event = stripe.webhooks.constructEvent(
    req.body,
    sig,
    process.env.STRIPE_WEBHOOK_SECRET
  );

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const customerEmail = session.customer_email;

    // Invite to GitHub repo
    await octokit.repos.addCollaborator({
      owner: 'yourusername',
      repo: 'blueprint-gtm-skills',
      username: customerEmail, // Requires GitHub username
      permission: 'pull'
    });

    // Send welcome email with clone instructions
    // ... email logic
  }

  res.status(200).json({ received: true });
}
```

#### Step 4: Watermarking with Git

**Strategy:** Create customer-specific branch

```bash
# For each customer
CUSTOMER_ID="cust-123"
git checkout -b customer-${CUSTOMER_ID}

# Run watermarking
./watermark-skills.sh customer@email.com "Name" BPGTM-2025-XXXXX

# Commit watermarked version
git add .
git commit -m "Watermarked for customer ${CUSTOMER_ID}"
git push origin customer-${CUSTOMER_ID}

# Customer clones their branch
# You send: git clone -b customer-123 https://github.com/you/blueprint-gtm-skills.git
```

#### Step 5: Handle Updates

**Updating All Customers:**

```bash
# Update main branch
git checkout main
git add [updated files]
git commit -m "Add new feature X"
git push

# Merge into all customer branches
for branch in $(git branch -r | grep customer-); do
  git checkout ${branch#origin/}
  git merge main
  git push
done

# Notify customers via email
# "New updates available! Run: git pull"
```

### Monthly Costs: $0 (Stripe 2.9% + $0.30)

### Expected Revenue Protection: 50-60%

### Limitations:
- GitHub Free: Only 3 collaborators on organization repos
- Requires GitHub Pro ($4/user/month) for more collaborators
- Customers must have GitHub accounts
- Not ideal for non-technical users

---

## Watermarking Process

### Quick Reference

```bash
# Generate license key (format: BPGTM-YYYY-XXXXX)
LICENSE_KEY="BPGTM-2025-$(openssl rand -hex 3 | tr '[:lower:]' '[:upper:]')"

# Run watermarking
./watermark-skills.sh \
  "customer@email.com" \
  "Customer Name" \
  "${LICENSE_KEY}"

# Output created:
# - watermarked-skills-[timestamp]/
# - blueprint-skills-bundle-[LICENSE].zip
# - [skill-name]-[LICENSE].zip (x4)
```

### What Gets Watermarked

Each `SKILL.md` file gets these lines added to frontmatter:

```yaml
---
name: blueprint-company-research
description: Research companies...
# Licensed to: Jordan Crawford (jordan@example.com)
# License Key: BPGTM-2025-A7F3G9
# Distribution of this file is prohibited without authorization
---
```

### License Key Format

**Pattern:** `BPGTM-YYYY-XXXXX`

- `BPGTM` = Blueprint GTM (product identifier)
- `YYYY` = Year (2025, 2026, etc.)
- `XXXXX` = Random hex (A7F3G9, etc.)

**Why this format:**
- Easy to identify in leaked files
- Year helps track when license was issued
- Random hex ensures uniqueness
- Searchable on Google/GitHub

### Tracking Watermarks

Create a spreadsheet to log all issued licenses:

| Date | Customer Name | Email | License Key | Platform | Order ID |
|------|--------------|-------|-------------|----------|----------|
| 2025-01-15 | Jordan Crawford | jordan@example.com | BPGTM-2025-A7F3G9 | Podia | #12345 |
| 2025-01-16 | Sarah Smith | sarah@company.com | BPGTM-2025-B2K8F1 | Gumroad | gum_67890 |

**Why track:**
- Identify source of leaks
- Provide support to legitimate customers
- Revoke access if needed
- Legal evidence for violations

### Detecting Leaks

**Set up Google Alerts:**

1. Go to [google.com/alerts](https://google.com/alerts)
2. Create alerts for:
   - `"blueprint-company-research" site:github.com`
   - `"BPGTM-2025-" filetype:md`
   - `"Blueprint GTM Skills" download`
   - Your specific license keys (if leaked, you'll find them)

**Manual Checks (Monthly):**

```bash
# Search GitHub for your skills
# (Requires GitHub token)
curl -H "Authorization: token YOUR_TOKEN" \
  "https://api.github.com/search/code?q=blueprint-company-research+in:file"

# Check common paste sites
# pastebin.com, gist.github.com, etc.
```

**If You Find a Leak:**

1. Check watermark to identify customer
2. Email customer privately (might be unintentional)
3. Request they remove/delete shared copy
4. Revoke platform access if intentional
5. Consider legal action only for commercial piracy
6. Update watermark tracking spreadsheet

---

## Pricing Recommendations

### Individual Skills

- **Company Research:** $97 (foundational skill)
- **Data Research:** $147 (most valuable, data-intensive)
- **Message Generation:** $147 (high ROI, directly revenue-impacting)
- **Explainer Builder:** $97 (nice-to-have, client deliverable)

**Total if bought separately:** $488

### Bundles

**Skills-Only Bundle:** $397 (save $91 = 19% discount)
- All 4 skills
- Installation guide
- Email support
- 12 months of updates

**Course + Skills (Recommended):** $997
- 6-10 hours of video training
- All 4 skills (watermarked)
- Private community access (6-12 months)
- Implementation labs
- Email support
- Lifetime updates

**VIP Done-With-You:** $2,997
- Everything in Course + Skills
- 3x 1-hour implementation calls
- Custom skill for your specific use case
- Priority support (24-hour response)
- Lifetime updates
- Private Slack channel

### Team Pricing

**3-Person Team:**
- Skills Only: $997 ($332/person, save $194)
- Course + Skills: $1,997 ($666/person, save $993)

**5-Person Team:**
- Skills Only: $1,497 ($299/person, save $488)
- Course + Skills: $2,997 ($599/person, save $1,988)

**Unlimited Agency License:**
- Skills Only: $2,997 (unlimited users)
- Course + Skills: $4,997 (unlimited users)

### Payment Plans (Podia Only)

**Course + Skills:**
- Full price: $997
- 3 payments: $349/month ($1,047 total)
- 6 payments: $179/month ($1,074 total)

**Psychology:** Payment plans increase conversion by 30-40% but add administrative overhead.

---

## Legal Protection

### License Terms Template

See `LICENSE_TERMS.md` (created separately) for full template.

**Key sections:**
1. Grant of License (what they CAN do)
2. Restrictions (what they CANNOT do)
3. Updates and Support
4. Termination conditions
5. Warranty disclaimer
6. Limitation of liability

### Displaying License Terms

**On Sales Page:**
- Link to full terms: "By purchasing, you agree to our [License Terms]"
- Quick summary in FAQ section

**In Product:**
- Include `LICENSE.md` in every ZIP
- Reference in README
- Watermark in every skill file

**At Checkout:**
- Checkbox: "I agree to the License Terms"
- Required before payment

### Enforcement Strategy

**Casual Sharing (Friend/Colleague):**
- Email customer privately
- Assume good intent
- Explain license terms
- Offer team license discount
- Request removal

**Serial Piracy (Public Sharing):**
- DMCA takedown notice (GitHub, paste sites)
- Cease and desist letter
- Revoke all access
- No refund
- Legal action if commercial use

**Commercial Piracy (Reselling):**
- Immediate legal action
- Trademark infringement claim
- Copyright violation
- Seek damages
- Public statement to deter others

### DMCA Takedown (GitHub)

If skills appear on public GitHub repo:

1. Go to [github.com/contact/dmca](https://github.com/contact/dmca)
2. Submit takedown notice:
   - Your contact info
   - Infringing repository URL
   - Proof of copyright (your original repo, purchase records)
   - Statement: "I have a good faith belief..."
   - Signature (electronic OK)
3. GitHub removes within 24-48 hours

---

## Handling Piracy

### Realistic Expectations

**You will face piracy.** Even with best protection:
- 30-40% of purchasers share with 1-2 people
- 5-10% become serial pirates
- Popular products end up on torrent sites

**Accept this reality and optimize accordingly.**

### Response Tiers

#### Tier 1: Ignore (80% of cases)

**When:** Customer shared with 1-2 colleagues/friends

**Why ignore:**
- Cost of enforcement > value of lost sale
- May be unintentional
- Might convert to legitimate customer later
- Could generate word-of-mouth marketing

**Track but don't act.**

#### Tier 2: Friendly Outreach (15% of cases)

**When:** Multiple copies traced to same watermark

**Response template:**
```
Subject: Blueprint GTM Skills - License Question

Hi [Customer Name],

I noticed your license key appearing in multiple locations and wanted
to reach out.

Your license (BPGTM-2025-XXXXX) is for personal use only. If you're
working with a team, I'd love to offer you our team pricing:

- 3-person team: $997 (just $332/person)
- 5-person team: $1,497 ($299/person)

This includes the same great support and updates, properly licensed
for everyone.

Would that work for your needs?

Best,
[Your Name]

P.S. If this was unintentional, no worries! Just wanted to check in.
```

**Goal:** Convert to legitimate team license, not punish.

#### Tier 3: Enforcement (5% of cases)

**When:**
- Public sharing (GitHub, forums, torrent sites)
- Commercial reselling
- Refusing to comply after outreach

**Actions:**
1. DMCA takedown (if on platform like GitHub)
2. Revoke platform access
3. Cease and desist letter (if high-value)
4. Public statement (if egregious)
5. Legal action (only if commercial or high-profile)

### Preventing Piracy Through Value

**Better than enforcement: Make legitimate purchase more attractive**

1. **Ongoing Updates**
   - Pirates get stale versions
   - Legitimate buyers get new skills, improvements
   - "One-time purchase, lifetime updates" creates retention

2. **Community Access**
   - Private Slack/Discord for buyers only
   - Office hours, Q&A sessions
   - Peer support and networking
   - Can't be pirated

3. **Implementation Support**
   - Email support for legitimate buyers
   - Troubleshooting help
   - Custom skill requests (high-tier)
   - Pirates get no support

4. **Professional Reputation**
   - B2B consultants value legitimate licenses
   - Using pirated tools damages credibility
   - Risk not worth $400 savings

5. **Upsell Opportunities**
   - Done-with-you implementation
   - Custom skill development
   - Agency partnerships
   - Ongoing consulting retainers

**Example:** Customer pays $997 for course. Over 12 months:
- Gets 3 new skills (value: $300)
- Attends 6 office hours (value: $600)
- Receives 10+ hours of support (value: $1,000)
- Joins mastermind community (priceless)
- **Total value delivered: $2,900+**

Pirates get: Initial 4 skills. No updates, no support, no community.

**Legitimate buyers get 3x the value.** That's how you win.

---

## Next Steps

### Week 1: Choose Platform & Set Up

**Decision Matrix:**

| Factor | Podia | Gumroad | GitHub + Stripe |
|--------|-------|---------|-----------------|
| Setup Time | 2-4 hours | 30 min | 4-8 hours |
| Monthly Cost | $89 | $0 | $0 |
| Transaction Fee | 0% | 9% | 2.9% |
| Protection Level | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Best For | Courses | Quick sales | Developers |

**Recommendation:** Start with Podia if creating course, Gumroad if skills-only.

### Week 2: Create Content

**If Podia (Course):**
- Record 4-6 hours of video lessons
- Create slide decks
- Write implementation exercises
- Test everything

**If Gumroad (Skills Only):**
- Write compelling product descriptions
- Create cover images (Canva)
- Set up automated emails
- Prepare watermarking workflow

### Week 3: Test & Refine

1. Test purchase flow yourself
2. Have friend make test purchase
3. Verify watermarking works correctly
4. Check download links
5. Test installation process
6. Review all email sequences

### Week 4: Launch

**Soft Launch:**
- Email your list (if you have one)
- Post in relevant communities
- Offer early-bird discount ($697 instead of $997)
- Limit to first 20 customers
- Gather testimonials

**Public Launch (Week 6):**
- Full price ($997)
- Share testimonials from early customers
- Create case studies
- Run webinar or workshop
- Paid ads (if budget allows)

---

## Support & Questions

If you have questions about distribution strategy, reach out to:
- **Email:** [your-email]
- **Website:** [your-website]

**Remember:** The goal isn't to prevent all piracy (impossible), but to maximize legitimate revenue while providing exceptional value to paying customers.

Focus on delighting your buyers, and piracy becomes a minor inconvenience rather than a major problem.

---

*Last updated: 2025-01-07*
