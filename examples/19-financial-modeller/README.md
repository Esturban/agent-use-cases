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

## What you'll see

```
============================================================
Business: SaaS startup
============================================================
Viability: VIABLE -- Net income turns positive in year 2; free cash flow positive from year 1.

Year    Revenue        EBITDA    Net Income           FCF
------------------------------------------------------
Y1     $1,200,000    $100,000      $75,000      $315,000
Y2     $1,740,000    $426,000     $319,500      $535,500
Y3     $2,523,000    $873,400     $655,050      $869,050

============================================================
Business: Manufacturing company
============================================================
Viability: NOT VIABLE -- DSCR of 1.18x is below the 1.25x threshold in years 1–2.
DSCR:      1.18x

Year    Revenue        EBITDA    Net Income           FCF
------------------------------------------------------
Y1     $4,500,000    $820,000     $590,400      $390,400
Y2     $5,040,000  $1,008,400     $726,048      $526,048
Y3     $5,644,800  $1,219,936     $878,754      $678,754
```

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
