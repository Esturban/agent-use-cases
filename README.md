# agent-use-cases

Eighteen production-style agent examples, each isolating one pattern from the agent harness.
Every example is a self-contained folder: `schema` → `workflow` → `main` → Colab workbook.

**Patterns covered:**

- **Action space** — reason → call tool → observe loop (ReAct)
- **Structured output** — Pydantic schemas as output contracts, with retry on validation failure
- **Grounded reasoning** — rubric in the prompt, model must cite evidence
- **Conditional routing** — classification result drives which branch runs next
- **Long-context extraction** — pull typed data from dense, multi-page documents
- **Subagent delegation** — supervisor coordinates specialist agents with typed handoffs
- **Citation-grounded critique** — every finding must cite the clause it comes from
- **Multi-document synthesis** — per-document extraction feeds a unified risk register
- **Multi-agent document generation** — supervisor decomposes brief, writer drafts full response
- **Executive critique** — NED-framed output identifies gaps and probing questions
- **Multi-criteria scoring** — nested dimension scores with threshold gating produce a ranked shortlist
- **Fan-out output** — one input simultaneously produces multiple typed schemas (reply + actions + follow-ups)
- **Citation-grounded regulation** — every obligation and penalty cites its source article
- **2D effort-impact matrix** — recommendations placed in quadrants and sorted by ROI
- **Dimensional gate logic** — go/no-go per dimension, overall status blocked by any single fail
- **Audience-targeted generation** — same company brief produces persona-specific outputs for VC, PE, and family office
- **Two-step pipeline** — LLM extracts parameters; Python runs the math deterministically
- **Tool-augmented research** — web search feeds structured synthesis; grounding replaces hallucination
- **Provider-agnostic structured output** — OpenRouter + openai SDK; swap the model string, the harness stays identical
- **Manual ReAct loop** — reason-act-observe without a framework; shows what orchestrators abstract away
- **Schema-first agent framework** — PydanticAI; types define tools and output contract before any logic is written
- **Code-tool use** — agent writes and executes Python to produce numeric results, not prose
- **Tool-augmented research** — web search feeds structured synthesis; grounding replaces hallucination
- **Multi-source intelligence** — multiple search tools consolidate into a single typed briefing object
- **Stateful entity tracking** — agent applies incremental updates from unstructured inputs to a typed project state
- **Retrieval-augmented generation** — past documents retrieved before drafting; output cites prior work
- **Multi-provider fan-out** — same prompt sent to N models in parallel; responses normalised into a typed consensus

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

Or open any workbook directly in Colab — no local setup needed.

---

## All Examples

<details open>
<summary>Click to expand</summary>

| # | Folder | What it demonstrates | Relevant Departments | Keys | Workbook |
|---|--------|----------------------|----------------------|:----:|:--------:|
| 1 | [1-basic-react-agent](./examples/1-basic-react-agent/README.md) | ReAct loop — reason → call tool → observe | Engineering, Data Science | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/1-basic-react-agent/basic_react_agent_workbook.ipynb) |
| 2 | [2-email-triage](./examples/2-email-triage/README.md) | `with_structured_output()` — schema-constrained classification | Operations, IT | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/2-email-triage/email_triage_workbook.ipynb) |
| 3 | [3-invoice-extractor](./examples/3-invoice-extractor/README.md) | Nested Pydantic schemas + field validation + retry on invalid output | Finance, Accounts Payable | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/3-invoice-extractor/invoice_extractor_workbook.ipynb) |
| 4 | [4-lead-qualifier](./examples/4-lead-qualifier/README.md) | Rubric in the system prompt — model scores and must cite criteria used | Sales, Business Development | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/4-lead-qualifier/lead_qualifier_workbook.ipynb) |
| 5 | [5-support-ticket-router](./examples/5-support-ticket-router/README.md) | Classification → conditional routing → escalation gate | Customer Service, IT | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/5-support-ticket-router/support_ticket_router_workbook.ipynb) |
| 6 | [6-resume-screener](./examples/6-resume-screener/README.md) | Same schema across many inputs — comparable, sortable structured output | HR, Talent Acquisition | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/6-resume-screener/resume_screener_workbook.ipynb) |
| 7 | [7-rfp-parser](./examples/7-rfp-parser/README.md) | Long-context extraction — typed requirement list from a dense document | Procurement, Legal | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/7-rfp-parser/rfp_parser_workbook.ipynb) |
| 8 | [8-multi-agent-research](./examples/8-multi-agent-research/README.md) | Supervisor + subagent delegation + typed handoff contracts | Strategy, Research | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/8-multi-agent-research/multi_agent_research_workbook.ipynb) |
| 9 | [9-contract-reviewer](./examples/9-contract-reviewer/README.md) | Citation-grounded critique — every risk finding must cite its clause | Legal, Procurement | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/9-contract-reviewer/contract_reviewer_workbook.ipynb) |
| 10 | [10-due-diligence](./examples/10-due-diligence/README.md) | Multi-document risk extraction + severity x likelihood matrix | Finance, M&A, Legal | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/10-due-diligence/due_diligence_workbook.ipynb) |
| 11 | [11-proposal-writer](./examples/11-proposal-writer/README.md) | Multi-agent document generation — supervisor + writer typed handoff | Sales, Business Development, Consulting | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/11-proposal-writer/proposal_writer_workbook.ipynb) |
| 12 | [12-board-pack-reviewer](./examples/12-board-pack-reviewer/README.md) | Executive critique — NED-framed output, information gaps, probing questions | Governance, Board, Finance | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/12-board-pack-reviewer/board_pack_workbook.ipynb) |
| 13 | [13-ma-screener](./examples/13-ma-screener/README.md) | Multi-criteria M&A scoring — DimensionScore nested model, threshold gating, ranked shortlist | Corporate Finance, M&A, Strategy | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/13-ma-screener/ma_screener_workbook.ipynb) |
| 14 | [14-exec-assistant](./examples/14-exec-assistant/README.md) | Fan-out output — one input → draft reply + action items + follow-up tracker simultaneously | Operations, Executive Office | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/14-exec-assistant/exec_assistant_workbook.ipynb) |
| 15 | [15-regulatory-researcher](./examples/15-regulatory-researcher/README.md) | Citation-grounded regulation — every obligation and penalty must cite its source article | Compliance, Legal, Risk | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/15-regulatory-researcher/regulatory_researcher_workbook.ipynb) |
| 16 | [16-mgmt-consulting](./examples/16-mgmt-consulting/README.md) | 2D effort-impact matrix — quadrant-typed recommendations sorted quick wins first | Operations, Finance, Consulting | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/16-mgmt-consulting/mgmt_consulting_workbook.ipynb) |
| 17 | [17-corporate-finance](./examples/17-corporate-finance/README.md) | Dimensional gate logic — pass/conditional/fail per dimension, any fail blocks overall status | Corporate Finance, CFO, Board | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/17-corporate-finance/corporate_finance_workbook.ipynb) |
| 18 | [18-fundraising-agent](./examples/18-fundraising-agent/README.md) | Audience-targeted generation — same brief → persona-specific materials for VC, PE, family office | Corporate Finance, Investor Relations | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/18-fundraising-agent/fundraising_agent_workbook.ipynb) |
| 19 | [19-financial-modeller](./examples/19-financial-modeller/README.md) | Two-step pipeline — LLM extracts assumptions, Python computes 3-year P&L, cash flow, and DSCR deterministically | Finance, FP&A | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/19-financial-modeller/financial_modeller_workbook.ipynb) |
| 20 | [20-strategy-consultant](./examples/20-strategy-consultant/README.md) | Tool-augmented research — ReAct agent calls market-size, competitor, and regulatory tools then synthesises a typed verdict | Strategy, Corporate Development | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/20-strategy-consultant/strategy_consultant_workbook.ipynb) |
| 24 | [24-openrouter-structured-output](./examples/24-openrouter-structured-output/README.md) | Provider-agnostic structured output — same Pydantic schema, any OpenRouter model string | Operations, Engineering | `OPENROUTER_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/24-openrouter-structured-output/openrouter_structured_output_workbook.ipynb) |
| 25 | [25-openrouter-react-agent](./examples/25-openrouter-react-agent/README.md) | Manual ReAct loop from scratch — message history + tool dispatch dict, no framework | Engineering, Data Science | `OPENROUTER_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/25-openrouter-react-agent/openrouter_react_agent_workbook.ipynb) |
| 26 | [26-pydantic-ai-agent](./examples/26-pydantic-ai-agent/README.md) | Schema-first agent framework — PydanticAI `Agent(result_type=Schema)` vs LangChain chain-first | Finance, Operations | `OPENAI_API_KEY` | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/26-pydantic-ai-agent/pydantic_ai_agent_workbook.ipynb) |

</details>

---

## Layout

```
examples/
  1-basic-react-agent/
  2-email-triage/
  ...
  18-fundraising-agent/
    src/schema.py      # Pydantic models
    src/workflow.py    # agent logic
    main.py            # runnable entry point
    *_workbook.ipynb   # Colab-ready notebook
    README.md
requirements.txt
.env.example
```

Each example is independent — install once, run any.
