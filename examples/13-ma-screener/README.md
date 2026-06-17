# 13-ma-screener

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/13-ma-screener/ma_screener_workbook.ipynb)

An agent that scores acquisition targets against a structured rubric and returns
a ranked shortlist with a full assessment card per candidate -- replacing
spreadsheet-based screening with a typed, auditable output.

## Harness focus

**Multi-criteria financial scoring rubric + grounded shortlist**

The agent applies a three-dimension scoring rubric (strategic fit, financial fit,
operational fit) to each target and assigns a threshold gate per dimension.
Targets that fail any threshold are screened out; the rest are ranked by composite
score. Every score includes evidence-based rationale, making the ranking auditable.

```
Acquirer brief + target list
           |
           v
    [M&A Screener]
           |
           v
    ScreeningResult
      |-- rubric_summary
      |-- shortlist (ranked by overall_score desc)
      |     |-- TargetAssessmentCard
      |           |-- strategic_fit   (DimensionScore: score, rationale, meets_threshold)
      |           |-- financial_fit   (DimensionScore)
      |           |-- operational_fit (DimensionScore)
      |           |-- overall_score   (0-30)
      |           |-- recommendation  (proceed | monitor | pass)
      |           |-- investment_thesis
      |           |-- key_risks
      |           |-- suggested_next_step
      |-- screened_out  (names that failed a threshold)
      |-- recommendation
```

**Keys:** `OPENAI_API_KEY`

```bash
python examples/13-ma-screener/main.py
```

## Key concepts

| Concept | Where |
|---------|-------|
| Nested DimensionScore with threshold gate | `src/schema.py` -- `DimensionScore.meets_threshold` |
| Multi-criteria rubric in system prompt | `src/workflow.py` -- `SCREENER_SYSTEM` |
| Screening out vs shortlisting | `src/schema.py` -- `ScreeningResult.screened_out` |
| Composite score from dimension sum | `src/schema.py` -- `TargetAssessmentCard.overall_score` |
| 5 synthetic targets with varied profiles | `main.py` -- FieldSense, LogiFlow, RetailAI, CloudOps, DataBridge |
