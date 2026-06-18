# 7 — RFP Parser

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/7-rfp-parser/rfp_parser_workbook.ipynb)

Procurement teams and vendors waste hours reading dense government RFPs to find deadlines, mandatory requirements, and evaluation weights buried in pages of legal prose. This example automates that work — paste in the document, get back a clean, structured summary ready for a bid/no-bid decision.

---

## What it does

The agent takes a raw RFP document as text and returns every deadline, requirement, and scoring criterion in a typed structure. It distinguishes hard deadlines from informational ones, flags mandatory requirements versus preferred qualifications, assigns a category to each requirement (technical, legal, administrative, financial), and extracts budget ceiling and contract duration when stated. The output is immediately usable in a bid checklist, compliance tracker, or proposal planning tool.

---

## How it works

The agent reads the full document text and extracts every field in a single pass. Because real RFPs bury requirements across multiple sections — scope, qualifications, legal terms — the system prompt explicitly instructs the model to find all requirements, not just the most prominent ones. Each requirement gets an ID, category, text, and a mandatory flag. Deadlines are classified as hard or soft based on whether missing them disqualifies a submission. Optional fields like budget ceiling and contract duration are returned as null when the document does not state them clearly.

---

## What you'll see

```
Title:             Enterprise Cloud Migration and Managed Services
Agency:            City of Riverside, Office of Information Technology
Budget ceiling:    $750,000
Contract duration: 3 years with two 1-year renewal options

Summary: The City of Riverside is seeking a vendor to migrate its on-premises
infrastructure to a FedRAMP-authorized cloud platform and provide managed services
for three years. The contract ceiling is $750,000 for the initial term.

DEADLINES (5)
  2026-06-20   Pre-proposal Conference
  2026-07-01   Questions Due
  2026-07-15   Proposal Submission Deadline [HARD]
  2026-08-01   Award Notification

REQUIREMENTS (8)
  REQ-01  [technical      ] [mandatory]
           Vendor must be a certified partner of at least one FedRAMP-authorized...
  REQ-02  [legal          ] [mandatory]
           Vendor must be registered to do business in the State of California...
  REQ-03  [administrative ] [mandatory]
           Vendor must carry minimum $2M general liability insurance...
  REQ-07  [technical      ] [preferred]
           Experience with municipal government IT modernization projects prefer...

SCORING CRITERIA (4)
   35%   Technical Approach and Methodology
   25%   Relevant Experience and References
   30%   Cost and Value
   10%   Staff Qualifications
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/7-rfp-parser/main.py
```

---

## Files

```
7-rfp-parser/
  src/schema.py      # Pydantic models: Deadline, Requirement, ScoringCriterion, RFPExtraction
  src/workflow.py    # Calls the model with structured output and returns an RFPExtraction object
  main.py            # Runs a sample City of Riverside RFP and prints the extracted fields
  README.md
```
