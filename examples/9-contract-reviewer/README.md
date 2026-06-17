# 9-contract-reviewer

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/9-contract-reviewer/contract_reviewer_workbook.ipynb)

An agent that reads a commercial contract and returns a structured legal review --
risk findings (each citing its exact clause), missing protections, and a
prioritised negotiation point list.

## Harness focus

**Legal document critique + citation-grounded risk register**

The key constraint: every `RiskFinding` must include a `clause_reference`.
The system prompt explicitly refuses findings without one. This forces the model
to ground every assertion in the actual document text rather than generating
generic legal boilerplate.

```
contract text (long string)
        |
        v
[REVIEWER]  with_structured_output(ContractReview)
        |
        v
ContractReview
  ├── risk_findings[]      <- each cites a clause number
  ├── missing_protections[]
  └── negotiation_points[] <- must_have / should_have / nice_to_have
```

**Keys:** `OPENAI_API_KEY`

```bash
python examples/9-contract-reviewer/main.py
```

## Key concepts

| Concept | Where |
|---------|-------|
| Citation obligation in system prompt | `src/workflow.py` — `REVIEWER_SYSTEM` |
| Nested schemas with `Literal` severity + priority | `src/schema.py` — `RiskFinding`, `NegotiationPoint` |
| `Optional[str]` for fields that may not be in every contract | `src/schema.py` — `counterparty`, `governing_law` |
| Single-call structured output on long document | `src/workflow.py` — `run()` |
