# 5 — Support Ticket Router

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/5-support-ticket-router/support_ticket_router_workbook.ipynb)

Customer support teams waste time manually triaging tickets and writing first responses. This example automates both steps — classifying each inbound ticket and drafting a ready-to-send reply — so agents spend their time resolving issues, not routing them.

---

## What it does

A support ticket comes in as a subject, body, and customer name. The agent first classifies the ticket: it assigns a type (billing, technical, account, etc.), an urgency level, and the team responsible. It then drafts a reply tailored to that team's tone — with a subject line, customer-facing body, and an internal note for the agent. If the ticket is sensitive enough to need a human review before sending, the reply is flagged for escalation.

---

## How it works

The agent runs two sequential calls. The first call reads the ticket and produces a structured classification — type, urgency, routing team, confidence score, and a one-sentence reason for the routing decision. The second call selects a team-specific prompt based on that routing result, then drafts the reply. An escalation flag on the draft acts as a checkpoint: tickets that need human review are held before they reach the customer.

---

## What you'll see

```
============================================================
TICKET: Charged twice this month - invoice #4821
FROM:   Sarah Chen
============================================================

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

    Hi Sarah, thank you for reaching out about the duplicate charge
    on invoice #4821. I'm sorry for the frustration — our billing
    team is reviewing this now and will process your refund within
    1-2 business days. You'll receive a confirmation by email.

  [Internal note]: Verify duplicate charge on invoice #4821 before sending.

============================================================
TICKET: Dashboard not loading - production down
FROM:   Marcus Torres
============================================================

[CLASSIFICATION]
  Type:       technical
  Urgency:    critical
  Team:       engineering
  Confidence: 99%
  Reasoning:  502 error blocking an Enterprise customer requires engineering escalation.

[DRAFT REPLY]
  Subject:   Re: Dashboard not loading - production down
  Escalate:  YES
  Body:

    Hi Marcus, we're aware of the issue affecting dashboard access and
    our engineering team is actively investigating the 502 errors.
    We'll provide a status update within 30 minutes.

  [Internal note]: Enterprise account — escalate to on-call engineer immediately.
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/5-support-ticket-router/main.py
```

---

## Files

```
5-support-ticket-router/
  src/schema.py      # TicketClassification and DraftReply Pydantic models
  src/workflow.py    # Two-step classify-then-draft pipeline
  main.py            # Runs three sample tickets and prints results
  README.md
```
