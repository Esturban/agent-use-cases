# 10-due-diligence

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/10-due-diligence/due_diligence_workbook.ipynb)

A two-stage agent that reads multiple company documents and produces a unified
commercial due diligence risk register -- each risk scored on severity AND likelihood,
every finding sourced back to the document it came from.

## Harness focus

**Multi-document risk extraction + severity x likelihood matrix**

Stage 1 extracts `DocumentFindings` from each document independently.
Stage 2 synthesises all findings into one `DDReport` -- consolidating overlaps,
scoring on two dimensions, and making a clear go/no-go recommendation.

```
[Doc 1] --> extractor --> DocumentFindings
[Doc 2] --> extractor --> DocumentFindings   --> synthesiser --> DDReport
[Doc 3] --> extractor --> DocumentFindings                        |
[Doc N] --> extractor --> DocumentFindings             risk_items (severity x likelihood)
                                                       overall_assessment
                                                       key_conditions
```

**Keys:** `OPENAI_API_KEY`

```bash
python examples/10-due-diligence/main.py
```

## Key concepts

| Concept | Where |
|---------|-------|
| Two-stage pipeline: extract then synthesise | `src/workflow.py` -- `_extract()` + `_synthesise()` |
| Per-document typed extraction | `src/schema.py` -- `DocumentFindings` |
| 2D risk scoring: severity x likelihood | `src/schema.py` -- `RiskItem` |
| Source attribution per risk item | `src/schema.py` -- `RiskItem.source_document` |
| Multi-document sample data | `main.py` -- accounts, contract, bio, regulatory notice |
