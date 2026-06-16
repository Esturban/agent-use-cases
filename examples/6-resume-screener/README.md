# 6-resume-screener

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/6-resume-screener/resume_screener_workbook.ipynb)

An agent that scores multiple resumes against a job specification and
surfaces the top candidates with structured, comparable reasoning.

## Harness focus

**Scoring rubric + comparable structured output across many inputs**

The same `ResumeScore` schema is applied to every resume, so outputs
are directly comparable — you can sort, filter, and rank candidates
using plain Python without parsing any free text.

## Key concepts

| Concept | Where to look |
|---------|--------------|
| Consistent schema across inputs | `schema.py` — same `ResumeScore` for every resume |
| Rubric embedded in system prompt | `JOB_SPEC` + scoring tiers in `workflow.py` |
| Ranked output | `main.py` — sort by `overall_score` |
| Honest gap reporting | `skills_missing`, `concern` fields |

## Quickstart

```bash
cd examples/6-resume-screener
pip install langchain-openai python-dotenv pydantic
echo "OPENAI_API_KEY=sk-..." > .env
python main.py
```
