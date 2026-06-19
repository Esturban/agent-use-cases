# Agent Use Cases

A teaching library of AI agent patterns in Python. 43 examples, each isolating one technique — from basic structured output to multi-stage orchestration pipelines with tool-calling and stateful state machines.

Work through them in order or jump to the concept you need. Each is self-contained: a typed schema, a workflow, and two or three real scenarios you can run immediately.

---

## How to start

```bash
git clone https://github.com/Esturban/agent-use-cases.git
cd agent-use-cases
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your OPENAI_API_KEY
python examples/1-basic-react-agent/main.py
```

Or open any workbook in Colab — no local setup needed.

Keys you'll need:
- `OPENAI_API_KEY` — most examples
- `OPENROUTER_API_KEY` — examples 24, 25, 27, 42 (free tier at openrouter.ai)
- `NEWSAPI_KEY` — example 31 (free tier at newsapi.org)

---

## Curriculum

### 1. Structured output and classification
Get a typed result instead of free text. Score, classify, and route inputs. This is the foundation everything else builds on.

| # | Example | Technique |
|---|---------|-----------|
| 1 | [Basic ReAct Agent](./examples/1-basic-react-agent/README.md) | Reason → call tool → observe loop |
| 2 | [Email Triage](./examples/2-email-triage/README.md) | Schema-constrained classification |
| 3 | [Invoice Extractor](./examples/3-invoice-extractor/README.md) | Structured extraction with retry on validation failure |
| 4 | [Lead Qualifier](./examples/4-lead-qualifier/README.md) | Scoring rubric — every score cites its criterion |
| 5 | [Support Ticket Router](./examples/5-support-ticket-router/README.md) | Classify → route → conditional draft reply |
| 6 | [Resume Screener](./examples/6-resume-screener/README.md) | Comparable scored output across many inputs |

### 2. Extraction from documents
Pull structure from long, dense, or multi-document inputs. Grounded output — every finding cites its source.

| # | Example | Technique |
|---|---------|-----------|
| 7 | [RFP Parser](./examples/7-rfp-parser/README.md) | Long-context extraction from a procurement document |
| 9 | [Contract Reviewer](./examples/9-contract-reviewer/README.md) | Clause-level risk extraction with citation |
| 10 | [Due Diligence](./examples/10-due-diligence/README.md) | Multi-document risk register synthesis |
| 12 | [Board Pack Reviewer](./examples/12-board-pack-reviewer/README.md) | Director briefing from a governance document |
| 15 | [Regulatory Researcher](./examples/15-regulatory-researcher/README.md) | Obligations and deadlines with article citations |
| 23 | [Knowledge Management](./examples/23-knowledge-mgmt/README.md) | Retrieve relevant past work, then cite it in the output |

### 3. Multi-agent coordination
Supervisor/worker patterns. Parallel fan-out. Typed handoffs between agents.

| # | Example | Technique |
|---|---------|-----------|
| 8 | [Multi-Agent Research](./examples/8-multi-agent-research/README.md) | Supervisor → researcher → writer with typed handoffs |
| 11 | [Proposal Writer](./examples/11-proposal-writer/README.md) | Supervisor breaks down RFP; specialists draft sections |
| 14 | [Executive Assistant](./examples/14-exec-assistant/README.md) | Parallel: draft reply + action items + follow-up tracker |
| 32 | [Onboarding Orchestrator](./examples/32-onboarding-orchestrator/README.md) | IT + HR + Facilities fan-out → Day 1 readiness plan |
| 35 | [Board Memo Synthesizer](./examples/35-board-memo-synthesizer/README.md) | Bull + bear + risk analysts in parallel → board memo |
| 37 | [Campaign Brief Fan-Out](./examples/37-campaign-brief-fan-out/README.md) | One brief → email + social + blog in parallel |
| 41 | [Competitor Response Engine](./examples/41-competitor-response-engine/README.md) | Classify urgency gate → conditional content fan-out |

### 4. Tool-calling and real APIs
The LLM calls Python functions and observes results. Real APIs — no mocked data.

| # | Example | Technique |
|---|---------|-----------|
| 25 | [Manual ReAct Loop](./examples/25-openrouter-react-agent/README.md) | Tool-calling loop written from scratch in 80 lines |
| 28 | [Dependency Vulnerability Scanner](./examples/28-dependency-vuln-scanner/README.md) | Calls OSV.dev live; LLM ranks real CVEs |
| 29 | [SEC ESG Extractor](./examples/29-sec-esg-extractor/README.md) | Fetches live 10-K from SEC EDGAR; extracts ESG disclosures |
| 30 | [Supplier Risk Scorer](./examples/30-supplier-risk-scorer/README.md) | Calls World Bank Governance Indicators; LLM scores risk tiers |
| 34 | [Clinical Trial Finder](./examples/34-clinical-trial-finder/README.md) | Queries ClinicalTrials.gov; filters by patient eligibility |
| 36 | [Incident Postmortem Drafter](./examples/36-incident-postmortem-drafter/README.md) | Log parser tool → structured postmortem document |
| 40 | [Self-Healing CI Agent](./examples/40-self-healing-ci-agent/README.md) | Calls `run_tests` + `apply_fix` tools; loops until green or postmortem |

### 5. Stateful orchestration
Typed state objects that accumulate updates. Stage transitions. Confidence gates. Versioned state.

| # | Example | Technique |
|---|---------|-----------|
| 22 | [AI Project Manager](./examples/22-ai-pmo/README.md) | Parse updates → keep typed state current; re-derive RAG status |
| 38 | [Deal Room Analyst](./examples/38-deal-room-analyst/README.md) | Confidence-gated pipeline — halts and escalates on weak signals |
| 39 | [Regulatory Change Tracker](./examples/39-regulatory-change-tracker/README.md) | Diffs update against obligation register; versioned compliance state |
| 43 | [Customer Lifecycle Orchestrator](./examples/43-customer-lifecycle-orchestrator/README.md) | Stage-gated state machine; specialist per lifecycle stage |

### 6. Multi-provider and adaptive generation
OpenRouter fan-out. Cross-model consensus. Persona-targeted output. Provider-agnostic patterns.

| # | Example | Technique |
|---|---------|-----------|
| 24 | [OpenRouter Structured Output](./examples/24-openrouter-structured-output/README.md) | Same schema, any model — swap one string |
| 27 | [Multi-Provider Fan-Out](./examples/27-multi-provider-fan-out/README.md) | Same question → 3 models in parallel → consensus |
| 42 | [Adaptive Investor Outreach](./examples/42-adaptive-investor-outreach/README.md) | Persona-targeted generation + 3-model claim cross-validation |

### Domain examples
Real business workflows that combine techniques from the sections above.

| # | Example | Domain |
|---|---------|--------|
| 13 | [M&A Screener](./examples/13-ma-screener/README.md) | Corporate Finance |
| 16 | [Management Consulting](./examples/16-mgmt-consulting/README.md) | Operations |
| 17 | [Corporate Finance](./examples/17-corporate-finance/README.md) | Finance |
| 18 | [Fundraising Agent](./examples/18-fundraising-agent/README.md) | Investor Relations |
| 19 | [Financial Modeller](./examples/19-financial-modeller/README.md) | Finance / FP&A |
| 20 | [Strategy Consultant](./examples/20-strategy-consultant/README.md) | Strategy |
| 21 | [Client Intel Monitor](./examples/21-client-intel/README.md) | Sales |
| 26 | [PydanticAI Agent](./examples/26-pydantic-ai-agent/README.md) | Engineering |
| 31 | [News Sentiment Monitor](./examples/31-news-sentiment-monitor/README.md) | Marketing |
| 33 | [Churn Signal Router](./examples/33-churn-signal-router/README.md) | Customer Success |
| 40 | [Self-Healing CI Agent](./examples/40-self-healing-ci-agent/README.md) | DevOps / SRE |

---

## Structure

Each example only has the files it actually needs:

```
examples/N-example-name/
  src/schema.py       # Pydantic models — typed contract for what the agent produces
  src/prompts.py      # Prompt constants
  src/workflow.py     # run() — LLM calls, tool dispatch, orchestration logic
  src/tools.py        # Tool functions the LLM calls (only when the example uses tool-calling)
  src/agents.py       # Named agent configs (only when the example has multiple distinct agents)
  src/providers.py    # Provider routing (only when the example uses multiple LLM providers)
  main.py             # 2-3 runnable scenarios
  *_workbook.ipynb    # Colab notebook with framework comparisons and exercises
  README.md
```

---

## Full example list

See [CATALOG.md](./CATALOG.md) for all 43 examples with difficulty ratings, department index, and technique tags.
