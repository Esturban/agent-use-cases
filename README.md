# Agent Use Cases

29 working examples of AI agents solving real business problems. Each example is a self-contained Python project you can run in five minutes or open directly in Colab.

Every example follows the same structure: a typed schema defines what the agent produces, a workflow wires the LLM calls together, and a main script runs two or three real-world scenarios so you can see the output immediately.

---

## What you'll learn

Each example isolates one technique. Work through them in order and you'll go from a basic tool-calling loop to multi-model parallel queries with consensus synthesis.

**Covered techniques, from simple to complex:**

- Get a structured, typed result instead of free text
- Make the model cite its evidence — no ungrounded assertions
- Route inputs to different downstream steps based on a classification
- Pull specific data out of long, dense documents
- Give the model tools to call and let it decide when to use them
- Coordinate multiple agents on a single task with typed handoffs
- Keep a stateful object up to date from a stream of unstructured updates
- Retrieve relevant past work before drafting, then cite it in the output
- Send the same prompt to multiple models in parallel and synthesise the results
- Run the same pattern on any provider by swapping one model string

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

Or click any Colab badge in the table below — no local setup needed.

Not sure where to start? See [CATALOG.md](./CATALOG.md) for difficulty ratings, utility notes, and a by-department index.

---

## All Examples

<details open>
<summary>Click to expand</summary>

| # | Example | What it does | Who uses it | Keys | Colab |
|---|---------|--------------|-------------|:----:|:-----:|
| 1 | [Basic ReAct Agent](./examples/1-basic-react-agent/README.md) | Model reasons, calls a tool, observes the result, repeats until done | Engineering, Data Science | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/1-basic-react-agent/basic_react_agent_workbook.ipynb) |
| 2 | [Email Triage](./examples/2-email-triage/README.md) | Classifies inbound emails by urgency and category into a typed result | Operations, IT | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/2-email-triage/email_triage_workbook.ipynb) |
| 3 | [Invoice Extractor](./examples/3-invoice-extractor/README.md) | Pulls vendor, amount, date, and line items from invoice text with validation and retry | Finance, Accounts Payable | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/3-invoice-extractor/invoice_extractor_workbook.ipynb) |
| 4 | [Lead Qualifier](./examples/4-lead-qualifier/README.md) | Scores inbound leads against ICP criteria; every score must cite which criterion it used | Sales, Business Development | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/4-lead-qualifier/lead_qualifier_workbook.ipynb) |
| 5 | [Support Ticket Router](./examples/5-support-ticket-router/README.md) | Classifies support tickets, routes to the right team, and drafts a first response | Customer Service, IT | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/5-support-ticket-router/support_ticket_router_workbook.ipynb) |
| 6 | [Resume Screener](./examples/6-resume-screener/README.md) | Scores resumes against a job spec with the same schema so results are directly comparable | HR, Talent Acquisition | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/6-resume-screener/resume_screener_workbook.ipynb) |
| 7 | [RFP Parser](./examples/7-rfp-parser/README.md) | Extracts requirements, deadlines, and scoring criteria from a dense procurement document | Procurement, Legal | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/7-rfp-parser/rfp_parser_workbook.ipynb) |
| 8 | [Multi-Agent Research](./examples/8-multi-agent-research/README.md) | Supervisor coordinates a researcher and a writer; each hands off a typed result | Strategy, Research | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/8-multi-agent-research/multi_agent_research_workbook.ipynb) |
| 9 | [Contract Reviewer](./examples/9-contract-reviewer/README.md) | Reviews contracts and flags risks; every finding must cite the clause it came from | Legal, Procurement | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/9-contract-reviewer/contract_reviewer_workbook.ipynb) |
| 10 | [Due Diligence](./examples/10-due-diligence/README.md) | Reads multiple company documents and produces a unified risk register with severity and likelihood | Finance, M&A, Legal | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/10-due-diligence/due_diligence_workbook.ipynb) |
| 11 | [Proposal Writer](./examples/11-proposal-writer/README.md) | Supervisor breaks down an RFP; specialist agents draft each section; assembler returns a full proposal | Sales, Consulting | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/11-proposal-writer/proposal_writer_workbook.ipynb) |
| 12 | [Board Pack Reviewer](./examples/12-board-pack-reviewer/README.md) | Reads a board pack and produces a director briefing: top risks, information gaps, questions for management | Governance, Board, Finance | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/12-board-pack-reviewer/board_pack_workbook.ipynb) |
| 13 | [M&A Screener](./examples/13-ma-screener/README.md) | Scores acquisition targets across strategic fit, financials, and operations; blocked below threshold | Corporate Finance, M&A | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/13-ma-screener/ma_screener_workbook.ipynb) |
| 14 | [Executive Assistant](./examples/14-exec-assistant/README.md) | One email or transcript in; draft reply, action items, and follow-up tracker out simultaneously | Operations, Executive Office | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/14-exec-assistant/exec_assistant_workbook.ipynb) |
| 15 | [Regulatory Researcher](./examples/15-regulatory-researcher/README.md) | Analyses regulatory documents and returns obligations, deadlines, and penalties; every item cites its article | Compliance, Legal, Risk | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/15-regulatory-researcher/regulatory_researcher_workbook.ipynb) |
| 16 | [Management Consulting](./examples/16-mgmt-consulting/README.md) | Identifies inefficiencies and places each recommendation on an effort-vs-impact matrix, quick wins first | Operations, Finance, Consulting | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/16-mgmt-consulting/mgmt_consulting_workbook.ipynb) |
| 17 | [Corporate Finance](./examples/17-corporate-finance/README.md) | Rates a company across five readiness dimensions; any dimension failing blocks the overall verdict | Corporate Finance, CFO | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/17-corporate-finance/corporate_finance_workbook.ipynb) |
| 18 | [Fundraising Agent](./examples/18-fundraising-agent/README.md) | Same company brief produces different investor materials shaped for VC, PE, and family office audiences | Corporate Finance, Investor Relations | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/18-fundraising-agent/fundraising_agent_workbook.ipynb) |
| 19 | [Financial Modeller](./examples/19-financial-modeller/README.md) | LLM reads a business brief and extracts assumptions; Python runs the 3-year P&L, cash flow, and DSCR math | Finance, FP&A | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/19-financial-modeller/financial_modeller_workbook.ipynb) |
| 20 | [Strategy Consultant](./examples/20-strategy-consultant/README.md) | Agent searches market size, competitors, and regulatory data then delivers an ENTER / MONITOR / AVOID verdict | Strategy, Corporate Development | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/20-strategy-consultant/strategy_consultant_workbook.ipynb) |
| 21 | [Client Intel Monitor](./examples/21-client-intel/README.md) | Searches news, filings, leadership changes, and market signals then produces a typed brief with account actions | Sales, Account Management | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/21-client-intel/client_intel_workbook.ipynb) |
| 22 | [AI Project Manager](./examples/22-ai-pmo/README.md) | Parses project updates — emails, call notes, messages — and keeps a typed state object current; re-derives RAG status each time | Operations, PMO | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/22-ai-pmo/ai_pmo_workbook.ipynb) |
| 23 | [Knowledge Management](./examples/23-knowledge-mgmt/README.md) | Finds relevant past work in a corpus before drafting; the output must cite which documents it drew from | Professional Services, Knowledge Management | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/23-knowledge-mgmt/knowledge_mgmt_workbook.ipynb) |
| 24 | [OpenRouter Structured Output](./examples/24-openrouter-structured-output/README.md) | Same email triage schema as example 2, running on any OpenRouter model — change the model string, nothing else changes | Operations, Engineering | `OPENROUTER_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/24-openrouter-structured-output/openrouter_structured_output_workbook.ipynb) |
| 25 | [Manual ReAct Loop](./examples/25-openrouter-react-agent/README.md) | Implements the tool-calling loop from scratch in 80 lines — message list, tool dispatch dict, while loop, no framework | Engineering, Data Science | `OPENROUTER_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/25-openrouter-react-agent/openrouter_react_agent_workbook.ipynb) |
| 26 | [PydanticAI Agent](./examples/26-pydantic-ai-agent/README.md) | Invoice extractor built with PydanticAI — the schema defines the agent's output and tools before any logic is written | Finance, Operations | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/26-pydantic-ai-agent/pydantic_ai_agent_workbook.ipynb) |
| 27 | [Multi-Provider Fan-Out](./examples/27-multi-provider-fan-out/README.md) | Sends the same question to GPT-4o-mini, Mistral, and Llama in parallel; collects typed opinions; synthesises a consensus | Strategy, Research | `OPENROUTER_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/27-multi-provider-fan-out/multi_provider_fan_out_workbook.ipynb) |
| 28 | [Dependency Vulnerability Scanner](./examples/28-dependency-vuln-scanner/README.md) | Reads requirements.txt, calls OSV.dev for live CVE data (no key needed), LLM ranks findings by severity and writes the upgrade action plan | Engineering, DevSecOps | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/28-dependency-vuln-scanner/dependency_vuln_scanner_workbook.ipynb) |
| 29 | [SEC ESG Extractor](./examples/29-sec-esg-extractor/README.md) | Fetches any company's latest 10-K from SEC EDGAR (no key needed), extracts ESG disclosures, maps them to CSRD categories, and scores completeness | ESG, Investor Relations, Legal | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/29-sec-esg-extractor/sec_esg_extractor_workbook.ipynb) |

</details>

---

## Structure

Every example follows the same layout:

```
examples/N-example-name/
  src/schema.py      # Pydantic models — defines what the agent produces
  src/workflow.py    # LLM calls, tool definitions, agent logic
  main.py            # 2-3 runnable scenarios
  *_workbook.ipynb   # Colab notebook — same code, no local setup needed
  README.md
```

Install once, run any example:

```bash
pip install -r requirements.txt
```

Keys needed:
- `OPENAI_API_KEY` — most examples
- `OPENROUTER_API_KEY` — examples 24, 25, 27 (free tier available at openrouter.ai)
