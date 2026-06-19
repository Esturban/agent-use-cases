# Agent Use Cases

43 standalone Python examples of AI agents solving real enterprise problems. Each example is self-contained, runs in under five minutes, and demonstrates one pattern you can take directly into your team's stack.

These are not toy demos. Every example is scoped to a real business function — legal review, financial modelling, CI automation, compliance tracking, customer success — and produces typed, structured output you can wire into an existing workflow.

---

## Quickstart

```bash
git clone https://github.com/Esturban/agent-use-cases.git
cd agent-use-cases
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your OPENAI_API_KEY
python examples/1-basic-react-agent/main.py
```

Or open any workbook directly in Colab — no local setup.

Keys needed:
- `OPENAI_API_KEY` — most examples
- `OPENROUTER_API_KEY` — examples 24, 25, 27, 42 (free tier at openrouter.ai)
- `NEWSAPI_KEY` — example 31 (free tier at newsapi.org)

---

## By department

### Finance and M&A
| # | Example | What it delivers |
|---|---------|-----------------|
| 3 | [Invoice Extractor](./examples/3-invoice-extractor/README.md) | Vendor, amount, date, line items from invoice text — structured and validated |
| 10 | [Due Diligence](./examples/10-due-diligence/README.md) | Unified risk register from multiple company documents |
| 13 | [M&A Screener](./examples/13-ma-screener/README.md) | Acquisition target scoring across strategic fit, financials, and operations |
| 17 | [Corporate Finance](./examples/17-corporate-finance/README.md) | Readiness rating across five dimensions; any dimension failing blocks the verdict |
| 19 | [Financial Modeller](./examples/19-financial-modeller/README.md) | 3-year P&L and cash flow model from a business brief |
| 35 | [Board Memo Synthesizer](./examples/35-board-memo-synthesizer/README.md) | Bull + bear + risk perspectives synthesised into a board memo |
| 38 | [Deal Room Analyst](./examples/38-deal-room-analyst/README.md) | Full M&A pipeline — contract review → diligence → financials → board memo; halts on weak confidence |
| 42 | [Adaptive Investor Outreach](./examples/42-adaptive-investor-outreach/README.md) | 3-year model → tailored materials per investor persona → claims cross-validated across 3 models |

### Legal and Compliance
| # | Example | What it delivers |
|---|---------|-----------------|
| 7 | [RFP Parser](./examples/7-rfp-parser/README.md) | Requirements, deadlines, and scoring criteria from procurement documents |
| 9 | [Contract Reviewer](./examples/9-contract-reviewer/README.md) | Risk clause extraction — every finding cites the clause it came from |
| 15 | [Regulatory Researcher](./examples/15-regulatory-researcher/README.md) | Obligations, deadlines, and penalties with article citations |
| 39 | [Regulatory Change Tracker](./examples/39-regulatory-change-tracker/README.md) | Diffs a new regulatory update against your obligation register; scores contract exposure; writes versioned compliance state |

### Engineering and DevOps
| # | Example | What it delivers |
|---|---------|-----------------|
| 28 | [Dependency Vulnerability Scanner](./examples/28-dependency-vuln-scanner/README.md) | Calls OSV.dev for live CVEs; ranks by severity; writes the upgrade plan |
| 36 | [Incident Postmortem Drafter](./examples/36-incident-postmortem-drafter/README.md) | Parses a raw incident log → structured timeline → blameless postmortem with action items |
| 40 | [Self-Healing CI Agent](./examples/40-self-healing-ci-agent/README.md) | Calls `run_tests`, `apply_fix` tools in a real loop; heals or writes a postmortem after N retries |

### Sales and Business Development
| # | Example | What it delivers |
|---|---------|-----------------|
| 4 | [Lead Qualifier](./examples/4-lead-qualifier/README.md) | ICP scoring — every score cites the criterion it used |
| 18 | [Fundraising Agent](./examples/18-fundraising-agent/README.md) | VC, PE, and family office materials from a single company brief |
| 21 | [Client Intel Monitor](./examples/21-client-intel/README.md) | News, filings, leadership changes → typed account brief with recommended actions |

### Customer Success and Operations
| # | Example | What it delivers |
|---|---------|-----------------|
| 5 | [Support Ticket Router](./examples/5-support-ticket-router/README.md) | Classify → route → draft first response |
| 22 | [AI Project Manager](./examples/22-ai-pmo/README.md) | Parse updates from any format → keep typed project state current; re-derives RAG status |
| 33 | [Churn Signal Router](./examples/33-churn-signal-router/README.md) | NPS → escalate / retain / neutral segments with personalised follow-up drafts |
| 43 | [Customer Lifecycle Orchestrator](./examples/43-customer-lifecycle-orchestrator/README.md) | Stateful account record across lead → onboarding → healthy → at-risk → renewal; specialist agent per stage |

### HR and People Operations
| # | Example | What it delivers |
|---|---------|-----------------|
| 6 | [Resume Screener](./examples/6-resume-screener/README.md) | Score resumes against a job spec — same schema across candidates makes results comparable |
| 32 | [Onboarding Orchestrator](./examples/32-onboarding-orchestrator/README.md) | IT provisioning + HR documentation + Facilities in parallel → Day 1 readiness plan |

### Marketing and Growth
| # | Example | What it delivers |
|---|---------|-----------------|
| 31 | [News Sentiment Monitor](./examples/31-news-sentiment-monitor/README.md) | Live brand headlines → per-article sentiment → weekly digest with trend direction |
| 37 | [Campaign Brief Fan-Out](./examples/37-campaign-brief-fan-out/README.md) | One brief → email copy + social captions + blog outline in parallel |
| 41 | [Competitor Response Engine](./examples/41-competitor-response-engine/README.md) | Classify signal urgency → only generate counter-campaign when it crosses the respond threshold |

### Strategy and Research
| # | Example | What it delivers |
|---|---------|-----------------|
| 8 | [Multi-Agent Research](./examples/8-multi-agent-research/README.md) | Supervisor coordinates researcher + writer with typed handoffs |
| 12 | [Board Pack Reviewer](./examples/12-board-pack-reviewer/README.md) | Director briefing — top risks, information gaps, questions for management |
| 16 | [Management Consulting](./examples/16-mgmt-consulting/README.md) | Inefficiency identification ranked on effort-vs-impact; quick wins first |
| 20 | [Strategy Consultant](./examples/20-strategy-consultant/README.md) | Market size + competitors + regulatory data → ENTER / MONITOR / AVOID verdict |
| 23 | [Knowledge Management](./examples/23-knowledge-mgmt/README.md) | Retrieve relevant past work from a corpus, then cite it in the output |

### ESG and Risk
| # | Example | What it delivers |
|---|---------|-----------------|
| 29 | [SEC ESG Extractor](./examples/29-sec-esg-extractor/README.md) | Fetches live 10-K from SEC EDGAR; extracts ESG disclosures mapped to CSRD categories |
| 30 | [Supplier Risk Scorer](./examples/30-supplier-risk-scorer/README.md) | World Bank Governance Indicators → supplier risk tiers with mitigation actions |
| 34 | [Clinical Trial Finder](./examples/34-clinical-trial-finder/README.md) | Queries ClinicalTrials.gov by patient criteria; ranks matches with eligibility summaries |

---

## Learning path

If you're working through these to learn the patterns, start here and work forward:

| Stage | Examples | What you learn |
|-------|----------|----------------|
| Foundation | 1 → 6 | Structured output, classification, scoring rubrics |
| Extraction | 7, 9, 10, 15, 23 | Long-context extraction; grounded output with citations |
| Coordination | 8, 11, 14, 32, 35, 37 | Multi-agent fan-out; typed handoffs between agents |
| Tool-calling | 25, 28, 29, 30, 34, 36, 40 | LLM calls real functions; observes results; loops |
| Stateful pipelines | 22, 38, 39, 43 | Typed state objects; stage gates; versioned updates |
| Multi-provider | 24, 27, 42 | OpenRouter fan-out; cross-model consensus |

---

## Structure

Each example has only the files it needs:

```
examples/N-example-name/
  src/schema.py       # Pydantic models — typed contract for the output
  src/prompts.py      # Prompt constants
  src/workflow.py     # run() — orchestration, LLM calls, tool dispatch
  src/tools.py        # Tool functions the LLM calls (only when the example uses tool-calling)
  src/agents.py       # Named agent configs (only when multiple distinct agents)
  src/providers.py    # Provider routing (only when multi-provider)
  main.py             # 2-3 runnable scenarios
  *_workbook.ipynb    # Colab notebook with framework comparisons and exercises
  README.md
```

See [CATALOG.md](./CATALOG.md) for all 43 examples with difficulty ratings and technique tags.
