# agent-use-cases

Twelve production-style agent examples, each isolating one pattern from the agent harness.
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

</details>

---

## Layout

```
examples/
  1-basic-react-agent/
  2-email-triage/
  ...
  12-board-pack-reviewer/
    src/schema.py      # Pydantic models
    src/workflow.py    # agent logic
    main.py            # runnable entry point
    *_workbook.ipynb   # Colab-ready notebook
    README.md
requirements.txt
.env.example
```

Each example is independent — install once, run any.
