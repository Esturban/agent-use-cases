# 14-exec-assistant

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/14-exec-assistant/exec_assistant_workbook.ipynb)

An agent that reads an email thread or meeting transcript and produces three
typed outputs simultaneously: a draft reply, a list of action items with owners
and deadlines, and a follow-up tracker -- all in a single structured call.

## Harness focus

**Fan-out output -- one input produces multiple typed schemas simultaneously**

A single LLM call returns one Pydantic model that contains three distinct typed
sub-structures. The model is constrained to populate all three even when the input
is thin -- if there is nothing substantive to reply to, it drafts an acknowledgement.
This pattern replaces three separate prompts with one typed, composable call.

```
Email thread or meeting transcript
              |
              v
    [Executive Assistant]
              |
              v
         ExecOutput
           |-- input_type        (email_thread | meeting_transcript)
           |-- draft_reply       (polished, ready-to-send)
           |-- subject_line      (email inputs only)
           |-- action_items[]
           |     |-- description
           |     |-- owner
           |     |-- due_date
           |     |-- priority    (high | medium | low)
           |-- follow_up_tracker[]
           |     |-- topic
           |     |-- waiting_on
           |     |-- check_in_by
           |     |-- notes
           |-- meeting_summary   (transcript inputs only)
```

**Keys:** `OPENAI_API_KEY`

```bash
python examples/14-exec-assistant/main.py
```

## Key concepts

| Concept | Where |
|---------|-------|
| Fan-out: one model contains three sub-structures | `src/schema.py` -- `ExecOutput` |
| Enforced population ("no empty lists") in system prompt | `src/workflow.py` -- `ASSISTANT_SYSTEM` |
| Input type detection (email vs transcript) | `src/schema.py` -- `ExecOutput.input_type` |
| Priority enum on extracted tasks | `src/schema.py` -- `ActionItem.priority` |
| Synthetic 3-party email thread with SLA dispute | `main.py` -- API integration delay scenario |
