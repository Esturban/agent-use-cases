# 33 — Churn Signal Router

NPS classifier router that segments survey responses and drafts personalised follow-ups per retention tier.

## What it does

Takes a batch of NPS survey responses (score 0–10 + comment) and routes each one to a segment — `escalate` (at-risk detractors), `retain` (promoters), or `neutral` (passives) — then drafts a personalised follow-up message per segment. Routing uses both the numeric score and the comment sentiment, so a score of 5 with a positive comment can be classified as neutral.

## Architecture

```
main.py
└── src/workflow.py         # run(responses) → ChurnBatch via parallel routing
    ├── src/prompts.py      # ROUTER_SYSTEM prompt constant
    └── src/schema.py       # NpsResponse, RoutedResponse, ChurnBatch Pydantic models
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
  "total": 6,
  "retain_count": 2,
  "neutral_count": 2,
  "escalate_count": 2,
  "responses": [
    {
      "customer_id": "C-001",
      "score": 2,
      "segment": "escalate",
      "follow_up_draft": "Dear valued customer, I'm reaching out personally...",
      "reasoning": "Score of 2 with explicit support frustration indicates strong churn risk."
    }
  ]
}
```

## Workbook

Open `churn_signal_router_workbook.ipynb` for an interactive walkthrough.
