# 47 Expense Audit Agent

Audits employee expense reports against a configurable T&E policy. Policy limits live in a `POLICY` dict in `tools.py` — not hardcoded in any prompt — and the LLM evaluates each expense line against the injected policy context to produce typed `PolicyViolation` objects. Approval routing is fully deterministic.

## Business Problem

Finance teams manually review hundreds of expense reports each month, checking every line against category limits, receipt requirements, and travel-class rules. Errors are common, inconsistent enforcement erodes policy trust, and high-value reports queue for days waiting for a human reviewer. This agent standardises and accelerates that review cycle.

## Harness Focus

**Configurable policy rule engine** — the `POLICY` dict in `tools.py` is the single source of truth for all T&E limits. Changing a limit (e.g. raising NYC meal allowance from \$120 to \$140) requires editing one value in one place. Nothing in `prompts.py` or `workflow.py` needs to change. The workflow injects the applicable limit for each line into the LLM context at runtime.

## How It Works

1. `tools.py` defines `POLICY` and two helper functions: `get_meal_limit(city)` and `get_accommodation_limit(city)`.
2. `workflow.py` builds a per-line context block pairing each `ExpenseLine` with its applicable limits, then invokes `gpt-4.1-nano` with structured output targeting `AuditResult`.
3. The LLM produces `PolicyViolation` objects with rule IDs and severity (`info` / `warn` / `block`).
4. Approval tier routing is deterministic post-LLM: no violations → `auto_approve`; info/warn only → `line_manager`; any block + total \< \$5 000 → `finance_director`; block + total ≥ \$5 000 or missing receipt above threshold → `rejected`.

## File Structure

```
examples/47-expense-audit-agent/
  src/__init__.py
  src/schema.py       # ExpenseLine, PolicyViolation, AuditResult
  src/prompts.py      # AUDITOR_PROMPT SystemMessage
  src/tools.py        # POLICY dict + get_meal_limit / get_accommodation_limit
  src/workflow.py     # run() entrypoint + approval tier logic
  main.py             # 3 sample reports: clean / mixed violations / missing receipts
  demo.py             # Gradio UI via OpenRouter
  expense_audit_workbook.ipynb
```

## Scenarios in main.py

| Report | Employee | Total | Expected Tier |
|---|---|---|---|
| EXP-2025-001 | Alice Chen | \$830 | auto_approve |
| EXP-2025-002 | Bob Kumar | \$4,670 | finance_director |
| EXP-2025-003 | Carol Davis | \$460 | rejected |

## How to Run

```bash
# Install dependencies (from repo root)
pip install -r requirements.txt

# Add your OpenAI key
cp .env.example .env
# edit .env: OPENAI_API_KEY=sk-...

# Run the three sample reports
cd examples/47-expense-audit-agent
python main.py

# Launch the Gradio demo (uses OpenRouter)
python demo.py
```
