# 36 — Incident Postmortem Drafter

Two-stage pipeline that parses raw incident logs into a structured timeline, then drafts a complete blameless postmortem document.

## What it does

Takes unstructured incident log text (timestamps, severity markers, free-form notes) and runs it through two sequential LLM calls:

1. **Parser** — extracts a structured `IncidentTimeline` (events, severity, affected services, duration)
2. **Postmortem Drafter** — produces a full `Postmortem` with root cause, contributing factors, action items, detection improvements, and an executive summary

## Architecture

```
main.py
└── src/workflow.py        # run(raw_log) → Postmortem (two sequential LLM calls)
    ├── src/prompts.py     # PARSE_SYSTEM, POSTMORTEM_SYSTEM
    └── src/schema.py      # TimelineEvent, IncidentTimeline, Postmortem Pydantic models
```

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

## Output

```json
{
  "incident_id": "INC-2026-042",
  "title": "Database Connection Pool Exhaustion",
  "timeline": {
    "start_time": "2026-06-18T14:30:00Z",
    "end_time": "2026-06-18T16:15:00Z",
    "duration_minutes": 105,
    "affected_services": ["orders-service", "payments-service"]
  },
  "root_cause": "Batch analytics job deployed without connection pool limits exhausted the shared RDS connection pool.",
  "contributing_factors": ["No connection limit on analytics job", "Missing DB connection pool monitoring"],
  "impact_summary": "...",
  "action_items": ["SRE: add connection_limit to analytics job by 2026-06-25"],
  "detection_improvements": ["Alert when DB pool utilization exceeds 80%"],
  "executive_summary": "..."
}
```

## Workbook

Open `incident_postmortem_drafter_workbook.ipynb` for an interactive walkthrough.
