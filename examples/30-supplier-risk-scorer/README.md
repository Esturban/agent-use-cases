# 30 — Supplier Risk Scorer

Pass in a list of suppliers and their countries of operation and get back a ranked geopolitical risk register. World Bank Worldwide Governance Indicators (WGI) supply the data — no API key, no subscription.

---

## What it does

You pass in a supplier list with countries and get back:

- World Bank governance scores per country: political stability, rule of law, control of corruption, regulatory quality
- A composite geopolitical risk score (0–100) per supplier
- Risk tier: LOW / MEDIUM / HIGH / CRITICAL
- Up to 3 specific governance risks driving the score
- A concrete mitigation action for each supplier
- A portfolio summary: highest-risk suppliers and the priority diversification action

---

## How it works

`_resolve_country_code()` maps country names to ISO alpha-3 codes. `_fetch_wgi()` calls the World Bank `/v2/country/{code}/indicator/{indicator}` endpoint for each of four WGI indicators — Political Stability, Rule of Law, Control of Corruption, and Regulatory Quality. Raw scores (range −2.5 to +2.5, higher is better) are passed to `gpt-4o-mini` via structured output, which converts them to a 0–100 risk scale, assigns tiers, surfaces key risks, and writes the portfolio summary as a typed `SupplierRiskRegister`.

The World Bank API is fully open — no registration, no rate limits on typical usage, updated annually.

---

## What you'll see

```
============================================================
Scoring: Apparel manufacturer supply chain
============================================================

Suppliers assessed: 5
Critical: 1  |  High: 2

Risk register (sorted by score):
  [CRITICAL] Sunrise Fabrics — Myanmar (MMR)
  Risk score: 88/100
  WGI: stability=-2.31  rule_of_law=-1.87  corruption=-1.52
  Key risks: Military junta instability | Human rights compliance exposure | Banking sector restrictions
  Mitigation: Initiate dual-sourcing from Vietnam or Bangladesh within 6 months; qualify backup supplier now.

  [HIGH] Apex Textiles — Bangladesh (BGD)
  Risk score: 58/100
  WGI: stability=-1.02  rule_of_law=-0.71  corruption=-0.94
  Key risks: Political volatility around elections | Labour rights compliance risk | Flood and climate exposure
  Mitigation: Require quarterly compliance audits and maintain 30-day safety stock.

Portfolio summary:
  Myanmar represents a CRITICAL concentration risk — the combination of political instability
  and international sanctions exposure makes immediate dual-sourcing essential. Bangladesh and
  Vietnam carry elevated but manageable risks with strong compliance frameworks available.
  The priority action is qualifying a Myanmar backup supplier before the next sourcing cycle.
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env -- World Bank API needs no key
python examples/30-supplier-risk-scorer/main.py
```

---

## Files

```
30-supplier-risk-scorer/
  src/schema.py      # GovernanceIndicators, SupplierRisk, SupplierRiskRegister
  src/workflow.py    # World Bank WGI API + LLM risk scoring
  main.py            # Apparel and electronics supplier chains as examples
  README.md
```
