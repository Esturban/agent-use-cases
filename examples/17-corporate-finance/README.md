# 17 — Corporate Finance Readiness Advisor

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/17-corporate-finance/corporate_finance_workbook.ipynb)

An agent that tells a company whether it is ready to raise capital — and exactly what to fix first. CFOs, founders, and deal advisors use it before entering a Series B, growth equity round, or IPO process.

---

## What it does

A company brief goes in (financials, governance, legal status, market position, narrative materials). The agent scores the company across five dimensions: governance, financials, market position, legal, and investor narrative. Each dimension gets a score out of 10, a gate verdict (pass, conditional, or fail), a list of specific blockers, and concrete remediation steps. The final output is a prioritised action plan with a realistic time-to-ready estimate.

---

## How it works

The agent evaluates each dimension independently and applies a strict gate rule: a single fail verdict anywhere makes the overall status "not ready," regardless of how strong the other scores are. This prevents a 9/10 financial score from masking an unresolved IP ownership problem. The critical path lists only the actions that actually unblock the deal, ordered by urgency. The time-to-ready estimate reflects the worst-case remediation timeline across all failing or conditional dimensions.

---

## What you'll see

```
=================================================================
READINESS REPORT | Volt Energy Technologies | SERIES_B
=================================================================

Overall status: NOT_READY

Strong revenue growth and NRR signal genuine product-market fit,
but two structural blockers prevent a Series B process from
launching. IP assignment gaps expose the core platform to investor
due diligence failure, and unaudited accounts for FY2023 and
FY2024 will be rejected by institutional investors outright.

DIMENSION SCORECARD:

  [FAIL] LEGAL -- 3/10
  Strengths: No litigation; standard SaaS contracts in place
  Blockers:  IP not assigned from 2 contractors; customer T&Cs last reviewed 2021
  Remediation:
    - Obtain signed IP assignment deeds from both contractors immediately
    - Engage IP counsel to assess contractor work-for-hire risk
    - Refresh customer SaaS agreements with current template

  [FAIL] GOVERNANCE -- 4/10
  Strengths: Experienced CFO appointment; founder-led growth trajectory
  Blockers:  No independent NEDs; no audit committee; no formal board cadence
  Remediation:
    - Appoint one independent NED with Series B experience before raise
    - Establish quarterly board meeting schedule with formal minutes
    - Form audit committee with CFO as chair

  [COND] FINANCIALS -- 7/10
  Strengths: 67% ARR growth; 74% gross margin; 118% NRR; burn controlled
  Blockers:  FY2023 and FY2024 accounts unaudited; 14-month runway is tight

  [PASS] MARKET_POSITION -- 8/10
  Strengths: 118% NRR; <5% churn; clear AI differentiation; GBP 2.8bn TAM

  [COND] NARRATIVE -- 5/10
  Strengths: Strong underlying metrics; clear use-of-proceeds story
  Blockers:  No formal data room; CFO lacks IR experience; CEO not known to institutions

CRITICAL PATH (4 actions):
  1. Execute IP assignment agreements with both contractors
  2. Commission FY2023 and FY2024 audits (allow 10-12 weeks)
  3. Appoint independent NED and formalise board governance
  4. Build investor data room and prepare CFO for LP meetings

Time to ready: 5-7 months

KEY VALUE DRIVERS:
  + 67% ARR growth with strong gross margin signals scalable unit economics
  + 118% NRR confirms enterprise stickiness and expansion revenue
  + AI-driven anomaly detection differentiates from 3 VC-backed incumbents
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/17-corporate-finance/main.py
```

---

## Files

```
17-corporate-finance/
  src/schema.py      # Pydantic models: DimensionAssessment and ReadinessReport
  src/workflow.py    # Calls the model and returns a validated ReadinessReport
  main.py            # Runs Volt Energy Technologies Series B scenario and prints the report
  README.md
```
