# 7-rfp-parser

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/7-rfp-parser/rfp_parser_workbook.ipynb)

An agent that reads a procurement RFP (Request for Proposals) and extracts
a fully structured `RFPExtraction` object — deadlines, requirements,
scoring criteria, and budget — from dense government document text.

## Harness focus

**Long-context extraction — pull a typed requirement list out of a large document**

The challenge here is not the schema design but the input: real RFPs run 20-100 pages
and bury requirements in dense prose. This example shows that `with_structured_output()`
works just as well on long documents as short ones — the model reads the full text,
finds all requirements, and returns a clean typed structure.

## Key concepts

| Concept | Where to look |
|---------|--------------|
| Nested schemas | `schema.py` — `RFPExtraction` contains `List[Deadline]`, `List[Requirement]`, `List[ScoringCriterion]` |
| Optional fields | `budget_ceiling`, `contract_duration` — null if not stated |
| Extraction instruction | System prompt: "Extract ALL requirements, not just a sample" |
| Mandatory vs preferred | `Requirement.mandatory` bool |

## Quickstart

```bash
cd examples/7-rfp-parser
pip install langchain-openai python-dotenv pydantic
echo "OPENAI_API_KEY=sk-..." > .env
python main.py
```
