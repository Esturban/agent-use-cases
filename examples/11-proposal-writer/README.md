# 11 — Proposal Writer

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/11-proposal-writer/proposal_writer_workbook.ipynb)

Consultancies and agencies spend hours manually reading RFPs and writing responses from scratch. This pipeline reads a raw RFP document and returns a fully drafted proposal — ready to edit and submit — in seconds.

---

## What it does

Paste in any RFP text and the pipeline returns a complete proposal document. A supervisor agent reads the RFP first, extracts every mandatory requirement, identifies win themes, and builds a structured writing brief. A writer agent then uses that brief to draft every section of the proposal: executive summary, methodology, team credentials, timeline, commercial terms, differentiators, and a compliance statement confirming all pass/fail requirements are met.

---

## How it works

The supervisor reads the RFP once and produces a structured outline — win themes, mandatory requirements flagged as pass/fail, evaluation criteria in priority order, and the exact sections to write. That outline becomes the handoff to the writer. The writer receives both the original RFP and the outline, so it drafts against confirmed requirements rather than guessing from raw text. Because mandatory items are extracted and labeled before writing begins, nothing slips through and every section connects back to how the client will score the bid.

---

## What you'll see

```
============================================================
STAGE 1 — RFP OUTLINE (Supervisor)
============================================================
Title:    Digital Transformation Office Maturity Assessment and Roadmap
Client:   Meridian Financial Services Group
Deadline: 30 March 2025

Requirements: 5 mandatory, 4 optional

Mandatory pass/fail:
  [M1] Firm must have completed at least three digital maturity assessments for regulated financial services clients in the past five years.
  [M2] Lead partner must have a minimum of 15 years' experience in financial services transformation.
  [M3] All data handling must comply with UK GDPR and FCA data governance requirements.
  [M4] Proposal must include a fixed-fee commercial structure.
  [M5] Draft deliverables must be provided within six weeks of contract signature.

Win themes (3):
  * Proven regulated-sector delivery track record
  * Independent, evidence-based maturity benchmarking
  * Speed to insight — quick wins within 90 days

Evaluation criteria (ranked):
  1. Relevant sector experience and case studies: 35 points
  2. Quality and specificity of proposed methodology: 30 points
  3. Team credentials and named personnel: 20 points
  4. Commercial value and fixed-fee clarity: 15 points

Sections to write: executive_summary, our_approach, team_and_credentials, timeline, commercial, why_us

============================================================
STAGE 2 — PROPOSAL DRAFT (Writer)
============================================================

--- EXECUTIVE SUMMARY ---
Meridian Financial Services Group has built a Digital Transformation Office with ambition
but without a clear measure of impact. We will deliver an independent maturity assessment
benchmarked against CMMI and the Gartner Digital Maturity Model, root cause analysis
backed by 20+ stakeholder interviews, and a prioritised 18-month roadmap — fixed fee GBP 175,000.

--- OUR APPROACH ---
Our four-phase methodology moves from discovery to delivery in ten weeks...

--- TEAM & CREDENTIALS ---
Our engagement lead has 18 years in financial services transformation across retail banking
and insurance. We have completed six regulated-sector maturity assessments since 2019.

--- TIMELINE ---
Weeks 1-2: Kick-off and stakeholder interview scheduling
Weeks 3-5: Maturity assessment and 20+ stakeholder interviews
Weeks 6-8: Root cause analysis and roadmap development
Weeks 9-10: Executive Committee presentation

--- COMMERCIAL ---
Fixed fee: GBP 175,000 exclusive of VAT. No time-and-materials components. Scope adjustment
negotiation available per MFSG RFP terms.

--- WHY US ---
Six completed digital maturity assessments for FCA-regulated firms since 2019, with a
lead partner holding 18 years of financial services transformation experience.

--- KEY DIFFERENTIATORS ---
  * Six completed digital maturity assessments in regulated financial services
  * Lead partner with 18 years financial services transformation experience
  * Fixed-fee guarantee — no scope creep surprises
  * Proprietary quick-win identification framework delivering results in 0-90 days

--- COMPLIANCE STATEMENT ---
This proposal confirms full compliance with all five mandatory requirements M1 through M5.
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/11-proposal-writer/main.py
```

---

## Files

```
11-proposal-writer/
  src/schema.py      # ProposalOutline and Proposal Pydantic models, plus RFPRequirement with mandatory flag
  src/workflow.py    # Two-agent pipeline: supervisor outlines the RFP, writer drafts every section
  main.py            # Runs a sample MFSG financial services RFP and prints both stages
  README.md
```
