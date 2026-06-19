# 15 — Regulatory Researcher

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/15-regulatory-researcher/regulatory_researcher_workbook.ipynb)

Compliance and legal teams spend hours reading regulations to find every obligation, deadline, and penalty that applies to their firm. This agent reads a regulatory document and extracts all of that into a structured, auditable summary — where every finding must cite the exact article it came from.

---

## What it does

You paste in the text of a regulation. The agent reads it and returns a structured compliance summary covering all obligations (who must do what, and whether it is ongoing), all deadlines with their article references, all financial penalties and their triggers, and a list of high-priority gaps firms commonly miss. Nothing appears in the output unless the agent can point to a specific article in the provided text.

---

## How it works

The agent is given a strict rule in its instructions: every obligation and every penalty must include the exact article reference, such as "Article 32(1)(a)". If the model cannot identify a specific article for a finding, it must leave it out rather than include an unsourced claim. This makes every line of output traceable back to the original document, so compliance staff can act on it without re-reading the source to verify.

---

## What you'll see

```
=================================================================
COMPLIANCE SUMMARY | Digital Markets Conduct Regulation 2024
=================================================================
Jurisdiction: United Kingdom
In force: 1 January 2025

OBLIGATIONS (4):

  [Article 4(1)] (one-off) Provide end-users with the ability to export
  personal data in a commonly used, machine-readable format upon request.
  Applies to: Designated undertakings
  Deadline: Within 30 days of a written request

  [Article 7(2)] (one-off) Publish interoperability technical specifications.
  Applies to: Designated undertakings operating a core platform service
  Deadline: Within 90 days of designation

  [Article 11(1)] (ongoing) Do not rank own products more favourably than
  third parties in search results, listings, or recommendations.
  Applies to: Designated undertakings

  [Article 15(1-2)] (ongoing) Submit quarterly compliance reports to the Authority.
  Applies to: Designated undertakings
  Deadline: Within 30 days of the end of each quarter

KEY DEADLINES (3):
  - Article 4(1): Data export within 30 days of written request
  - Article 7(2): Interoperability specs within 90 days of designation
  - Article 15(2): Quarterly report within 30 days of quarter end

PENALTIES (2):

  [Article 22(1)] Trigger: Breach of any obligation under the Regulation
  Max fine: 10% of total worldwide annual turnover
  Other: 20% for repeated infringement (Article 22(2))

  [Article 23(1)] Trigger: Ongoing non-compliance after Authority decision
  Max fine: 5% of average daily worldwide turnover per day of non-compliance

HIGH-PRIORITY GAPS (2):
  - Article 7(2) technical specifications deadline is often missed at designation
  - Article 15(3) report content requirements (evidence, complaints, spec changes) are frequently incomplete
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/15-regulatory-researcher/main.py
```

---

## Files

```
15-regulatory-researcher/
  src/schema.py      # Pydantic models: RegulatoryObligation, RegulatoryPenalty, ComplianceSummary
  src/workflow.py    # Calls the model with citation-enforcement instructions and returns a ComplianceSummary
  main.py            # Runs the agent on a fictional DMCR 2024 excerpt and prints the results
  README.md
```
