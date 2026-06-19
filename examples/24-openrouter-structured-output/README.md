# 24 — OpenRouter Structured Output

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/24-openrouter-structured-output/openrouter_structured_output_workbook.ipynb)

Support teams and operations teams receive hundreds of emails a day. This example shows how to automatically sort each email into a priority level and category, and recommend a concrete next action — so staff only read what needs their attention.

---

## What it does

Each email is passed to a language model, which reads it and returns four structured fields: urgency (high, medium, or low), category (billing, technical, general, or spam), a one-sentence summary, and a recommended action. The result is guaranteed to match those exact fields — no parsing, no post-processing. Four diverse email samples run in sequence and the results print as a formatted table.

---

## How it works

The script sends each raw email body to OpenRouter's API using the standard OpenAI SDK, with a Pydantic model as the expected response shape. OpenRouter accepts any model string — swapping `openai/gpt-4o-mini` for `anthropic/claude-3-haiku` or `mistralai/mistral-7b-instruct` is a one-word change and nothing else in the code changes. The model reads the email and returns urgency, category, summary, and recommended action as typed fields. If the model cannot fit its answer into those fields, the call fails loudly rather than returning something unusable.

---

## What you'll see

```
LABEL                  URGENCY    CATEGORY       SUMMARY
------------------------------------------------------------------------------------------
Overdue invoice        high       billing        Account suspended over unpaid invoice #48
                                                 Action: Escalate to billing team immedia

Feature request        low        general        Customer requests a dark mode option for
                                                 Action: Log as a product feedback item an

Security alert         high       technical      Suspicious login detected from unrecognis
                                                 Action: Notify user to reset password and

Vendor newsletter      low        spam           Vendor sharing Q3 product update and road
                                                 Action: No action needed, archive the ema
```

---

## How to run

```bash
# Requires OPENROUTER_API_KEY in .env
# Get a free key at https://openrouter.ai
python examples/24-openrouter-structured-output/main.py
```

---

## Files

```
24-openrouter-structured-output/
  src/schema.py      # EmailTriage Pydantic model with urgency, category, summary, recommended_action
  src/workflow.py    # OpenAI SDK call to OpenRouter endpoint with Pydantic response parsing
  main.py            # 4 email samples (overdue invoice, feature request, security alert, newsletter)
  README.md
```
