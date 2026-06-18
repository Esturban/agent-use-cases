# 26 — PydanticAI Agent

**Harness focus:** Schema-first agent framework — PydanticAI wraps the model call in a typed `Agent` whose output contract is defined entirely in Pydantic. Contrast with LangChain's chain-first approach.

---

## Business problem

Accounts payable teams receive invoices in dozens of formats. You want structured extraction — same as example 3 — but you want to understand a framework that puts the schema at the centre of the design, not the chain.

---

## What it demonstrates

- `Agent(model, result_type=Invoice)` — the output type drives everything: prompt injection, API call, validation, and retry
- `agent.run_sync(text)` returning `result.data: Invoice` — no `.parse()`, no `.invoke()`, the type is the contract
- Nested Pydantic models (`LineItem` inside `Invoice`) work without extra configuration
- Framework comparison: PydanticAI vs LangChain `with_structured_output()` — same output, different design philosophy

---

## Framework comparison

| Aspect | LangChain (ex. 3) | PydanticAI (ex. 26) |
|--------|-------------------|---------------------|
| Entry point | `llm.with_structured_output(Schema)` → runnable | `Agent(model, result_type=Schema)` → Agent |
| Invocation | `chain.invoke(text)` | `agent.run_sync(text).data` |
| Retry on invalid | Manual with RunnableWithFallbacks | Built-in |
| System prompt | In the chain | In the Agent constructor |

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
pip install pydantic-ai python-dotenv
python examples/26-pydantic-ai-agent/main.py
```

---

## Files

```
26-pydantic-ai-agent/
  src/schema.py      # Invoice + LineItem Pydantic models
  src/workflow.py    # PydanticAI Agent with result_type=Invoice
  main.py            # 2 invoice samples (SaaS + consulting)
  README.md
```
