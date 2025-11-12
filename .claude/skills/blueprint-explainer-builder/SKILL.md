---
name: blueprint-explainer-builder
description: Create mobile-responsive HTML explainer document that teaches Blueprint GTM methodology through company-specific PQS and PVP examples. Shows transformation from generic outreach to data-driven intelligence. Use after completing blueprint-message-generation.
---

# Blueprint GTM Explainer Document Builder

## Purpose

Transform validated PQS/PVP messages into a beautiful, mobile-responsive HTML document that explains the Blueprint GTM methodology through company-specific examples. Shows the "old way" (generic pitches) vs "new way" (data-driven intelligence).

This is Stage 4 (Final Deliverable) of the Blueprint GTM Intelligence System.

## Methodology Reference

This skill implements the Blueprint GTM v1.1.0 methodology. For detailed guidance on:
- PVP vs PQS distinction and message classification
- Quality standards (8.5+ for TRUE PVPs, 7.0-8.4 for Strong PQS)
- Message format requirements and examples

See: `references/methodology.md`

## When to Use This Skill

- After completing `blueprint-message-generation` skill
- User has validated PQS and PVP messages ready
- Need to create final consultant-ready deliverable
- Ready to package the complete analysis into sharable format

## Requirements

**Input Required:**

### Artifact 1: Company Research Output
- Company name and core offering
- ICP profile
- Target persona details

### Artifact 2: Validated Messages
- Top 2-3 PQS messages (8.0+ buyer score)
- Top 2-3 PVP messages (8.0+ buyer score)
- Data sources used for each message
- Why each message won (from critique)

**Dependencies:**
- Must complete all previous skills (company research, data research, message generation)

## Output

Single self-contained HTML file:
- Filename: `blueprint-gtm-playbook-[company-name].html`
- Mobile-responsive (works perfectly on phones, tablets, desktops)
- Inline CSS (no external dependencies)
- Under 2MB file size
- Professional Blueprint brand styling

---

## Workflow

### Phase 1: Extract Content Components

Gather all necessary content from previous stages:

**From Company Research:**
- Company name
- Core offering (what they sell)
- Target ICP industries
- Target persona job title

**From Message Generation:**
- 3 best PQS messages with buyer scores
- 3 best PVP messages with buyer scores
- Data sources used (EPA ECHO, OSHA, etc.)
- Why each message works (from critiques)

**Content You'll Create:**
- "Old Way" example (generic SDR email)
- Jordan's bio section
- Transformation narrative

---

### Phase 2: Create "Old Way" Example

Write a typical bad SDR email that the company's team might send today.

**Bad Email Characteristics:**
- Generic personalization (recent LinkedIn post, company growth, etc.)
- Immediate pivot to product features
- Vague benefit claims (save time, reduce costs)
- Name-drop big customers
- Ask for a meeting

**Template Structure:**

```
Subject: Quick question about [their process area]

Hi [Persona Name],

I noticed [generic observation from LinkedIn/website/news].

I'm reaching out because [Company Name] helps companies like yours [vague benefit claim]. Our [technology type] has helped [big name customers] [achieve generic outcome].

[Insert feature list or ROI claim]

Do you have 15 minutes next week to discuss how we could help [Prospect Company] achieve similar results?

Best,
[SDR Name]
[Company Name]
```

**Example for Compliance Software Company:**

```
Subject: Compliance challenges at [Company]

Hi Sarah,

Congrats on the recent expansion to your Texas facility! I saw the announcement on LinkedIn.

I'm reaching out because MedTrainer helps healthcare organizations like yours streamline compliance training and reduce audit risk. We've helped organizations like Mayo Clinic and Cleveland Clinic achieve 40% reduction in compliance violations.

Our AI-powered platform automates training assignments, tracks completions, and provides real-time reporting dashboards that compliance officers love.

Do you have 15 minutes next Tuesday to discuss how we could help [Company] reduce compliance burden?

Best,
Mike
MedTrainer
```

---

### Phase 3: Build HTML Document

Use the following complete HTML template with Blueprint brand styling:

**CRITICAL REQUIREMENTS:**
- All CSS must be inline (in `<style>` tag)
- No external dependencies
- Mobile-responsive (viewport meta tag, responsive CSS)
- No line breaks within sentences in message examples
- Test all colors against brand palette

**HTML Template:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blueprint GTM Playbook for [COMPANY_NAME]</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --print-blue: #5611A6;
            --dark-print: #280A4A;
            --light-print: #D6B2FF;
            --corn: #FFF277;
            --ice: #F5F8FF;
            --white: #FFFFFF;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.7;
            color: var(--dark-print);
            background: var(--ice);
            font-size: 16px;
        }

        .container {
            max-width: 100%;
            margin: 0 auto;
            padding: 1rem;
        }

        h1 {
            font-size: 2rem;
            font-weight: 700;
            color: var(--dark-print);
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid var(--light-print);
        }

        h2 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--dark-print);
            margin: 2.5rem 0 1rem;
            padding-left: 1rem;
            position: relative;
        }

        h2::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: var(--print-blue);
        }

        h3 {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--dark-print);
            margin-bottom: 0.5rem;
        }

        p {
            font-size: 1rem;
            color: rgba(40, 10, 74, 0.9);
            margin-bottom: 1rem;
            line-height: 1.7;
        }

        .section {
            background: var(--white);
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 8px rgba(86, 17, 166, 0.08);
            margin-bottom: 2rem;
        }

        .highlight-box {
            background: var(--corn);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        }

        .old-way-example {
            background: #FFF8DC;
            border: 2px solid #F0E68C;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }

        .message-example {
            background: var(--ice);
            padding: 1rem;
            border-radius: 0.5rem;
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
            line-height: 1.6;
            white-space: pre-wrap;
            overflow-x: auto;
            margin: 0.5rem 0;
        }

        .play-card {
            background: var(--white);
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(86, 17, 166, 0.08);
            border: 1px solid var(--light-print);
        }

        .play-type {
            display: inline-block;
            background: var(--print-blue);
            color: var(--white);
            padding: 0.25rem 0.75rem;
            border-radius: 2rem;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }

        .play-type.pvp {
            background: var(--dark-print);
        }

        .play-explanation {
            background: var(--ice);
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }

        .data-sources {
            background: var(--corn);
            padding: 0.75rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            font-size: 0.875rem;
        }

        .why-section {
            font-size: 0.875rem;
            color: rgba(40, 10, 74, 0.8);
            margin-bottom: 1rem;
        }

        @media (min-width: 768px) {
            .container {
                max-width: 900px;
                padding: 2rem;
            }

            h1 {
                font-size: 2.5rem;
            }

            h2 {
                font-size: 1.75rem;
            }

            .section, .play-card {
                padding: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">

        <!-- SECTION 1: Title & Jordan's Bio -->
        <div class="section">
            <h1>Blueprint GTM Playbook for [COMPANY_NAME]</h1>

            <h2>Who the Hell is Jordan Crawford?</h2>

            <p>Founder of Blueprint GTM. Built a business by scraping 25M+ job posts to find company pain points. Believes the Predictable Revenue model is dead. Thinks mounting an AI SDR on outdated methodology is like putting a legless robot on a horse—no one gets anywhere, and it still shits along the way.</p>

            <p>The core philosophy is simple: The message isn't the problem. The LIST is the message. When you know exactly who to target and why they need you right now, the message writes itself.</p>
        </div>

        <!-- SECTION 2: The Old Way -->
        <div class="section">
            <h2>The Old Way (What Everyone Does)</h2>

            <p>Let's be brutally honest about what your GTM team is doing right now. They're buying lists from ZoomInfo, adding some "personalization" like mentioning a LinkedIn post, then blasting generic messages about features. Here's what it actually looks like:</p>

            <div class="old-way-example">
                <p><strong>The Typical [COMPANY_NAME] SDR Email:</strong></p>
                <div class="message-example">[INSERT BAD EMAIL FROM PHASE 2]</div>
            </div>

            <p><strong>Why this fails:</strong> The prospect is an expert. They've seen this template 1,000 times. There's zero indication you actually understand their specific situation. It's interruption disguised as personalization. Delete.</p>
        </div>

        <!-- SECTION 3: The New Way -->
        <div class="section">
            <h2>The New Way: Intelligence-Driven GTM</h2>

            <p>Blueprint GTM flips the entire approach. Instead of interrupting prospects with pitches, you deliver insights so valuable they'd pay consulting fees to receive them. You become the person who helps them see around corners, not another vendor in their inbox.</p>

            <p>This requires two fundamental shifts:</p>

            <div class="highlight-box">
                <h3>1. Hard Data Over Soft Signals</h3>
                <p><strong>Stop:</strong> "I see you're hiring compliance people" (job postings - everyone sees this)</p>
                <p><strong>Start:</strong> "Your facility at 1234 Industrial Pkwy received EPA violation #2024-XYZ on March 15th" (government database with record number)</p>
            </div>

            <div class="highlight-box">
                <h3>2. Mirror Situations, Don't Pitch Solutions</h3>
                <p><strong>PQS (Pain-Qualified Segment):</strong> Reflect their exact situation with such specificity they think "how did you know?" Use government data with dates, record numbers, facility addresses.</p>
                <p><strong>PVP (Permissionless Value Proposition):</strong> Deliver immediate value they can use today - analysis already done, deadlines already pulled, patterns already identified - whether they buy or not.</p>
            </div>
        </div>

        <!-- SECTION 4: PQS Examples -->
        <div class="section">
            <h2>[COMPANY_NAME] PQS Plays: Mirroring Exact Situations</h2>

            <p>These messages demonstrate such precise understanding of the prospect's current situation that they feel genuinely seen. Every claim traces to a specific government database with verifiable record numbers.</p>

            <!-- PQS Play Card 1 -->
            <div class="play-card">
                <span class="play-type">PQS</span>
                <h3>Play 1: [DESCRIPTIVE TITLE]</h3>

                <div class="play-explanation">
                    <p><strong>What's the play?</strong> [Explain the targeting strategy and specific pain point this addresses]</p>
                </div>

                <div class="why-section">
                    <p><strong>Why this works:</strong> [Explain why this specific data creates urgency. Connect to business impact - fines, shutdowns, repeat inspections, etc.]</p>
                </div>

                <div class="data-sources">
                    <strong>Data source:</strong> [Specific government database name with what it tracks]
                </div>

                <p><strong>The message:</strong></p>
                <div class="message-example">[INSERT ACTUAL PQS MESSAGE - NO LINE BREAKS WITHIN SENTENCES]</div>
            </div>

            <!-- PQS Play Card 2 -->
            <div class="play-card">
                <span class="play-type">PQS</span>
                <h3>Play 2: [DESCRIPTIVE TITLE]</h3>

                [SAME STRUCTURE AS ABOVE]
            </div>

            <!-- PQS Play Card 3 -->
            <div class="play-card">
                <span class="play-type">PQS</span>
                <h3>Play 3: [DESCRIPTIVE TITLE]</h3>

                [SAME STRUCTURE AS ABOVE]
            </div>
        </div>

        <!-- SECTION 5: PVP Examples -->
        <div class="section">
            <h2>[COMPANY_NAME] PVP Plays: Delivering Immediate Value</h2>

            <p>These messages provide actionable intelligence before asking for anything. The prospect can use this value today whether they respond or not. That's the power of permissionless value.</p>

            <!-- PVP Play Card 1 -->
            <div class="play-card">
                <span class="play-type pvp">PVP</span>
                <h3>Play 1: [VALUE-FOCUSED TITLE]</h3>

                <div class="play-explanation">
                    <p><strong>What's the play?</strong> [Explain what specific value/intelligence you're delivering upfront]</p>
                </div>

                <div class="why-section">
                    <p><strong>Why this works:</strong> [Explain why this intelligence is valuable to them right now. What would it cost to generate this themselves? What risk does it help them avoid?]</p>
                </div>

                <div class="data-sources">
                    <strong>Data source:</strong> [Specific government database(s) used to generate this intelligence]
                </div>

                <p><strong>The message:</strong></p>
                <div class="message-example">[INSERT ACTUAL PVP MESSAGE - NO LINE BREAKS WITHIN SENTENCES]</div>
            </div>

            <!-- PVP Play Card 2 -->
            <div class="play-card">
                <span class="play-type pvp">PVP</span>
                <h3>Play 2: [VALUE-FOCUSED TITLE]</h3>

                [SAME STRUCTURE AS ABOVE]
            </div>

            <!-- PVP Play Card 3 -->
            <div class="play-card">
                <span class="play-type pvp">PVP</span>
                <h3>Play 3: [VALUE-FOCUSED TITLE]</h3>

                [SAME STRUCTURE AS ABOVE]
            </div>
        </div>

        <!-- SECTION 6: The Transformation -->
        <div class="section">
            <h2>The Transformation</h2>

            <p>Notice the difference? Traditional outreach talks about YOUR product and YOUR benefits. Blueprint GTM talks about THEIR situation and THEIR challenges using verifiable data they can look up themselves.</p>

            <div class="highlight-box">
                <p><strong>The shift is simple but profound:</strong></p>
                <p>Stop sending messages about what you do. Start sending intelligence about what they need to know right now. When you lead with EPA violation #2024-XYZ on March 15th instead of "I see you're hiring," you're not another sales email - you're the person who actually did the research.</p>
            </div>

            <p>This isn't about templates or tactics. It's about building a systematic way to identify prospects experiencing specific, urgent challenges where [COMPANY_NAME]'s solutions provide unique value - and proving you've done the homework with government database record numbers.</p>

            <p>The companies that master this approach don't compete on features. They compete on intelligence.</p>
        </div>

    </div>
</body>
</html>
```

---

### Phase 4: Populate the Template

Fill in all placeholders with actual content:

**Replace These Placeholders:**

1. **[COMPANY_NAME]** - Use actual company name (all instances)
2. **[INSERT BAD EMAIL FROM PHASE 2]** - Use the bad email you created
3. **[DESCRIPTIVE TITLE]** - Create titles for each play (e.g., "Recent EPA Violations + Active Permits")
4. **[Explain the targeting strategy...]** - Explain who gets this message and why
5. **[Explain why this specific data creates urgency...]** - Connect data to business impact
6. **[Specific government database name...]** - Name the actual database (EPA ECHO, OSHA, etc.)
7. **[INSERT ACTUAL PQS MESSAGE]** - Paste the full message text
8. **[INSERT ACTUAL PVP MESSAGE]** - Paste the full message text

**Message Formatting Rules (CRITICAL):**
- Remove all line breaks within sentences
- Let text wrap naturally
- Only use line breaks between paragraphs
- Test on mobile to ensure proper wrapping

**Example - Wrong:**

```
Subject: 3 OSHA violations

Your facility at 1234 Industrial Pkwy received
OSHA citation #987654321 on March 15, 2025
for three serious violations.

Did I get the count right?
```

**Example - Right:**

```
Subject: 3 OSHA violations

Your facility at 1234 Industrial Pkwy received OSHA citation #987654321 on March 15, 2025 for three serious violations (CFR 1910.147, 1910.212, 1910.305). Most facilities don't know second citations within 12 months trigger mandatory willful classification with 10x penalties. Did I get the count right?
```

---

### Phase 5: Quality Assurance

Before finalizing, test the HTML:

**Checklist:**
- [ ] All [PLACEHOLDERS] replaced with actual content
- [ ] Company name correct throughout
- [ ] 3 PQS plays populated
- [ ] 3 PVP plays populated
- [ ] No line breaks within sentences in messages
- [ ] All data sources named (EPA ECHO, OSHA, etc.)
- [ ] "Why this works" explains business impact
- [ ] Old Way email is realistic and bad
- [ ] All CSS is inline (no external files)
- [ ] Viewport meta tag present for mobile
- [ ] File size under 2MB
- [ ] Filename follows format: `blueprint-gtm-playbook-[company-name].html`

**Visual Check:**
- Proper contrast for readability
- Colors match Blueprint brand palette
- Spacing looks clean on mobile and desktop
- No overlapping text
- Cards are properly styled

**Content Check:**
- Jordan's bio section unchanged
- Philosophy explanation clear
- Transformation narrative compelling
- Each play card has all required sections

---

## Complete Output

**Deliverable:**

Single HTML file named: `blueprint-gtm-playbook-[company-name].html`

**Usage:**
- Can be emailed directly
- Can be hosted on web server
- Works offline (all CSS inline)
- Mobile-responsive for on-the-go reading
- Can be printed (clean print styling)

**File Should Include:**
- Jordan's bio and philosophy
- Old Way vs New Way comparison
- 3 PQS play cards with messages
- 3 PVP play cards with messages
- Transformation narrative
- All using Blueprint brand styling

---

## Integration with Other Skills

**This Skill Receives From:**
- `blueprint-company-research`: Company name, ICP, persona
- `blueprint-message-generation`: Validated messages, data sources, buyer scores

**This Skill Completes:** The Blueprint GTM workflow

**Expected Usage Pattern:**
```
User has validated messages from message generation
→ Claude recognizes all artifacts complete
→ Automatically invokes this skill
→ Produces final HTML explainer document
→ User receives sharable deliverable
```

---

## Tips for Consultants

1. **Customize the "Why this works" sections**: Connect data to real business impact (fines, shutdowns, lost licenses)
2. **Use actual database names**: "EPA ECHO" not "environmental database"
3. **Keep messages intact**: Don't edit the validated messages - they scored 8.0+ for a reason
4. **Test on mobile**: This will be read on phones - make sure text wraps properly
5. **Verify no line breaks**: Messages must flow naturally without mid-sentence breaks
6. **Make bad email realistic**: The contrast between old way and new way is the teaching moment

---

## References

- See `references/EXPLAINER_TEMPLATE.md` for full template with detailed comments
- See `references/DESIGN_SYSTEM.md` for Blueprint brand colors and typography guidelines
- See `examples/overjet/explainer.html` for complete real-world example
- See `assets/template.html` for base template file
