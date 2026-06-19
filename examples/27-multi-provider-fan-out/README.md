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

## What you'll see

```
============================================================
Topic: Should a mid-market B2B SaaS company prioritise EMEA expansion or double down on the US market?
============================================================

Models queried (3):

  [openai/gpt-4o-mini] confidence=high
  Recommendation: Double down on the US market first — capture a dominant position before spreading resources thin across unfamiliar regulatory environments.
  Risks: Slower total addressable market growth | Competitor moves into EMEA unchallenged | Over-reliance on a single geography
  Opportunities: Faster sales cycles | Existing customer expansion revenue | Stronger brand recognition to anchor future EMEA entry

  [mistralai/mistral-small] confidence=medium
  Recommendation: A phased EMEA entry targeting the UK and DACH region offers strong upside with manageable complexity if the US base is already profitable.
  Risks: GDPR compliance overhead | Longer enterprise sales cycles in Europe | Currency exposure
  Opportunities: Less saturated competitive landscape | Strong demand for US-built SaaS tools | EU tech investment tailwinds

  [meta-llama/llama-3.1-8b-instruct] confidence=medium
  Recommendation: Prioritise the US until net revenue retention exceeds 110%, then use that cash flow to fund a focused EMEA pilot.
  Risks: Premature international expansion draining runway | Underestimating localisation costs | Talent acquisition challenges in new markets
  Opportunities: Higher average contract values in enterprise EMEA | EU public sector as an underserved segment | Partnership-led go-to-market to reduce entry cost

Points of agreement:
  + US market should be solidified before significant EMEA investment
  + EMEA entry requires dedicated local resources to succeed
  + Phased geographic expansion reduces execution risk

Points of disagreement:
  ! Mistral sees near-term EMEA opportunity; GPT-4o-mini and Llama favour a longer US consolidation phase
  ! Models differ on the revenue threshold that should trigger international expansion

Consolidated recommendation:
  Prioritise the US market until the business has strong unit economics and a repeatable sales motion, then pursue a targeted EMEA pilot starting in English-speaking markets before expanding further.
```

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
