# 15-regulatory-researcher

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/15-regulatory-researcher/regulatory_researcher_workbook.ipynb)

An agent that extracts every obligation, deadline, and penalty from a regulatory
document -- with a hard rule that every finding must cite its exact source article
or it is excluded from the output.

## Harness focus

**Citation-grounded extraction -- no finding without a source article**

The system prompt contains a mandatory citation rule: every obligation and penalty
must include the exact article reference (e.g. "Article 32(1)(a)"). If the model
cannot point to a specific article in the provided text, it must omit the finding.
This makes the output auditable and safe to act on in a compliance context.

```
Regulation text (excerpt)
         |
         v
  [Regulatory Researcher]
         |
         v
   ComplianceSummary
     |-- regulation_name
     |-- jurisdiction
     |-- in_force_date
     |-- obligations[]              (each must cite source_article)
     |     |-- source_article       e.g. "Article 4(1)"
     |     |-- obligation
     |     |-- applies_to
     |     |-- is_ongoing
     |     |-- deadline
     |-- key_deadlines[]            (each includes article ref)
     |-- penalties[]                (each must cite source_article)
     |     |-- source_article
     |     |-- trigger
     |     |-- maximum_fine
     |     |-- other_consequences
     |-- high_priority_gaps[]
```

**Keys:** `OPENAI_API_KEY`

```bash
python examples/15-regulatory-researcher/main.py
```

## Key concepts

| Concept | Where |
|---------|-------|
| Mandatory citation rule in system prompt | `src/workflow.py` -- `RESEARCHER_SYSTEM` |
| source_article field on every finding | `src/schema.py` -- `RegulatoryObligation`, `RegulatoryPenalty` |
| Deadline strings include article ref | `src/schema.py` -- `ComplianceSummary.key_deadlines` |
| Fictional DMCR 2024 with 5 articles | `main.py` -- Articles 4, 7, 11, 15, 22, 23 |
| Citation enforcement comparison (with/without) | `regulatory_researcher_workbook.ipynb` -- Part 5 |
