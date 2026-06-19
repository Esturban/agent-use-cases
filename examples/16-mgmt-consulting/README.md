# 16 — Management Consulting Cost Optimizer

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/16-mgmt-consulting/mgmt_consulting_workbook.ipynb)

A consultant agent that reads an operational profile, diagnoses inefficiencies, and delivers a prioritized cost optimization report — quick wins first, backed by effort and impact estimates. Built for operations leads, CFOs, or anyone who needs a structured view of where money is being lost.

---

## What it does

You provide a plain-text description of a company's operations — headcount, systems, workflows, known pain points. The agent reads it and returns a full cost optimization report sorted into four quadrants: quick wins, major projects, fill-ins, and thankless tasks. Each recommendation includes a rationale, concrete implementation steps, and an estimated annual saving in local currency. The output is designed to be handed directly to an executive or ops team.

---

## How it works

The agent is forced to classify every recommendation along two axes — effort (low/medium/high) and impact (low/medium/high) — and assign it to exactly one of four quadrants. The schema defines separate lists for each quadrant, so the model cannot hedge by burying a high-value finding in a generic list. The system prompt encodes the quadrant assignment rules explicitly, and every saving estimate must be expressed as a specific currency figure rather than a vague range.

---

## What you'll see

```
=================================================================
COST OPTIMIZATION REPORT | Meridian Logistics Ltd
=================================================================

Meridian Logistics is carrying approximately GBP 1.9m in avoidable
annual costs across seven identified inefficiencies. The highest-ROI
actions are SaaS consolidation and invoice automation, both of which
can be completed within a quarter with minimal capital outlay.

Total addressable saving: GBP 1.87m per annum

QUICK WINS (2):

  [LOW effort / HIGH impact] | Saving: GBP 124k
  SaaS Subscription Consolidation [technology]
  14 overlapping tools with 40% redundancy — consolidating to one tool per
  category recovers over GBP 120k with no headcount change.
  Steps:
    - Audit all active subscriptions and map feature overlap
    - Select single tool per category and negotiate volume pricing
    - Run 60-day parallel before decommissioning legacy tools

  [LOW effort / HIGH impact] | Saving: GBP 18k
  Digitise Print-Based Approval Workflows [process]
  Paper-routed approvals delay cash flow by up to 7 days — switching to
  digital sign-off eliminates postage cost and cuts cycle time to hours.
  Steps:
    - Deploy e-signature and approval workflow within existing SaaS budget
    - Migrate purchase orders, expenses, and supplier approvals in one sprint

MAJOR PROJECTS (2):

  [HIGH effort / HIGH impact] | Saving: GBP 720k
  Automate Invoice Processing [process]
  12 FTE processing invoices at 3-day cycle time vs 4-hour benchmark;
  AP automation eliminates rework and frees staff for higher-value work.
  Steps:
    - Evaluate AP automation vendors (e.g. Basware, Tipalti)
    - Pilot with one regional office before full rollout

THANKLESS TASKS (avoid) (1):

  [HIGH effort / LOW impact] | Saving: GBP 120k
  Replace Legacy ERP Middleware [technology]
  High replacement cost and long delivery timeline relative to saving;
  defer until ERP modernisation is budgeted as a standalone programme.
  Steps:
    - Document current middleware dependencies
    - Re-evaluate when ERP contract renewal is due

PRIORITIZATION: Start with SaaS consolidation — lowest disruption, fastest
payback, and creates budget headroom to fund the invoice automation project.
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/16-mgmt-consulting/main.py
```

---

## Files

```
16-mgmt-consulting/
  src/schema.py      # Recommendation and CostOptimizationReport Pydantic models with quadrant typing
  src/workflow.py    # Consultant system prompt and structured output call
  main.py            # Meridian Logistics sample profile and formatted report printer
  README.md
```
