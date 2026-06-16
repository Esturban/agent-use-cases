# 8-multi-agent-research

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/8-multi-agent-research/multi_agent_research_workbook.ipynb)

A three-agent pipeline where a supervisor refines a research question, a researcher
sub-agent extracts structured findings, and a writer sub-agent produces an
executive-level brief — each agent doing only what it's best at.

## Harness focus

**Subagent delegation + handoff contracts**

Each handoff is typed:
- Supervisor → Researcher: refined question (plain string)
- Researcher → Writer: `ResearchFindings` (typed Pydantic object)
- Writer → Output: `WrittenBrief` (typed Pydantic object)

The schema at each handoff is the contract that keeps agents decoupled. The researcher
doesn't know how the writer will use the findings; the writer doesn't know what the
supervisor asked — each agent receives exactly what it needs.

## Key concepts

| Concept | Where to look |
|---------|--------------|
| Supervisor pattern | `SUPERVISOR_SYSTEM` in `workflow.py` |
| Typed handoff | `ResearchFindings` feeds `writer_input` |
| Single-responsibility agents | Each agent has one system prompt, one schema |
| Chain of typed calls | `run()` — three sequential LLM calls |

## Quickstart

```bash
cd examples/8-multi-agent-research
pip install langchain-openai python-dotenv pydantic
echo "OPENAI_API_KEY=sk-..." > .env
python main.py
```
