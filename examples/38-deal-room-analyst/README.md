# 38 — Deal Room Analyst

Confidence-gated M&A pipeline: contract review → due diligence → financial model → board memo. The orchestrator halts and escalates at any stage where confidence falls below threshold rather than proceeding on weak signals.

**Prerequisites:** [9-contract-reviewer](../9-contract-reviewer), [10-due-diligence](../10-due-diligence), [13-ma-screener](../13-ma-screener), [19-financial-modeller](../19-financial-modeller), [35-board-memo-synthesizer](../35-board-memo-synthesizer)

## What it does

Takes a deal package (contract text, diligence documents, financial summary) and runs four sequential specialist stages:

1. **Contract Review** — risk clauses by severity, missing protections, recommended redlines
2. **Due Diligence** — unified risk register covering financial, legal, operational, management, and regulatory areas
3. **Financial Model** — 3-year P&L projection with implied valuation
4. **Board Memo** — go/pause/reject recommendation with conditions, synthesising all three prior stages

Each stage produces a `confidence` score (0.0–1.0). If any stage falls below the threshold (default 0.6), the orchestrator halts, populates an `EscalationFlag`, and returns a partial result — it does not proceed to expensive downstream stages on insufficient data.

## Architecture

```
main.py
└── src/workflow.py        # run(deal) → DealRoomResult, confidence-gated at each stage
    ├── src/prompts.py     # CONTRACT_SYSTEM, DILIGENCE_SYSTEM, FINANCIAL_SYSTEM, BOARD_SYSTEM
    └── src/schema.py      # DealInput, ContractReview, DueDiligenceReport, FinancialModel,
                           # BoardMemo, EscalationFlag, DealRoomResult
```

**Harness focus:** confidence-gated sequential pipeline — each stage writes a numeric confidence score; orchestrator halts and escalates rather than passing weak signals downstream.

**Framework:** openai-sdk (direct `OpenAI` client, `response_format` structured output)

**Comparable patterns:** LangGraph conditional edges, LangChain sequential chains with output parsers, CrewAI task dependencies with guardrails

## Setup

```bash
pip install openai pydantic python-dotenv
```

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_key
```

## Usage

```bash
python main.py
```

## Output (pipeline completes)

```
RECOMMENDATION: PROCEED
Verdict: NovaTech represents a clean acquisition with strong ARR growth and no material risk blockers.
Key Risks:
  • Retention dependency on CTO and VP Sales post-close
Pipeline Confidence: 0.87
```

## Output (pipeline halts)

```
PIPELINE HALTED at stage: due_diligence
Confidence: 0.45 (threshold: 0.60)
Reason: Due diligence confidence 0.45 below threshold 0.60. Document coverage insufficient.
```

## Workbook

Open `deal_room_analyst_workbook.ipynb` for an interactive walkthrough.
