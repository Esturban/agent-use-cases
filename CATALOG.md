# Example Catalog

Difficulty and utility ratings for all 27 examples. Use this to decide where to start or which example to adapt for a specific problem.

**Difficulty scale:** 1 = single LLM call with a schema, 5 = multi-agent with tool loops, parallel calls, and stateful merging

**Utility:** the business problem it solves, who benefits, and what you'd need to change to use it in production

---

## Beginner — Learn the fundamentals (difficulty 1–2)

Start here if you're new to structured AI outputs or want to understand how typed results work before adding tools or agents.

| # | Example | Difficulty | What makes it work | Production swap |
|---|---------|:----------:|--------------------|-----------------|
| 2 | Email Triage | 1 | Single LLM call with a schema — urgency and category come back as typed fields, not free text | Replace the sample emails with your email API or webhook payload |
| 3 | Invoice Extractor | 1 | Adds validation and automatic retry when the output doesn't match the schema | Point at your invoice documents or an OCR output |
| 4 | Lead Qualifier | 1 | Puts a scoring rubric in the prompt; forces the model to cite which criterion drove each score | Replace the ICP criteria with your own qualification framework |
| 5 | Support Ticket Router | 2 | Classification result feeds a conditional branch — different logic runs for different ticket types | Wire the output to your helpdesk system (Zendesk, Intercom, etc.) |
| 6 | Resume Screener | 1 | Same schema applied to many inputs — results are directly comparable and sortable | Replace sample resumes with your ATS export |
| 26 | PydanticAI Agent | 1 | Shows how schema-first frameworks (PydanticAI) differ from chain-first ones (LangChain) | Good reference if you're choosing a framework |

---

## Intermediate — Document extraction and multi-step pipelines (difficulty 2–3)

These examples extract typed information from longer inputs, combine multiple LLM calls, or add simple tool use.

| # | Example | Difficulty | What makes it work | Production swap |
|---|---------|:----------:|--------------------|-----------------|
| 1 | Basic ReAct Agent | 2 | Model decides when to call a tool, reads the result, and loops until it has an answer | Replace the math tools with any real API call |
| 7 | RFP Parser | 2 | Pulls structured data from a long, dense document in one pass | Feed it any procurement document or specification |
| 9 | Contract Reviewer | 3 | Every risk finding must cite the clause number — no ungrounded assertions allowed | Point at your contract templates or uploaded PDFs |
| 12 | Board Pack Reviewer | 2 | Long document in, executive-framed structured output out | Works on any board report, investor update, or management pack |
| 14 | Executive Assistant | 2 | One input produces three typed outputs at once — draft, actions, and follow-up tracker | Connect to your email or meeting transcript pipeline |
| 15 | Regulatory Researcher | 3 | Every obligation and penalty must cite its source article, not just describe it | Point at any regulatory document — GDPR, SEC rules, sector-specific regs |
| 19 | Financial Modeller | 2 | LLM extracts assumptions from prose; Python does the arithmetic deterministically | Replace the sample briefs with your own financial inputs |
| 24 | OpenRouter Structured Output | 1 | Identical to example 2 but runs on any OpenRouter model — one variable change | Use when you need a specific model not on OpenAI directly |
| 25 | Manual ReAct Loop | 2 | Shows exactly what LangGraph abstracts — useful before you commit to a framework | Reference implementation; extend with any tool you want |

---

## Advanced — Multi-agent, tool-augmented, and stateful (difficulty 3–4)

These examples coordinate multiple agents, maintain state across inputs, or integrate research tools to ground outputs in real data.

| # | Example | Difficulty | What makes it work | Production swap |
|---|---------|:----------:|--------------------|-----------------|
| 8 | Multi-Agent Research | 3 | Supervisor delegates to a researcher and a writer with typed handoffs between them | Replace the research tool with a real web search or database query |
| 10 | Due Diligence | 3 | Reads N documents independently, then merges findings into one risk register | Feed it the actual target company's financials, contracts, and filings |
| 11 | Proposal Writer | 4 | Supervisor decomposes an RFP, specialist agents draft each section, assembler produces the final document | Wire to your RFP intake and document output system |
| 13 | M&A Screener | 3 | Scores across multiple dimensions with a threshold gate — below threshold blocks the overall verdict | Replace scoring criteria with your own investment thesis |
| 16 | Management Consulting | 3 | Places recommendations on an effort-vs-impact matrix and sorts by quick wins | Use on any operational or cost review input |
| 17 | Corporate Finance | 3 | Multi-dimension gate logic — any single dimension failing blocks the overall readiness verdict | Adapt dimensions to match your capital raising or IPO checklist |
| 18 | Fundraising Agent | 3 | Same data produces different outputs shaped for different investor personas | Replace VC/PE/family office framing with your own target investor types |
| 20 | Strategy Consultant | 3 | ReAct agent calls market, competitor, and regulatory tools; synthesis pass converts findings to a typed verdict | Replace mock tools with Exa, Tavily, or your own data sources |
| 21 | Client Intel Monitor | 3 | Four tool categories — news, filings, leadership, signals — each produces a different schema section | Connect to your CRM, news APIs, or SEC EDGAR |
| 22 | AI Project Manager | 3 | Each update is extracted into a delta then merged with the current state; RAG status re-derived each time | Point at your project email threads, Slack exports, or call transcripts |
| 23 | Knowledge Management | 3 | LLM-as-retriever selects relevant docs before drafting; output must cite which docs it drew from | Replace the in-memory corpus with a vector store or SharePoint index |

---

## Expert — Multi-provider and parallel orchestration (difficulty 4–5)

These examples run multiple models in parallel, synthesise across providers, or demonstrate framework-independent patterns.

| # | Example | Difficulty | What makes it work | Production swap |
|---|---------|:----------:|--------------------|-----------------|
| 27 | Multi-Provider Fan-Out | 4 | Same prompt sent to three models in parallel; typed opinions normalised; synthesis produces a consensus | Add more models to the list — any OpenRouter model string works |

---

## By department

Quick reference if you're looking for examples relevant to a specific team.

| Department | Examples |
|------------|---------|
| Finance / FP&A | 3, 10, 13, 17, 18, 19 |
| Sales / Business Development | 4, 11, 21 |
| Legal / Compliance | 7, 9, 15 |
| Operations / PMO | 2, 5, 14, 16, 22 |
| Strategy | 8, 12, 20, 27 |
| HR / Talent | 6 |
| Engineering | 1, 24, 25, 26 |
| Knowledge / Professional Services | 23 |
| Account Management | 21 |
| Governance / Board | 12 |
