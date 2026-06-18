# 22 — AI Project Manager

Feed it project updates — emails, status call notes, Slack threads — and it keeps a structured project state up to date. Each update re-derives the RAG status and rewrites the executive summary.

---

## What it does

You pass in unstructured update text and get back an evolving `ProjectState` that tracks:

- Milestones with on-track / at-risk / delayed / complete status
- Active risks with severity and owner
- Current blockers and who needs to resolve them
- Deliverable ownership (who owns what, by when)
- A green / amber / red overall RAG status with an executive summary

Run three updates in sequence and watch the status move from green to amber as the project hits a vendor delay.

---

## How it works

Two structured LLM calls per update — no agent loop, no tools:

1. **Extract**: parse the raw update into a partial `ProjectState` delta
2. **Merge**: combine the delta with the current state, re-derive the RAG status, and write a fresh executive summary

This keeps the state object as the single source of truth. The LLM never sees raw text twice; it only sees typed state.

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/22-ai-pmo/main.py
```

---

## Files

```
22-ai-pmo/
  src/schema.py      # Milestone, Risk, Blocker, DeliverableOwner, ProjectState, UpdateInput
  src/workflow.py    # extract + merge two-pass update pipeline
  main.py            # 3 sequential updates: kick-off, vendor delay, resolution + slip
  README.md
```
