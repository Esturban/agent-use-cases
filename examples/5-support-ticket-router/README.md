# 5-support-ticket-router

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/5-support-ticket-router/support_ticket_router_workbook.ipynb)

A two-stage agent that classifies inbound support tickets and drafts a
first-response email — routing each ticket to the right team with an
appropriate tone and escalation flag.

## Harness focus

**Classification → conditional routing → guarded draft reply**

The agent runs two sequential LLM calls:
1. **Classifier** — `with_structured_output(TicketClassification)` assigns type, urgency, and team
2. **Drafter** — selects a team-specific system prompt based on the routing result, then drafts a `DraftReply`

The `escalate` flag acts as a human-in-the-loop gate: tickets flagged for escalation pause the send pipeline until a human reviews the draft.

## Key concepts

| Concept | Where to look |
|---------|--------------|
| Multi-schema pipeline | `workflow.py` — classifier → drafter |
| Conditional system prompts | `DRAFT_PROMPTS` dict keyed by team |
| Escalation gate | `DraftReply.escalate` field |
| Typed routing | `TicketClassification.team` drives drafter selection |

## Quickstart

```bash
cd examples/5-support-ticket-router
pip install langchain-openai python-dotenv pydantic
echo "OPENAI_API_KEY=sk-..." > .env
python main.py
```

## Sample output

```
======================================================
TICKET: Charged twice this month - invoice #4821
FROM:   Sarah Chen
======================================================

[CLASSIFICATION]
  Type:       billing
  Urgency:    high
  Team:       billing
  Confidence: 97%
  Reasoning:  Duplicate charge dispute requires billing team review.

[DRAFT REPLY]
  Subject:   Re: Charged twice this month - invoice #4821
  Escalate:  No
  Body:
    Hi Sarah, thank you for reaching out...

  [Internal note]: Verify duplicate charge on invoice #4821 before sending.
```
