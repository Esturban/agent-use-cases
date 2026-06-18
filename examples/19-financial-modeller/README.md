# 19 — Financial Model Builder

Give it a plain-English business description. It extracts the financial assumptions, then runs Python to build a 3-year P&L, cash flow statement, and viability check — including DSCR if there's debt.

---

## What it does

You paste in a business brief and get back:

- Year-by-year revenue, gross profit, EBITDA, net income, and free cash flow
- Debt service coverage ratio (if the business carries debt)
- A plain VIABLE / NOT VIABLE verdict with the specific reason

---

## How it works

The model reads the brief and extracts typed financial parameters (growth rates, cost ratios, debt service). Python then runs the arithmetic deterministically — no LLM involved in the calculations.

This keeps the numbers accurate. The AI does the reading; Python does the math.

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/19-financial-modeller/main.py
```

---

## Files

```
19-financial-modeller/
  src/schema.py      # FinancialAssumptions, YearlyProjection, FinancialModel
  src/workflow.py    # LLM extraction + Python computation pipeline
  main.py            # 2 business briefs (SaaS startup, manufacturing company)
  README.md
```
