# 16-mgmt-consulting

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/16-mgmt-consulting/mgmt_consulting_workbook.ipynb)

An agent that reads an operational profile, identifies inefficiencies, and places
each recommendation into a 2x2 effort-impact matrix -- producing a prioritized
cost optimization report with quick wins first.

## Harness focus

**Structured diagnosis + 2D effort-impact ranking**

The model is constrained to classify every recommendation by effort (low/medium/high)
and impact (low/medium/high), then map it to one of four quadrants. The schema
enforces this: quick_wins, major_projects, fill_ins, and thankless_tasks are
separate typed lists. The system prompt encodes the exact quadrant assignment rules.

```
Operational profile
        |
        v
 [Management Consultant]
        |
        v
 CostOptimizationReport
   |-- executive_summary
   |-- total_addressable_saving
   |-- quick_wins[]             (low effort, high impact)
   |     |-- Recommendation
   |           |-- title, category
   |           |-- effort, impact, quadrant
   |           |-- estimated_annual_saving
   |           |-- rationale
   |           |-- implementation_steps
   |-- major_projects[]         (high effort, high impact)
   |-- fill_ins[]               (low effort, low impact)
   |-- thankless_tasks[]        (high effort, low impact)
   |-- prioritization_note
```

**Keys:** `OPENAI_API_KEY`

```bash
python examples/16-mgmt-consulting/main.py
```

## Key concepts

| Concept | Where |
|---------|-------|
| 2x2 quadrant logic encoded in system prompt | `src/workflow.py` -- `CONSULTANT_SYSTEM` |
| Quadrant as typed Literal field | `src/schema.py` -- `Recommendation.quadrant` |
| Schema enforces separate list per quadrant | `src/schema.py` -- `CostOptimizationReport` |
| 7-issue Meridian Logistics profile | `main.py` -- varied effort/impact scenarios |
| Saving estimates in GBP per recommendation | `src/schema.py` -- `Recommendation.estimated_annual_saving` |
