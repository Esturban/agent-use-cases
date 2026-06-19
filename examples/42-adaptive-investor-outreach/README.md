# 42 — Adaptive Investor Outreach

Persona-adaptive generation with multi-model claim validation: builds a 3-year financial model, generates tailored fundraising materials per investor persona (VC/PE/family office), then cross-validates every key financial claim across 3 models before finalising.

## Business Problem

Fundraising materials written for a VC land flat with a PE firm and confuse a family office. Each audience has a distinct risk tolerance, return profile, and decision vocabulary. At the same time, financial claims in investor materials are only as credible as the models behind them — and a single model's projections can go unchallenged until a sceptical LP asks a hard question.

This example solves both problems in one pipeline: persona-adaptive writing plus adversarial claim validation before anything goes out the door.

## Architecture

```
CompanyBrief
     |
     v
_build_projection()          [gpt-4o-mini, OpenAI]
     |
     +---> _build_materials(vc)           --|
     +---> _build_materials(pe)           --+--> parallel (ThreadPoolExecutor)
     +---> _build_materials(family_office)--|
     |
     +---> _extract_key_claims()
               |
               +---> _validate_claim(claim_1) -> [gpt-4o-mini | mistral-7b | llama-3.1-8b]
               +---> _validate_claim(claim_2) -> [gpt-4o-mini | mistral-7b | llama-3.1-8b]
               ...   (all claims validated in parallel; each fans out to 3 models)
     |
     v
OutreachPackage
  - projection
  - materials [vc, pe, family_office]
  - validated_claims  (confirmed / disputed / inconclusive per model)
  - flagged_claims    (claims where 2+ models returned 'disputed')
```

**Two layers of parallelism:**

1. Outer fan-out: 3 personas generated concurrently, 5 claims validated concurrently.
2. Inner fan-out: each claim is sent to 3 validation models simultaneously via OpenRouter.

Total parallel LLM calls at peak: 3 (persona) + 5 x 3 (validation) = 18 concurrent requests.

## Patterns Demonstrated

- **Persona-adaptive generation** — same underlying data, three distinct audience framings
- **Financial modelling via structured output** — conservative projection with flagged uncertainty
- **Multi-model fan-out validation** — cross-provider consistency check before claim inclusion
- **Nested parallelism** — outer task-level and inner model-level concurrency via `ThreadPoolExecutor`
- **Flagging dissent** — surface claims where models disagree rather than silently averaging

## Prerequisites

| # | Example | Pattern Introduced |
|---|---------|-------------------|
| 18 | fundraising-agent | Fundraising context and investor targeting |
| 19 | financial-modeller | Conservative projection generation |
| 27 | multi-provider-fan-out | OpenRouter fan-out + multi-model consensus |
| 35 | board-memo-synthesizer | Multi-lens synthesis for a professional audience |

## Framework

- **openai-sdk** (direct) for primary generation (projection + persona materials)
- **openai-sdk** pointed at **OpenRouter** (`https://openrouter.ai/api/v1`) for multi-model validation
- **pydantic** v2 for all structured outputs via `client.beta.chat.completions.parse`
- **concurrent.futures.ThreadPoolExecutor** for nested parallelism

## Comparable Patterns in Other Frameworks

| Framework | Equivalent Pattern |
|-----------|-------------------|
| LangGraph | Multi-agent graph with a financial-model node feeding parallel persona-writer nodes, then parallel validator nodes with a flag-accumulator edge |
| LangChain | `LLMRouterChain` + `LLMCheckerChain` with a custom multi-LLM routing wrapper per claim |
| CrewAI | Multi-crew setup: FinanceAnalyst crew -> PersonaWriter crew (3 agents) -> FactChecker crew (3 agents, one per validation model) |

## Setup

### 1. Environment variables

Create a `.env` file in the repo root (or this directory):

```
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
```

Both keys are required:
- `OPENAI_API_KEY` — primary generation (gpt-4o-mini for projection and persona materials)
- `OPENROUTER_API_KEY` — multi-model claim validation (gpt-4o-mini + mistral-7b + llama-3.1-8b via OpenRouter)

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Packages used: `openai`, `pydantic`, `python-dotenv` (all in the shared `requirements.txt`).

## Usage

```bash
python main.py
```

Runs both scenarios end-to-end, prints a structured summary to stdout, and writes a full JSON package per company:

- `clearpath_ai_outreach.json`
- `ironbridge_dynamics_outreach.json`

### Run a custom scenario

```python
from src.schema import CompanyBrief
from src.workflow import run

brief = CompanyBrief(
    company_name="Acme Corp",
    sector="B2B SaaS",
    stage="series_a",
    arr_usd=3_000_000,
    growth_rate_pct=70.0,
    ebitda_margin_pct=-28.0,
    headcount=35,
    key_differentiator="Best-in-class integrations with 200+ enterprise tools.",
    use_of_funds="Sales team expansion and product R&D.",
)
package = run(brief)
print(package.flagged_claims)
```

## Output

```
======================================================================
OUTREACH PACKAGE: ClearPath AI
======================================================================

[Financial Projection]
  Year 1 ARR   :      $3,400,000
  Year 2 ARR   :      $5,780,000
  Year 3 ARR   :      $9,248,000
  Year 3 EBITDA:        -$462,400
  Implied EV   :     $83,232,000
  Assumptions:
    - Growth decelerates from 80% to ~60% by Year 2 as TAM saturation begins
    - (!) NRR of 128% assumed to hold; any churn increase materially impacts Year 3

[Investor Materials]

  -- VC --
  Pitch angle : ClearPath AI is compounding ARR at 80% YoY with 128% NRR...
  Hook        : You asked for a Series A with genuine product-market fit...

  -- PE --
  Pitch angle : At 14x ARR with a clear path to EBITDA breakeven by Year 2...

  -- FAMILY_OFFICE --
  Pitch angle : ClearPath offers long-duration exposure to the AI support layer...

[Claim Validation]

  [PASS] ARR will reach $3,400,000 by end of Year 1.
  Dissenters: 0 / 3
    openai/gpt-4o-mini                          confirmed       conf=0.88
    mistralai/mistral-7b-instruct               confirmed       conf=0.81
    meta-llama/llama-3.1-8b-instruct            confirmed       conf=0.79

  [FLAG] EBITDA will reach $-462,400 by Year 3.
  Dissenters: 2 / 3
    openai/gpt-4o-mini                          disputed        conf=0.72
    mistralai/mistral-7b-instruct               disputed        conf=0.68
    meta-llama/llama-3.1-8b-instruct            confirmed       conf=0.61

[Flagged Claims -- 2+ models disputed]
  ! EBITDA will reach $-462,400 by Year 3.
```

## Key Files

```
examples/42-adaptive-investor-outreach/
├── main.py                  # Entry point with 2 diverse company scenarios
├── src/
│   ├── schema.py            # Pydantic models (CompanyBrief -> OutreachPackage)
│   ├── prompts.py           # System prompts for projection, materials, validation
│   ├── providers.py         # OpenRouter multi-model validation + VALIDATION_MODELS
│   └── workflow.py          # run() + internal helpers; all parallelism here
└── README.md
```
