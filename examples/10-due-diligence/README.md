# 10 — Commercial Due Diligence

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/10-due-diligence/due_diligence_workbook.ipynb)

Investors and acquirers need to read a pile of documents — financials, contracts, regulatory notices, management bios — and surface every risk before signing a deal. This example automates that review, producing a scored risk register with a clear go/no-go recommendation.

---

## What it does

You feed in a set of company documents as plain text. The agent reads each one individually, extracts key facts and red flags, then synthesises everything into a single due diligence report. Each risk is scored on both severity and likelihood, traced back to the document it came from, and paired with a recommended mitigation. The output is a structured risk register ready for a deal committee.

---

## How it works

The agent runs in two stages. First it processes each document independently — pulling out concrete findings, red flags, and open questions specific to that source. Then it takes all those per-document findings and synthesises them into one unified report, consolidating overlapping risks, scoring them on a severity-by-likelihood grid, and producing an executive summary with an overall assessment. Source attribution is preserved at every step so every risk item can be traced to its origin document.

---

## What you'll see

```
=================================================================
COMMERCIAL DUE DILIGENCE REPORT
=================================================================
Target:     Acme Technologies Ltd
Assessment: PROCEED_WITH_CONDITIONS

EXECUTIVE SUMMARY
Acme shows strong revenue growth (+35% YoY) and improving margins, but the
business carries significant concentration risk: a single customer accounts for
50% of revenue under a contract expiring in February 2025 with no auto-renewal.
An ICO enforcement notice for a GDPR breach and the CEO's planned relocation
add further execution risk. Proceeding is viable subject to contract renewal
confirmation and regulatory remediation evidence.

RISK REGISTER (6 items)
  SEV    LIK  AREA           TITLE
  -------------------------------------------------------
  [CRIT] [H]  commercial     Revenue concentration — RetailCo
         Source: Management Accounts (FY2024)
  [CRIT] [H]  commercial     Key contract expiry with no auto-renewal
         Source: Key Customer Contract (RetailCo)
  [HIGH] [H]  regulatory     ICO enforcement notice — GDPR breach
         Source: ICO Enforcement Notice
  [HIGH] [M]  financial      Overdue debtor days (87 vs 45 benchmark)
         Source: Management Accounts (FY2024)
  [HIGH] [M]  management     CEO relocation to Singapore — key-man risk
         Source: CEO Biography
  [MED ] [M]  operational    Three senior engineer departures in Q4
         Source: Management Accounts (FY2024)

KEY CONDITIONS (3)
  * Obtain written confirmation of RetailCo renewal before closing
  * Confirm ICO remediation programme is on track (DPO appointed, report filed)
  * Escrow or clawback mechanism to cover outstanding RetailCo receivables (GBP 310k)

FURTHER INVESTIGATION (2)
  ? Audit the IP assignment clause in Section 7 — assess impact on platform roadmap
  ? Verify CEO transition plan and board succession arrangements for Singapore move
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/10-due-diligence/main.py
```

---

## Files

```
10-due-diligence/
  src/schema.py      # DocumentFindings, RiskItem, and DDReport Pydantic models
  src/workflow.py    # Two-stage extract-then-synthesise pipeline
  main.py            # Four sample documents (accounts, contract, bio, ICO notice)
  README.md
```
