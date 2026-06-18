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

## What you'll see

```
============================================================
After update 1: Kick-off notes (Week 1)
Status: GREEN
Summary: Project is on track. Three milestones are defined with clear owners. No risks or blockers have been identified at this stage.

Milestones (3):
  [on_track] Data Migration -- Q3-2024
  [on_track] UAT Sign-off -- Q4-2024
  [on_track] Go-Live -- Q1-2025

============================================================
After update 2: Weekly status call (Week 4)
Status: AMBER
Summary: The data migration milestone is at risk due to a missing vendor API spec. Procurement must escalate by end of week or the Q3 target will slip.

Milestones (3):
  [at_risk] Data Migration -- Q3-2024
  [on_track] UAT Sign-off -- Q4-2024
  [on_track] Go-Live -- Q1-2025

Blockers (1):
  Vendor API spec not delivered (raised by Sarah Chen, needs Procurement)

Risks (1):
  [HIGH] Q3 data migration target will slip if API spec not received this week (owner: Procurement)

============================================================
After update 3: Escalation email (Week 6)
Status: AMBER
Summary: Blocker resolved after procurement escalation, but data migration has slipped three weeks to early Q4-2024. UAT is pushed to late Q4-2024 and go-live is now at risk. Close monitoring required to protect the Q1-2025 launch.

Milestones (3):
  [delayed] Data Migration -- Q4-2024
  [at_risk] UAT Sign-off -- Q4-2024
  [at_risk] Go-Live -- Q1-2025

Risks (1):
  [MEDIUM] Go-live target at risk if further delays materialise in UAT (owner: James Park)
```

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
