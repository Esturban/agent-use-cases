# 41 — Competitor Response Engine

Closed-loop signal-to-action pipeline: monitors competitor and brand signals, classifies response urgency (ignore/watch/respond), and only when responding generates a counter-campaign brief then fans out to a full content pack.

## What it does

Takes a batch of competitor signals (news articles, social mentions, press releases, product launches, or pricing changes) and runs a gated three-stage pipeline:

1. **Gate agent** — classifies urgency across the entire signal batch:
   - `ignore` — noise with no meaningful competitive impact
   - `watch` — emerging pattern worth monitoring, no action yet
   - `respond` — strong threat or viral moment requiring immediate counter-action

2. **Brief agent** — only on `respond`: writes a `CounterBrief` that frames our brand's response without naming the competitor.

3. **Content fan-out** — only on `respond`: three specialist agents run in parallel via `ThreadPoolExecutor`:
   - Email copywriter → subject, preview, body, CTA
   - Social media strategist → Instagram, LinkedIn, Twitter posts
   - SEO blog planner → title, meta, section outline, word count

If urgency is `ignore` or `watch`, the pipeline exits after classification — no LLM calls are made for brief or content generation.

## Architecture

```
main.py
└── src/workflow.py          # run(batch) → ResponseEngineResult
    ├── _classify()          # Gate agent — SignalClassification
    ├── _build_brief()       # Brief agent — CounterBrief (respond only)
    ├── _write_email()  ─┐
    ├── _write_social() ─┤── ThreadPoolExecutor(max_workers=3) (respond only)
    ├── _write_blog()   ─┘
    ├── src/prompts.py       # CLASSIFY_SYSTEM, BRIEF_SYSTEM, EMAIL/SOCIAL/BLOG_SYSTEM
    └── src/schema.py        # CompetitorSignal, SignalBatch, SignalClassification,
                             # CounterBrief, EmailCopy, SocialPost, BlogOutline,
                             # ContentPack, ResponseEngineResult
```

## Harness focus

Closed-loop signal-to-action with a conditional gate. A monitoring agent surfaces competitor and brand signals; a gate agent classifies response urgency (ignore/watch/respond); only on "respond" does the orchestrator spin up a counter-campaign brief and content fan-out, keeping expensive generation conditional on signal strength.

## Framework

`openai-sdk` — direct OpenAI Python client with structured outputs (`response_format: json_schema`) and `ThreadPoolExecutor` for parallel fan-out.

## Prerequisites

This example builds on patterns from:

- **#21 — client-intel**: structured competitor intelligence extraction
- **#31 — news-sentiment-monitor**: signal ingestion and classification from news feeds
- **#37 — campaign-brief-fan-out**: parallel content generation from a structured brief (the fan-out stage is reused directly here)

## Comparable patterns

| Framework | Equivalent construct |
|-----------|----------------------|
| LangGraph | Conditional edges — `respond` edge activates the brief + fan-out subgraph; `ignore`/`watch` edges route to a terminal node |
| LangChain | Router chains — `LLMRouterChain` selects the response branch based on classification output |
| CrewAI | Conditional crews — a gate crew classifies urgency; a response crew is only instantiated when urgency is `respond` |

## Setup

```bash
pip install openai pydantic python-dotenv
```

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_key
```

## Usage

```bash
python main.py
```

The script runs two scenarios back-to-back:

- **Scenario A** — competitor product launch + viral social signal → `respond` → full content pack
- **Scenario B** — minor competitor blog post → `ignore` → no content generated

## Output

### Scenario A (respond)

```
Brand:   Flowdesk
Urgency: RESPOND
Reason:  NovaCRM's free tier launch directly targets Flowdesk's SMB customer base and
         has gone viral on LinkedIn, creating immediate retention and acquisition risk.

Key Threat:  A well-funded competitor now offers a free tier covering our core features,
             giving prospects a zero-cost alternative and putting existing customers at risk.
Opportunity: This moment lets Flowdesk articulate the depth and quality that free tools
             cannot match, and accelerate trials before NovaCRM captures mindshare.

--- Counter Brief ---
Topic:     Why depth beats free — the case for Flowdesk
Audience:  SMB founders and marketers currently evaluating or reconsidering their email
           and CRM stack
...

--- Email ---
Subject:  Free is a starting point, not a destination
Preview:  Here is what you actually need to grow
CTA Btn:  Start your free trial
...

--- Social Posts ---
[INSTAGRAM]
Your tools should grow with you, not hold you back. ...
  #emailmarketing  #smallbusiness  #marketingautomation

[LINKEDIN]
Free tiers are appealing until you need to scale. ...
  #crm  #marketingstrategy  #smb

[TWITTER]
Free gets you started. The right platform gets you results. ...
  #emailmarketing  #flowdesk

--- Blog Outline ---
Title: Why Your Marketing Platform Choice Matters More Than Price
Meta:  Choosing the right marketing platform goes beyond cost. Learn what SMBs need ...
~1100 words
  1. Introduction: The Free Tool Trap
  2. What "Full-Featured" Actually Means for SMBs
  3. The Hidden Cost of Switching Later
  4. How Depth Drives Revenue at Scale
  5. Conclusion: Start with the Right Foundation
```

### Scenario B (ignore)

```
Brand:   Flowdesk
Urgency: IGNORE
Reason:  SmallReach's cold email blog post targets enterprise sales teams outside our SMB
         segment and has no paid distribution. No competitive impact detected.

[No content generated — urgency below response threshold]
```
