# 20 — Strategy Consultant

Give it a market name. It calls three research tools, pulls back market size, competitor profiles, and regulatory context, then delivers a structured verdict: enter, monitor, or avoid — with a scored opportunity/risk breakdown.

---

## What it does

You pass in a market description (e.g. "B2B SaaS Europe") and get back:

- TAM in USD billions and annual growth rate
- Top competitors with estimated market share, strengths, and weaknesses
- Scored opportunities and risks (1–10)
- A plain ENTER / MONITOR / AVOID verdict with a two-sentence rationale

---

## How it works

A LangGraph ReAct agent calls three research tools in sequence — market size, competitor landscape, regulatory environment — then a second structured LLM call converts the findings into a typed `MarketAnalysis` object.

The tools use mock data here, but the pattern is identical whether you point them at a real search API, a scraper, or an internal knowledge base.

---

## What you'll see

```
============================================================
Market: B2B SaaS Europe
============================================================
TAM:          $187.4B
Growth:       14.2% / year
Verdict:      ENTER
Rationale:    The European B2B SaaS market is growing faster than North America,
              with a fragmented competitor landscape leaving room for a focused
              entrant. Regulatory overhead is manageable for a compliant-by-design
              product.

Competitors (4):
  Salesforce               31% share
  SAP                      22% share
  HubSpot                  11% share
  Pipedrive                 6% share

Opportunities & Risks (6):
  [+] 9/10  GDPR-compliant positioning is a genuine wedge vs US-headquartered incumbents
  [+] 8/10  SMB segment is underserved — incumbents focus on enterprise
  [-] 7/10  Long sales cycles and procurement bureaucracy in German and French markets
  [+] 6/10  EUR weakness vs USD lowers effective price for local buyers
  [-] 5/10  High customer acquisition cost due to language and market fragmentation
  [-] 4/10  Incumbent lock-in through ERP integrations is hard to displace
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/20-strategy-consultant/main.py
```

---

## Files

```
20-strategy-consultant/
  src/schema.py      # CompetitorProfile, OpportunityRisk, MarketAnalysis
  src/workflow.py    # ReAct agent + three mock research tools
  main.py            # 2 markets: B2B SaaS Europe, Industrial IoT USA
  README.md
```
