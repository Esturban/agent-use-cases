# 90 · Approval Gate Pattern

A reusable LangGraph harness that pauses execution at a human-review checkpoint before any irreversible action fires.

**Business problem:** "Route to an approval tier" is a label most agent demos put on an output field — nothing actually stops the action from happening. Any agent that posts journal entries, revokes access, or sends customer-facing collections notices needs a real gate: the tool call must be unreachable until a human signs off.

**Harness focus:** interrupt-and-resume human approval gate — the graph has three nodes (`draft_action` → `human_review` → `execute_or_log`). `human_review` calls LangGraph's `interrupt()`, which genuinely halts execution via the checkpointer until a caller resumes with `Command(resume=<ApprovalDecision>)`. A human can approve, edit the payload, or reject — every path is logged, and rejected/edited actions never silently retry. This is the first example in the repo built on LangGraph's actual `StateGraph` + `interrupt`/`Command` primitives rather than a single LCEL chain, and other examples (the Security Operations and Ledger Integrity clusters) depend on this pattern rather than re-deriving it.

**How to run:**
```
cp .env.example .env  # add OPENAI_API_KEY
python examples/90-approval-gate-pattern/main.py
```

**Colab workbook:** `approval_gate_workbook.ipynb`
