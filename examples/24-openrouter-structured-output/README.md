# 24 — OpenRouter Structured Output

**Harness focus:** Provider-agnostic structured output — OpenRouter unified API with the `openai` SDK; swap the model string to change provider, pattern stays identical.

---

## Business problem

Your email triage logic shouldn't be coupled to a single LLM provider. When pricing changes, a model is deprecated, or a new frontier model ships, you should be able to switch with a one-line change — not a refactor.

This example shows how to use OpenRouter as a provider-agnostic gateway: the same `openai` SDK call, the same Pydantic schema, any model string.

---

## What it demonstrates

- `client.beta.chat.completions.parse()` with a Pydantic `response_format` — structured output without LangChain
- OpenRouter as a drop-in replacement for the OpenAI endpoint (`base_url="https://openrouter.ai/api/v1"`)
- Swapping `model="openai/gpt-4o-mini"` → `"anthropic/claude-3-haiku"` → `"mistralai/mistral-7b-instruct"` without touching any other code

---

## Schema

```python
class EmailTriage(BaseModel):
    urgency: Literal["high", "medium", "low"]
    category: Literal["billing", "technical", "general", "spam"]
    summary: str
    recommended_action: str
```

---

## How to run

```bash
# 1. Get a free API key at https://openrouter.ai
# 2. Add to your .env:
#    OPENROUTER_API_KEY=sk-or-...

pip install openai python-dotenv
python examples/24-openrouter-structured-output/main.py
```

To switch providers, change the `model` argument in `main.py` or pass it to `classify()`:

```python
result = classify(email, model="anthropic/claude-3-haiku")
result = classify(email, model="mistralai/mistral-7b-instruct")
```

---

## Key insight

The `openai` SDK's `beta.chat.completions.parse()` accepts any Pydantic model as `response_format`. Combined with OpenRouter's unified endpoint, the structured output pattern is **completely provider-agnostic** — the harness (schema + parse logic) never changes, only the model string does.

Compare with [2-email-triage](../2-email-triage/README.md) which uses LangChain's `with_structured_output()` — same result, different entry point into the pattern.

---

## Files

```
24-openrouter-structured-output/
  src/schema.py      # EmailTriage Pydantic model
  src/workflow.py    # OpenAI client → OpenRouter + parse
  main.py            # 4 diverse email samples
  README.md
```
