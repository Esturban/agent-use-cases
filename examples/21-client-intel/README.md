# 21 — Client Intelligence Monitor

Give it a company name. It searches four sources in parallel — press, regulatory filings, leadership changes, market signals — and delivers a single structured brief with recommended account actions.

---

## What it does

You pass in a company name and get back:

- Recent funding rounds (round type, size, investor)
- Executive moves (hires, departures, promotions)
- Regulatory exposures (topic, severity, one-line summary)
- Strategic signals (what they're doing and why it matters to you)
- Prioritised relationship actions for the account team

---

## How it works

A LangGraph ReAct agent calls four research tools — news search, regulatory filings, leadership tracker, and market signals — then a second structured LLM call converts all findings into a typed `ClientIntelBrief`.

The tools use mock data here. Swap them out for Exa, a CRM API, or an SEC EDGAR connector and the schema and synthesis step remain identical.

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/21-client-intel/main.py
```

---

## Files

```
21-client-intel/
  src/schema.py      # FundingEvent, LeadershipChange, RegulatoryExposure, StrategicSignal, ClientIntelBrief
  src/workflow.py    # ReAct agent + four mock source tools
  main.py            # 2 companies: Acme Corp, Beta Industries
  README.md
```
