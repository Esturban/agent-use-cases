# 48 AR Collection Agent

## Business Problem

Finance teams managing large receivables portfolios spend significant time deciding
how to chase overdue invoices. The tone of outreach matters: a friendly nudge for a
two-week-old invoice is appropriate, but that same tone on a 95-day debt looks
unprofessional and risks escalating conflict. Manually drafting different letters for
every aging tier is slow and inconsistent.

## Harness Focus

**Aging-bucket state machine + tone-calibrated generation.**

- **Bucket assignment is deterministic.** A `BUCKET_MAPPING` dict maps each aging
  bucket (`current`, `1_30`, `31_60`, `61_90`, `90_plus`) to an escalation tier
  (`no_action`, `friendly_reminder`, `formal_notice`, `final_demand`, `legal_referral`).
  No LLM involvement in the classification decision.

- **Letter persona is LLM-driven via per-tier SystemMessage.** Each of the four
  letter-generating tiers has its own `SystemMessage` in `ESCALATION_PROMPTS`, tuned
  to a distinct tone: warm and courteous for `friendly_reminder`, firm-professional for
  `formal_notice`, serious and legal-warning for `final_demand`, and an internal memo
  format addressed to Legal for `legal_referral`.

- **Priority scoring and credit-hold logic are also deterministic**, computed from
  `days_overdue`, `outstanding_amount`, and exposure-to-credit-limit ratio.

The pattern demonstrates how to layer deterministic business rules (state machine,
scoring, hold logic) with selective LLM invocation (letter drafting only) to keep
outputs auditable and costs predictable.

## File Structure

```
48-ar-collection-agent/
  src/__init__.py       — package init
  src/schema.py         — ARCustomer, CollectionAction, CollectionPlan (Pydantic)
  src/prompts.py        — BUCKET_MAPPING dict + ESCALATION_PROMPTS per tier
  src/workflow.py       — _get_bucket, _priority_score, _credit_hold, run()
  main.py               — 6 sample customers across all aging buckets
  README.md             — this file
  ar_collection_workbook.ipynb — Colab walkthrough
  demo.py               — Gradio demo via OpenRouter
```

## How to Run

```bash
# From repo root
cd examples/48-ar-collection-agent

# Install dependencies (if not already installed at repo level)
pip install langchain-openai python-dotenv pydantic

# Set your OpenAI API key
export OPENAI_API_KEY=sk-...

# Run the collection plan over 6 sample customers
python main.py
```

## Expected Output

The agent will:
1. Classify each customer into an aging bucket (deterministic).
2. Generate a tone-calibrated collection letter or memo (LLM).
3. Compute a priority score and credit-hold recommendation (deterministic).
4. Print a summary table sorted by priority, then display letter previews.

## Aging Bucket → Escalation Tier Mapping

| Days Overdue | Aging Bucket | Escalation Tier    | LLM Letter? |
|:---:|:---:|:---:|:---:|
| 0            | current      | no_action          | No          |
| 1 – 30       | 1_30         | friendly_reminder  | Yes (warm)  |
| 31 – 60      | 31_60        | formal_notice      | Yes (firm)  |
| 61 – 90      | 61_90        | final_demand       | Yes (serious)|
| 91+          | 90_plus      | legal_referral     | Yes (memo)  |
