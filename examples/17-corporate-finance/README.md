# 17-corporate-finance

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/17-corporate-finance/corporate_finance_workbook.ipynb)

An agent that assesses a company's readiness for a capital markets transaction
across five dimensions -- governance, financials, market position, legal, and
narrative -- with a go/no-go gate per dimension and a prioritized remediation plan.

## Harness focus

**Multi-dimension readiness scoring with go/no-go gate per dimension**

Each dimension gets a score (0-10) and a gate verdict: pass, conditional, or fail.
The overall_status is determined by strict gate logic: one fail = not_ready; all
conditional (no fail) = ready_with_conditions; all pass = ready. This prevents
a strong financial score from masking a legal blocker.

```
Company brief
      |
      v
[Corporate Finance Advisor]
      |
      v
 ReadinessReport
   |-- transaction_type  (ipo | series_a | series_b | growth_equity | pe_buyout)
   |-- overall_status    (ready | ready_with_conditions | not_ready)
   |-- executive_summary
   |-- dimensions[]
   |     |-- DimensionAssessment
   |           |-- dimension   (governance | financials | market_position | legal | narrative)
   |           |-- score       (0-10)
   |           |-- gate        (pass | conditional | fail)
   |           |-- strengths[]
   |           |-- blockers[]
   |           |-- remediation[]
   |-- critical_path[]
   |-- estimated_time_to_ready
   |-- key_value_drivers[]
```

**Keys:** `OPENAI_API_KEY`

```bash
python examples/17-corporate-finance/main.py
```

## Key concepts

| Concept | Where |
|---------|-------|
| Gate logic (pass/conditional/fail) with strict overall_status rule | `src/workflow.py` -- `ADVISOR_SYSTEM` |
| Gate as typed Literal on DimensionAssessment | `src/schema.py` -- `DimensionAssessment.gate` |
| One fail blocks the whole deal | `src/schema.py` -- `ReadinessReport.overall_status` |
| Five ordered dimensions enforced in system prompt | `src/workflow.py` -- dimension ordering |
| Volt Energy: realistic Series B with 3 blockers | `main.py` -- IP gaps, governance, late accounts |
