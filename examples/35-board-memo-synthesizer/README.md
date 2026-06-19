# 35 — Board Memo Synthesizer

Bull, bear, and risk analyst fan-out producing a one-page board memo with a recommended position.

## What it does

Fans out three specialist analysts in parallel — bull (upside), bear (downside), and risk — each reading the same set of analyst reports from their lens. A synthesis agent then combines all three opinions into a structured board memo with a recommended position (proceed / pause / reject) and a one-sentence verdict.

## Architecture

```
main.py
└── src/workflow.py        # run(topic, reports) → BoardMemo via ThreadPoolExecutor
    ├── src/agents.py      # run_bull / run_bear / run_risk / synthesise
    ├── src/prompts.py     # BULL_SYSTEM, BEAR_SYSTEM, RISK_SYSTEM, SYNTHESIS_SYSTEM
    └── src/schema.py      # AnalystOpinion, BoardMemo Pydantic models
```

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

## Output

```json
{
  "topic": "Proposed acquisition of NovaTech Inc.",
  "bull_case": {"lens": "bull", "key_points": ["45% ARR growth", "122% NRR"], "conclusion": "...", "confidence": "high"},
  "bear_case": {"lens": "bear", "key_points": ["38% customer concentration"], "conclusion": "...", "confidence": "medium"},
  "risk_case": {"lens": "risk", "key_points": ["Regulatory approval 9-12 months"], "conclusion": "...", "confidence": "high"},
  "recommended_position": "pause",
  "executive_summary": "The proposed acquisition presents a compelling growth opportunity...",
  "one_sentence_verdict": "Proceed with caution pending regulatory clarity and key-person retention commitments."
}
```

## Workbook

Open `board_memo_synthesizer_workbook.ipynb` for an interactive walkthrough.
