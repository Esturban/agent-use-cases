# 14 — Executive Assistant

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/14-exec-assistant/exec_assistant_workbook.ipynb)

Turns a messy email thread or meeting transcript into a ready-to-send reply, a prioritised task list, and a follow-up tracker — all in one pass. Built for chiefs of staff, EAs, and anyone who manages high-volume correspondence.

---

## What it does

A raw email thread or meeting transcript goes in. The agent reads it, drafts a polished reply, extracts every action item with an owner, deadline, and priority level, and builds a follow-up tracker for anything that needs monitoring but isn't a direct task yet. All three outputs come back together in a single call — no separate prompts, no stitching results together manually.

---

## How it works

The agent is given a system prompt that forbids empty lists — if the input is thin, it drafts an acknowledgement rather than returning nothing. It detects whether the input is an email thread or a meeting transcript and adjusts its output accordingly: email threads get a suggested subject line, transcripts get a brief summary. Each action item is tagged with a priority (high, medium, or low) and an owner where one can be identified. Follow-up entries capture what is being waited on and when to chase if there is no update.

---

## What you'll see

```
=================================================================
EXEC ASSISTANT OUTPUT | Type: email_thread
=================================================================

Subject: RE: API Integration Deadline — Action Plan and Next Steps

DRAFT REPLY:
James and Sarah,

Thank you both for the quick responses. To align on next steps:
James will restart integration work by Wednesday 18 June with a
revised delivery target of 9 July 2025. Legal to confirm SLA
exposure by EOD Tuesday. I'd like us on a call Wednesday to lock
in the Vendor X communication approach.

David

ACTION ITEMS (4):
  1. [HIGH] Legal to advise on SLA exposure and fee rebate risk
     Owner: Legal | Due: Tuesday 17 Jun EOD
  2. [HIGH] Engineering to restart API integration with Vendor X
     Owner: James Reed | Due: Wednesday 18 Jun
  3. [MEDIUM] Schedule alignment call with Vendor X on revised timeline
     Owner: Sarah Connor | Due: Friday 20 Jun
  4. [MEDIUM] CEO update call with James and Sarah
     Owner: David Okafor | Due: Wednesday 18 Jun

FOLLOW-UP TRACKER (2):
  - SLA exposure assessment
    Waiting on: Legal | Check in by: Tuesday 17 Jun
    Notes: 5% monthly rebate per week of delay — quantify total exposure
  - Vendor X revised timeline agreement
    Waiting on: Sarah Connor | Check in by: Friday 20 Jun
    Notes: Agree new date before any formal written notification
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/14-exec-assistant/main.py
```

---

## Files

```
14-exec-assistant/
  src/schema.py      # ExecOutput, ActionItem, and FollowUpEntry Pydantic models
  src/workflow.py    # Builds the prompt and calls the model with structured output
  main.py            # Runs a three-party email thread with an SLA dispute scenario
  README.md
```
