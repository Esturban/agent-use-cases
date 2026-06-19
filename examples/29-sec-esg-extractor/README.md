# 29 — SEC ESG Extractor

Point it at any public company ticker and it fetches the latest 10-K directly from SEC EDGAR (no API key), extracts ESG disclosures, maps them to CSRD reporting categories, and scores the company's disclosure completeness.

---

## What it does

You pass in a stock ticker and get back:

- Every ESG disclosure found in the filing, mapped to a CSRD category (Climate Change, Governance, Own Workforce, etc.)
- Completeness rating per topic: FULL, PARTIAL, or MINIMAL
- Specific gaps versus what CSRD would require
- An overall CSRD coverage score (0–100)
- The 3 strongest disclosure areas and 3 critical gaps
- A plain-English analyst note on ESG maturity

---

## How it works

`_search_cik()` resolves the ticker to a CIK via EDGAR's company tickers endpoint. `_latest_10k()` pulls the most recent 10-K accession number from the submissions API. `_fetch_filing_text()` downloads the primary HTML document and strips tags. `_extract_esg_sections()` scans for ESG-relevant markers (climate, governance, human capital, etc.) to keep the context window focused. The extracted text goes to `gpt-4o-mini` via structured output, which maps each disclosure to a CSRD category and scores completeness.

All EDGAR endpoints are public and require no authentication — only a valid User-Agent header.

---

## What you'll see

```
============================================================
Analysing: Microsoft Corporation (MSFT)
============================================================

Microsoft Corporation — 2024 10-K
CSRD Coverage Score: 68/100
Disclosures found: 12

Strongest areas: Climate Change | Governance | Own Workforce
Critical gaps:   Biodiversity & Ecosystems | Pollution | Workers in Value Chain

Disclosures (top 5):

  [FULL] Climate Change — GHG Emissions
  Section: Item 1. Business
  Text: Microsoft has committed to being carbon negative by 2030 and to removing all the carbon
        it has emitted since its founding by 2050...
  
  [PARTIAL] Own Workforce — Employee Wellbeing
  Section: Item 7. MD&A
  Text: We offer comprehensive benefits including healthcare, 401(k) matching, and parental leave...
  Gaps: Quantitative wellbeing metrics missing; No breakdown by region or employment category

Analyst note:
  Microsoft provides one of the more complete ESG disclosures among US tech companies,
  with strong climate commitments and governance transparency. The most significant CSRD gap
  is biodiversity — the filing contains no material disclosure on ecosystem impact or 
  nature-related financial risks, which CSRD's ESRS E4 would require.
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env -- SEC EDGAR needs no key
python examples/29-sec-esg-extractor/main.py
```

---

## Files

```
29-sec-esg-extractor/
  src/schema.py      # ESGDisclosure, ESGReport with CSRD category mapping
  src/workflow.py    # SEC EDGAR fetch + section extraction + LLM analysis
  main.py            # Microsoft and ExxonMobil as contrasting examples
  README.md
```
