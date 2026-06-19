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

## What you'll see

```
============================================================
Company: Acme Corp
============================================================

Funding:
  Q1 2025  Series C  $120M  (Sequoia Capital)

Leadership:
  Q4 2024  CFO  departure  -- Sandra Okafor
  Q1 2025  CFO  hire       -- Marcus Weil

Regulatory:
  [HIGH] Data Privacy: Under EU DPA investigation for cross-border data transfers without adequate safeguards.
  [MEDIUM] Antitrust: Informal inquiry opened into recent acquisition of a logistics software startup.

Strategic Signals:
  * Expanding into APAC with a new Singapore entity registered in March 2025.
    -> Budget cycle likely shifting; procurement decisions may move to regional leads.
  * Signed a three-year infrastructure deal with a hyperscaler announced at their Q1 earnings call.
    -> Long-term vendor lock-in underway — replatforming window is closing.

Recommended Actions:
  1. Schedule an exec briefing before their Q2 planning cycle closes — new CFO is still forming vendor opinions.
  2. Send a GDPR compliance resource kit to reinforce your value in their risk programme.
  3. Identify the Singapore country lead and initiate an introductory call within 30 days.
```

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
