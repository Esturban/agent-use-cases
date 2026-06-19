# 8 — Multi-Agent Research Pipeline

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/8-multi-agent-research/multi_agent_research_workbook.ipynb)

Turn any research topic into a polished executive brief — automatically. Useful for analysts, product teams, or anyone who needs to brief stakeholders quickly without spending hours summarizing sources.

---

## What it does

You provide a topic. A supervisor agent sharpens it into a focused research question. A researcher agent then pulls together key facts, emerging trends, and open gaps on that topic. A writer agent takes those findings and produces a structured brief — title, executive summary, key takeaways, and a full body — ready to share with leadership.

---

## How it works

Three agents run in sequence, each with a single responsibility. The supervisor reformulates the raw topic into a precise question. The researcher answers that question by producing typed findings — facts, trends, and gaps — in a fixed format. The writer receives only those findings and produces the final brief, also in a fixed format. Neither the researcher nor the writer needs to know what the other does; the typed outputs at each step act as clean handoff contracts between them.

---

## What you'll see

```
Topic: The impact of AI agents on software development workflows

Running: Supervisor → Researcher → Writer...
------------------------------------------------------------

[SUPERVISOR] Refined question:
  How are autonomous AI agents changing the day-to-day workflows of software engineers, and what productivity and quality tradeoffs are emerging?

[RESEARCHER] Findings on: AI agents in software development

  Key facts (4):
    - 75% of developers surveyed in 2024 reported using AI tools in daily coding tasks (Stack Overflow Developer Survey)
    - AI agents can reduce time-to-PR for routine features by 30–50% in early adopter teams
    - Code review automation is the fastest-growing use case, cited by 61% of engineering leads
    - Hallucination rates in AI-generated code remain a concern, with 1 in 5 suggestions requiring significant correction

  Trends (3):
    - Shift from single-step autocomplete to multi-step agentic coding loops that plan, write, and test
    - Growth of "AI-first" engineering workflows where agents handle boilerplate and humans own architecture
    - Increasing demand for AI literacy as a core engineering competency

  Gaps (2):
    - Long-term effects on developer skill retention and junior engineer career paths are largely unstudied
    - No consensus metric for measuring agent-driven productivity across teams of different sizes

[WRITER] Brief: AI Agents and the Future of Software Engineering Workflows

  Executive Summary:
  AI agents are moving from passive autocomplete tools to active participants in the software development lifecycle, automating code generation, review, and testing. While early adopters report significant speed gains, the field lacks standardized measures of productivity, and questions about skill atrophy and junior developer impact remain open.

  Key Takeaways:
    * AI agents accelerate routine development tasks but require human oversight to catch hallucinations
    * Engineering leaders should define clear boundaries for agent autonomy before widespread adoption
    * Investing in AI literacy now will be a competitive differentiator within 18–24 months

  Further Reading:
    - Human-AI collaboration models in software teams
    - Measuring developer experience and productivity in AI-augmented workflows
    - Ethics and accountability in AI-generated code

--- Full Brief ---

## AI Agents and the Future of Software Engineering Workflows
...
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/8-multi-agent-research/main.py
```

---

## Files

```
8-multi-agent-research/
  src/schema.py      # ResearchFindings and WrittenBrief Pydantic models
  src/workflow.py    # Three-agent chain: supervisor, researcher, writer
  main.py            # Runs the pipeline on a sample topic and prints results
  README.md
```
