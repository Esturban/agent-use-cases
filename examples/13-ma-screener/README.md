# 13 — M&A Target Screener

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/13-ma-screener/ma_screener_workbook.ipynb)

Private equity and corporate development teams spend days scoring acquisition candidates in spreadsheets. This agent replaces that with a consistent, auditable shortlist — scored against your own criteria in seconds.

---

## What it does

You provide an acquirer brief (sector focus, revenue range, margin floor, geography) and a list of target companies with their key metrics. The agent scores each target across three dimensions — strategic fit, financial fit, and operational fit — on a 0–10 scale each. Targets that fail any minimum threshold are filtered out; the rest are ranked by composite score with a one-sentence investment thesis, top risks, and a recommended next step per candidate.

---

## How it works

The agent reads the acquirer brief and applies a rubric that scores each target on strategic alignment, financial profile, and integration complexity. Any target that falls below the minimum threshold on any dimension is removed from the shortlist and listed separately as screened out. For targets that clear all thresholds, the agent sums the three dimension scores into a composite out of 30 and ranks them. Every score comes with a rationale tied to the data in the brief, so the ranking can be explained and challenged.

---

## What you'll see

```
=================================================================
M&A SCREENING RESULT | Acquirer: Apex Capital Partners
=================================================================

Rubric: B2B SaaS targets in UK/EU with GBP 10-50m ARR, 15%+ EBITDA margin, and bolt-on integration within 6 months.

Top-line: FieldSense is the standout candidate — strong margins, high NRR, and minimal integration risk. CloudOps Nordic is a solid second. LogiFlow and RetailAI fail financial thresholds; DataBridge is geographically out of scope.

SHORTLIST (2 targets):

  [25/30] FieldSense Ltd (UK)
  Recommendation: PROCEED
  Thesis: Best-in-class unit economics and 120 NRR make FieldSense the highest-conviction bolt-on in the set.
  Scores -- Strategic: 9/10 | Financial: 9/10 | Operational: 7/10
  Key risks: Integration of 45-person team, potential key-man dependency on founding CEO
  Next step: Initiate NDA and request management accounts for FY2023-2024

  [21/30] CloudOps Nordic AB (Sweden)
  Recommendation: PROCEED
  Thesis: Predictable recurring revenue and low churn justify a premium; EU domicile adds some deal complexity.
  Scores -- Strategic: 8/10 | Financial: 7/10 | Operational: 6/10
  Key risks: Cross-border legal structure, FX exposure on SEK revenues
  Next step: Confirm EU entity structure and arrange introductory call with founders

SCREENED OUT: LogiFlow GmbH, RetailAI Ltd, DataBridge Inc
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/13-ma-screener/main.py
```

---

## Files

```
13-ma-screener/
  src/schema.py      # DimensionScore, TargetAssessmentCard, and ScreeningResult Pydantic models
  src/workflow.py    # Scoring rubric prompt and agent invocation returning a ScreeningResult
  main.py            # Five synthetic B2B SaaS targets screened against an Apex Capital brief
  README.md
```
