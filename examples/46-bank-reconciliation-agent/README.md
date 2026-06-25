# 46 Bank Reconciliation Agent

## Business Problem

Month-end bank reconciliation is one of the most time-consuming controls in the
finance close cycle. An accountant must compare every line on the bank statement
against the General Ledger cash account, explain all differences, and certify
that the two balances agree after adjustments.

Most differences are routine: timing gaps (a cheque posted in GL but not yet
cleared at the bank) or bank charges with no automatic GL counterpart. These do
not need an LLM — they can be resolved by simple deterministic rules.

The genuinely difficult items are the exceptions: unusual wire transfers,
unrecorded bank charges, possible duplicates, or outright fraud indicators.
These are few in number but high in risk, and they benefit from an LLM review
that can reason about the narrative, the amount, and the surrounding context.

## Harness Focus

**Bounded matching loop — LLM call volume scales with exception count, not total
transaction volume.**

The agent uses a two-pass deterministic pre-matcher before the LLM is ever
invoked:

| Pass | Logic | Result |
|------|-------|--------|
| 1 — exact | Same absolute amount + same date | `match_confidence = exact` |
| 2 — probable | Same absolute amount + date within 2 days | `match_confidence = probable` |

Only items that survive both passes are forwarded to the LLM. In a typical
month-end with 200 bank transactions, the pre-matcher resolves ~95 % of them
deterministically. The LLM sees a small, curated list of genuine exceptions —
usually fewer than 10 items. This keeps token cost proportional to the number
of problems, not the size of the data set.

Framework: raw `openai` SDK — no LangGraph, no LangChain.

## File Structure

```
examples/46-bank-reconciliation-agent/
  src/__init__.py
  src/schema.py           # Pydantic models
  src/prompts.py          # RECON_SYSTEM prompt string
  src/calculator.py       # Deterministic pre-matcher (date_diff_days, find_matches)
  src/workflow.py         # run() — wires calculator + LLM
  main.py                 # Two runnable scenarios
  demo.py                 # Gradio UI via OpenRouter
  bank_recon_workbook.ipynb
```

## How to Run

```bash
# Prerequisites: OPENAI_API_KEY in .env
cd examples/46-bank-reconciliation-agent
python main.py
```

### Gradio demo (OpenRouter)

```bash
# Prerequisites: OPENAI_API_KEY set to an OpenRouter key in .env
python demo.py
```

## Scenarios

| Scenario | Period | Bank Txns | GL Entries | Expected Outcome |
|----------|--------|-----------|------------|-----------------|
| Standard close | June 2025 | 12 | 11 | Reconciled with 1 timing diff + 1 bank charge |
| Suspicious | July 2025 | 8 | 8 | Not reconciled — fraud indicator + duplicate flagged |
