# 18 — Fundraising Package Generator

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/18-fundraising-agent/fundraising_agent_workbook.ipynb)

Founders raising capital have to pitch the same company in completely different terms depending on who is sitting across the table. This agent takes a single company brief and produces three investor-ready packages — one for VCs, one for PE firms, and one for family offices — each written in the language and priorities that audience actually responds to.

---

## What it does

You provide a company brief with financials, team, and transaction details. The agent drafts a full fundraising package for each of three investor types: venture capital, private equity, and family office. Each package includes an investor thesis, the metrics that matter to that persona, a tailored narrative angle, specific asks, pre-emptive objection responses, and a recommended document sequence. All three are assembled into one consolidated output alongside universal value propositions that land across all audiences.

---

## How it works

Three separate LLM calls run in sequence, each given the same company brief but a different persona-specific system prompt. The VC call is framed around growth, TAM, and ARR momentum. The PE call emphasises EBITDA potential and exit multiples. The family office call focuses on capital preservation and downside protection. Every call returns the same `FundraisingMaterials` structure, so the content is fully comparable across personas. The three outputs are then assembled into a single `FundraisingPackage` alongside cross-audience value props.

---

## What you'll see

```
=================================================================
FUNDRAISING PACKAGE | Volt Energy Technologies | Series B
=================================================================

UNIVERSAL VALUE PROPS (resonate across all audiences):
  + 74% gross margin signals durable unit economics at scale
  + 118% NRR means the business grows without adding customers
  + Ex-Google DeepMind CTO gives technical credibility in a crowded market
  + Annual churn below 5% across 210 commercial and industrial customers

========================================
FOR: VENTURE CAPITAL
========================================

Thesis: Volt Energy is the infrastructure layer for commercial energy intelligence
in the UK — a category that does not yet have a dominant SaaS winner.

Headline metrics:
  - ARR GBP 8.2m, +67% YoY
  - NRR 118% — compounding revenue without incremental CAC
  - Gross margin 74% — software economics, not services

Narrative angle: The AI-native energy stack before the market consolidates.
Three VC-backed competitors confirm the category; none has broken out.

Key asks:
  - GBP 15m Series B to accelerate EU expansion before the window closes
  - Introductions to EU enterprise channel partners

Objection responses:
  - Customer concentration: top customer is 31% of ARR — mitigation plan available
  - Runway: 14 months reflects intentional growth spend, not distress

Suggested materials (in order):
  - One-page executive summary
  - Pitch deck (growth and market slides first)
  - ARR bridge and cohort retention data

========================================
FOR: PRIVATE EQUITY
========================================

Thesis: A cash-generative SaaS business with 74% gross margin, proven retention,
and a clear path to EBITDA positivity within 18 months of disciplined cost management.

Headline metrics:
  - Gross margin 74% — PE-quality unit economics
  - NRR 118% — recurring revenue base is growing without churn risk
  - 14-month runway — manageable bridge to profitability with capital discipline

Narrative angle: Not a growth-at-all-costs story. This is an efficient SaaS operator
that has built a defensible customer base and can reach EBITDA breakeven with focused capital.

Key asks:
  - GBP 15m with board seat to support CFO on route to profitability
  - Governance input: no independent board members yet — PE adds immediate value

Objection responses:
  - No EBITDA today: management has a clear 18-month model; CFO from Big 4 appointed 8 months ago
  - Customer concentration: contractual visibility into renewal cycle available on request

Suggested materials (in order):
  - Financial model with profitability scenario analysis
  - Customer contract summary and renewal schedule
  - Management team CVs
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/18-fundraising-agent/main.py
```

---

## Files

```
18-fundraising-agent/
  src/schema.py      # FundraisingMaterials and FundraisingPackage Pydantic models
  src/workflow.py    # Three persona-specific LLM calls assembled into one package
  main.py            # Runs the Volt Energy Technologies Series B brief and prints all three personas
  README.md
```
