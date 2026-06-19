# Agent Use Cases

Standalone Python examples of AI agents solving real enterprise problems. Each example is self-contained — a typed schema, a workflow, and two or three scenarios you can run immediately or open directly in Colab.

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

Keys needed:
- `OPENAI_API_KEY` — most examples
- `OPENROUTER_API_KEY` — examples 24, 25, 27, 42 (free tier at openrouter.ai)
- `NEWSAPI_KEY` — example 31 (free tier at newsapi.org)

---

## Examples by department

### Finance and M&A

| # | Example | What it solves | Departments | Difficulty | Colab |
|---|---------|---------------|-------------|:----------:|:-----:|
| 3 | [Invoice Extractor](./examples/3-invoice-extractor/README.md) | Pulls vendor, amount, date, and line items from invoice text with validation and retry | Finance, Accounts Payable | Beginner | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/3-invoice-extractor/invoice_extractor_workbook.ipynb) |
| 10 | [Due Diligence](./examples/10-due-diligence/README.md) | Reads multiple company documents and produces a unified risk register with severity and likelihood scores | Finance, M&A, Legal | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/10-due-diligence/due_diligence_workbook.ipynb) |
| 12 | [Board Pack Reviewer](./examples/12-board-pack-reviewer/README.md) | Reads a board pack and surfaces top risks, information gaps, and questions for management | Governance, Finance, Board | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/12-board-pack-reviewer/board_pack_workbook.ipynb) |
| 13 | [M&A Screener](./examples/13-ma-screener/README.md) | Scores acquisition targets across strategic fit, financials, and operations; blocks below threshold | Corporate Finance, M&A | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/13-ma-screener/ma_screener_workbook.ipynb) |
| 17 | [Corporate Finance](./examples/17-corporate-finance/README.md) | Rates a company across five readiness dimensions; any dimension failing blocks the overall verdict | Corporate Finance, CFO | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/17-corporate-finance/corporate_finance_workbook.ipynb) |
| 18 | [Fundraising Agent](./examples/18-fundraising-agent/README.md) | One company brief generates separate investor materials shaped for VC, PE, and family office audiences | Corporate Finance, Investor Relations | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/18-fundraising-agent/fundraising_agent_workbook.ipynb) |
| 19 | [Financial Modeller](./examples/19-financial-modeller/README.md) | LLM extracts assumptions from a business brief; Python runs the 3-year P&L, cash flow, and DSCR | Finance, FP&A | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/19-financial-modeller/financial_modeller_workbook.ipynb) |
| 35 | [Board Memo Synthesizer](./examples/35-board-memo-synthesizer/README.md) | Bull, bear, and risk analysts run in parallel over the same reports then synthesise a board memo | Executive, M&A, Corporate Finance | Advanced | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/35-board-memo-synthesizer/board_memo_synthesizer_workbook.ipynb) |
| 38 | [Deal Room Analyst](./examples/38-deal-room-analyst/README.md) | Full M&A pipeline — contract review → diligence → financial model → board memo; halts and escalates if any stage falls below confidence threshold | Corporate Finance, M&A, Legal | Advanced | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/38-deal-room-analyst/deal_room_analyst_workbook.ipynb) |
| 42 | [Adaptive Investor Outreach](./examples/42-adaptive-investor-outreach/README.md) | 3-year financial model → tailored materials per investor persona; every financial claim cross-validated across 3 models before inclusion | Corporate Finance, Investor Relations | Advanced | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/42-adaptive-investor-outreach/adaptive_investor_outreach_workbook.ipynb) |

### Legal and Compliance

| # | Example | What it solves | Departments | Difficulty | Colab |
|---|---------|---------------|-------------|:----------:|:-----:|
| 7 | [RFP Parser](./examples/7-rfp-parser/README.md) | Extracts requirements, deadlines, and scoring criteria from procurement documents | Procurement, Legal | Beginner | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/7-rfp-parser/rfp_parser_workbook.ipynb) |
| 9 | [Contract Reviewer](./examples/9-contract-reviewer/README.md) | Flags risk clauses by severity; every finding cites the exact clause it came from | Legal, Procurement | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/9-contract-reviewer/contract_reviewer_workbook.ipynb) |
| 15 | [Regulatory Researcher](./examples/15-regulatory-researcher/README.md) | Analyses regulatory documents and returns obligations, deadlines, and penalties with article citations | Compliance, Legal, Risk | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/15-regulatory-researcher/regulatory_researcher_workbook.ipynb) |
| 39 | [Regulatory Change Tracker](./examples/39-regulatory-change-tracker/README.md) | Diffs a new regulatory update against your obligation register; assesses contract exposure per obligation in parallel; writes versioned compliance state | Legal, Compliance, Risk | Advanced | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/39-regulatory-change-tracker/regulatory_change_tracker_workbook.ipynb) |

### Engineering and DevOps

| # | Example | What it solves | Departments | Difficulty | Colab |
|---|---------|---------------|-------------|:----------:|:-----:|
| 25 | [Manual ReAct Loop](./examples/25-openrouter-react-agent/README.md) | Implements the tool-calling loop from scratch in 80 lines — message list, tool dispatch, while loop, no framework | Engineering | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/25-openrouter-react-agent/openrouter_react_agent_workbook.ipynb) |
| 28 | [Dependency Vulnerability Scanner](./examples/28-dependency-vuln-scanner/README.md) | Reads requirements.txt, calls OSV.dev for live CVE data, ranks by severity, writes the upgrade plan | Engineering, DevSecOps | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/28-dependency-vuln-scanner/dependency_vuln_scanner_workbook.ipynb) |
| 36 | [Incident Postmortem Drafter](./examples/36-incident-postmortem-drafter/README.md) | Parses a raw incident log into a timeline then drafts a blameless postmortem with root cause and action items | Engineering, IT Operations, SRE | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/36-incident-postmortem-drafter/incident_postmortem_drafter_workbook.ipynb) |
| 40 | [Self-Healing CI Agent](./examples/40-self-healing-ci-agent/README.md) | Calls `run_tests`, `apply_fix` tools in a real loop; heals the build or writes a structured postmortem after N retries | Engineering, DevOps, SRE | Advanced | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/40-self-healing-ci-agent/self_healing_ci_agent_workbook.ipynb) |

### Sales and Business Development

| # | Example | What it solves | Departments | Difficulty | Colab |
|---|---------|---------------|-------------|:----------:|:-----:|
| 4 | [Lead Qualifier](./examples/4-lead-qualifier/README.md) | Scores inbound leads against ICP criteria; every score cites the criterion it used | Sales, Business Development | Beginner | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/4-lead-qualifier/lead_qualifier_workbook.ipynb) |
| 11 | [Proposal Writer](./examples/11-proposal-writer/README.md) | Breaks down an RFP and fans out to specialist agents drafting each section; assembles a full proposal | Sales, Consulting | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/11-proposal-writer/proposal_writer_workbook.ipynb) |
| 21 | [Client Intel Monitor](./examples/21-client-intel/README.md) | Searches news, filings, and leadership changes then produces a typed brief with recommended account actions | Sales, Account Management | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/21-client-intel/client_intel_workbook.ipynb) |

### Customer Success and Operations

| # | Example | What it solves | Departments | Difficulty | Colab |
|---|---------|---------------|-------------|:----------:|:-----:|
| 5 | [Support Ticket Router](./examples/5-support-ticket-router/README.md) | Classifies support tickets, routes to the right team, and drafts a first response | Customer Service, IT | Beginner | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/5-support-ticket-router/support_ticket_router_workbook.ipynb) |
| 14 | [Executive Assistant](./examples/14-exec-assistant/README.md) | One email or transcript in; draft reply, action items, and follow-up tracker out simultaneously | Operations, Executive Office | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/14-exec-assistant/exec_assistant_workbook.ipynb) |
| 22 | [AI Project Manager](./examples/22-ai-pmo/README.md) | Parses project updates from any format and keeps a typed state object current; re-derives RAG status each time | Operations, PMO | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/22-ai-pmo/ai_pmo_workbook.ipynb) |
| 33 | [Churn Signal Router](./examples/33-churn-signal-router/README.md) | Classifies NPS responses into escalate / retain / neutral segments and drafts a personalised follow-up per customer | Customer Success, Sales | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/33-churn-signal-router/churn_signal_router_workbook.ipynb) |
| 43 | [Customer Lifecycle Orchestrator](./examples/43-customer-lifecycle-orchestrator/README.md) | Stateful account record moves through lead → onboarding → healthy → at-risk → renewal; a different specialist agent runs at each stage | Customer Success, Sales, Operations | Advanced | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/43-customer-lifecycle-orchestrator/customer_lifecycle_orchestrator_workbook.ipynb) |

### HR and People Operations

| # | Example | What it solves | Departments | Difficulty | Colab |
|---|---------|---------------|-------------|:----------:|:-----:|
| 6 | [Resume Screener](./examples/6-resume-screener/README.md) | Scores resumes against a job spec using the same schema across all candidates so results are directly comparable | HR, Talent Acquisition | Beginner | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/6-resume-screener/resume_screener_workbook.ipynb) |
| 32 | [Onboarding Orchestrator](./examples/32-onboarding-orchestrator/README.md) | Fans out IT provisioning, HR documentation, and Facilities setup to three parallel agents; synthesises a Day 1 readiness plan | HR, Operations, IT | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/32-onboarding-orchestrator/onboarding_orchestrator_workbook.ipynb) |

### Marketing and Growth

| # | Example | What it solves | Departments | Difficulty | Colab |
|---|---------|---------------|-------------|:----------:|:-----:|
| 31 | [News Sentiment Monitor](./examples/31-news-sentiment-monitor/README.md) | Fetches live brand headlines, classifies per-article sentiment, and produces a weekly digest with trend direction | Marketing, Communications, Strategy | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/31-news-sentiment-monitor/news_sentiment_monitor_workbook.ipynb) |
| 37 | [Campaign Brief Fan-Out](./examples/37-campaign-brief-fan-out/README.md) | One campaign brief fans out in parallel to email copywriter, social strategist, and blog planner; assembles a typed content pack | Marketing, Content, Growth | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/37-campaign-brief-fan-out/campaign_brief_fan_out_workbook.ipynb) |
| 41 | [Competitor Response Engine](./examples/41-competitor-response-engine/README.md) | Classifies competitor signals by urgency; only generates counter-campaign content when the signal crosses the respond threshold | Marketing, Growth, Strategy | Advanced | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/41-competitor-response-engine/competitor_response_engine_workbook.ipynb) |

### Strategy and Research

| # | Example | What it solves | Departments | Difficulty | Colab |
|---|---------|---------------|-------------|:----------:|:-----:|
| 8 | [Multi-Agent Research](./examples/8-multi-agent-research/README.md) | Supervisor coordinates a researcher and writer with typed handoffs between them | Strategy, Research | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/8-multi-agent-research/multi_agent_research_workbook.ipynb) |
| 16 | [Management Consulting](./examples/16-mgmt-consulting/README.md) | Identifies inefficiencies and places each recommendation on an effort-vs-impact matrix; quick wins first | Operations, Finance, Consulting | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/16-mgmt-consulting/mgmt_consulting_workbook.ipynb) |
| 20 | [Strategy Consultant](./examples/20-strategy-consultant/README.md) | Researches market size, competitors, and regulatory signals then delivers an ENTER / MONITOR / AVOID verdict | Strategy, Corporate Development | Advanced | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/20-strategy-consultant/strategy_consultant_workbook.ipynb) |
| 23 | [Knowledge Management](./examples/23-knowledge-mgmt/README.md) | Finds relevant past work in a document corpus before drafting; output must cite which documents it drew from | Professional Services, Knowledge Management | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/23-knowledge-mgmt/knowledge_mgmt_workbook.ipynb) |

### ESG and Risk

| # | Example | What it solves | Departments | Difficulty | Colab |
|---|---------|---------------|-------------|:----------:|:-----:|
| 29 | [SEC ESG Extractor](./examples/29-sec-esg-extractor/README.md) | Fetches any company's latest 10-K from SEC EDGAR, extracts ESG disclosures, maps to CSRD categories, and scores completeness | ESG, Investor Relations, Legal | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/29-sec-esg-extractor/sec_esg_extractor_workbook.ipynb) |
| 30 | [Supplier Risk Scorer](./examples/30-supplier-risk-scorer/README.md) | Scores a supplier list using live World Bank Governance Indicators; LLM converts scores into risk tiers with mitigation actions | Supply Chain, Procurement, Risk | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/30-supplier-risk-scorer/supplier_risk_scorer_workbook.ipynb) |
| 34 | [Clinical Trial Finder](./examples/34-clinical-trial-finder/README.md) | Queries ClinicalTrials.gov for recruiting trials then filters and ranks results by patient eligibility | Healthcare, Research, Patient Services | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/34-clinical-trial-finder/clinical_trial_finder_workbook.ipynb) |

---

## Foundation examples

Start here if you're building from scratch. These isolate one pattern at a time before the domain examples layer them together.

| # | Example | What it teaches | Difficulty | Colab |
|---|---------|----------------|:----------:|:-----:|
| 1 | [Basic ReAct Agent](./examples/1-basic-react-agent/README.md) | Reason → call tool → observe loop | Beginner | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/1-basic-react-agent/basic_react_agent_workbook.ipynb) |
| 2 | [Email Triage](./examples/2-email-triage/README.md) | Schema-constrained classification — typed result instead of free text | Beginner | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/2-email-triage/email_triage_workbook.ipynb) |
| 24 | [OpenRouter Structured Output](./examples/24-openrouter-structured-output/README.md) | Same schema on any OpenRouter model — swap one string, nothing else changes | Beginner | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/24-openrouter-structured-output/openrouter_structured_output_workbook.ipynb) |
| 26 | [PydanticAI Agent](./examples/26-pydantic-ai-agent/README.md) | Schema-first agent design with PydanticAI — output contract defined before logic | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/26-pydantic-ai-agent/pydantic_ai_agent_workbook.ipynb) |
| 27 | [Multi-Provider Fan-Out](./examples/27-multi-provider-fan-out/README.md) | Same question to GPT-4o-mini, Mistral, and Llama in parallel; typed opinions synthesised into consensus | Intermediate | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/27-multi-provider-fan-out/multi_provider_fan_out_workbook.ipynb) |

---

## Structure

Each example has only the files it actually needs:

```
examples/N-example-name/
  src/schema.py       # Pydantic models — typed contract for the output
  src/prompts.py      # Prompt constants
  src/workflow.py     # run() — orchestration, LLM calls, tool dispatch
  src/tools.py        # Tool functions the LLM calls (only in tool-calling examples)
  src/agents.py       # Named agent configs (only when the example has multiple distinct agents)
  src/providers.py    # Provider routing (only in multi-provider examples)
  main.py             # 2-3 runnable scenarios
  *_workbook.ipynb    # Colab notebook with framework comparisons and exercises
  README.md
```
