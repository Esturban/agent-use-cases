# 9 — Contract Reviewer

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/9-contract-reviewer/contract_reviewer_workbook.ipynb)

A freelancer, founder, or legal ops team paste in a commercial contract and get back a prioritised risk register, a list of missing standard protections, and a ranked negotiation checklist — all grounded in the actual clause numbers.

---

## What it does

You feed the agent any contract text — a services agreement, an NDA, a vendor deal. It reads the full document and returns a structured review broken into three parts: risk findings (each one tied to a specific section), protections that are absent but should be present, and a negotiation point list ranked from must-have to nice-to-have. The output is machine-readable and ready to drop into a dashboard, a Notion doc, or an email to a lawyer.

---

## How it works

Every risk finding is required to cite the exact clause it came from — the agent will not return a finding without a `clause_reference`. This forces it to stay grounded in the document rather than generating generic legal commentary. The overall review also captures the contract type, counterparty, governing law, an overall risk rating, and a two-sentence executive summary suitable for a non-lawyer. Two sample contracts ship with the example — a lopsided Professional Services Agreement and a straightforward NDA — so you can see the difference in output immediately.

---

## What you'll see

```
=================================================================
CONTRACT: Professional Services Agreement
=================================================================
Type:         Professional Services Agreement
Counterparty: Vendor Ltd
Governing law:State of Delaware
Overall risk: HIGH

EXECUTIVE SUMMARY
This agreement is heavily weighted in favour of the Client across payment,
IP, and termination terms. Service Provider takes on unlimited liability
while Client bears none, creating severe commercial exposure.

RISK FINDINGS (5)

  [CRIT] [Section 5] Client faces zero liability while Service Provider's is unlimited.
     Impact:   Service Provider has no financial ceiling on damages claims.
     Redline:  Add mutual limitation of liability capped at 12 months of fees paid.

  [HIGH] [Section 3] IP assignment sweeps in pre-existing tools and methodologies.
     Impact:   Service Provider loses ownership of proprietary methods built before this contract.
     Redline:  Carve out pre-existing IP; assign only work product created specifically for Client.

  [HIGH] [Section 2] 90-day payment terms with no late-payment interest.
     Impact:   Client can delay payment indefinitely at no cost.
     Redline:  Reduce to net-30; add 1.5% monthly interest on overdue amounts.

MISSING PROTECTIONS (2)

  - Dispute resolution clause
    Why:      Without it, any disagreement defaults straight to litigation.
    Add:      Parties shall first attempt mediation for 30 days before pursuing legal action.

  - Indemnification cap
    Why:      Unlimited indemnity exposure is uninsurable for most service providers.
    Add:      Each party's indemnification obligation shall not exceed fees paid in the prior 12 months.

NEGOTIATION POINTS (3)

  [!!!] IP carve-out for pre-existing work
    Current:  All work product including pre-existing tools assigned to Client.
    Target:   Assignment covers only new work product created under this Agreement.

  [!!] Payment terms
    Current:  90 days, no interest on late payment.
    Target:   Net-30 with 1.5% monthly interest after due date.

  [!] Termination symmetry
    Current:  Client can terminate immediately; Service Provider needs 180 days notice.
    Target:   Equal 30-day notice period for both parties.
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/9-contract-reviewer/main.py
```

---

## Files

```
9-contract-reviewer/
  src/schema.py      # Pydantic models: RiskFinding, MissingProtection, NegotiationPoint, ContractReview
  src/workflow.py    # Calls the model with a citation-enforcing system prompt and returns a ContractReview
  main.py            # Runs two sample contracts (Services Agreement, NDA) and prints formatted output
  README.md
```
