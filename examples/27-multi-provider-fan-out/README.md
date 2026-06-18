# 27 — Multi-Provider Fan-Out

Same question, three models, one answer. It sends your strategic topic to GPT-4o-mini, Mistral, and Llama in parallel through OpenRouter, then synthesises where they agree, where they diverge, and what the consolidated recommendation is.

---

## What it does

You pass in a strategic question and get back:

- One typed opinion from each model (recommendation, risks, opportunities, confidence)
- Points of agreement across models
- Points of disagreement
- A single synthesised recommendation based on the majority view

---

## How it works

`ThreadPoolExecutor` fires all model calls in parallel. Each response is parsed into a `StrategicOpinion` via the OpenAI structured output API — same call signature regardless of model. A final synthesis pass over all opinions produces the `ModelConsensus`.

Swap any model string to try a different provider. The schema and the synthesis step stay identical.

---

## How to run

```bash
# Requires OPENROUTER_API_KEY in .env
python examples/27-multi-provider-fan-out/main.py
```

---

## Files

```
27-multi-provider-fan-out/
  src/schema.py      # StrategicOpinion, ModelConsensus
  src/workflow.py    # ThreadPoolExecutor fan-out + synthesis pass
  main.py            # 2 strategic topics
  README.md
```
