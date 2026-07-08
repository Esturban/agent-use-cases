# 97 · Ledger Integrity Supervisor

Orchestrates a period-close controls cycle, consolidates every exception into one ranked register, and requires a human controller's sign-off before the close can be marked complete.

**Business problem:** A period close touches journal entries, bank reconciliation, fixed assets, payment screening, and access controls -- five checks that are each individually correct, run by five different people or systems. But a pile of correct point checks is not itself a control: nothing stops one team from closing the books while another team's exception sits unreviewed, and nothing connects the dots when the same identity or vendor shows up in more than one check's findings.

**How it works:** Five checks run every close cycle -- journal-entry balance, bank-to-GL matching, fixed-asset depreciation math, payment fraud rules, and segregation-of-duties conflicts. All five are plain deterministic Python, not model judgment, because every one of them has a computable right answer. A simple cross-check then looks for the same identity or vendor showing up in more than one check's findings -- in the example scenario, the same preparer who posted an unbalanced entry also holds two conflicting access roles, and the vendor on that entry is also the counterparty on an unmatched, fraud-flagged bank transaction. The most financially material exception is held for a human controller to approve, edit, or reject before the cycle can move past it. The one thing an LLM actually does here is write the final audit narrative -- and even that step is handed the exact numbers and correlations already computed, rather than asked to add them up itself.

**How to run:**
```
cp .env.example .env  # add OPENAI_API_KEY
python examples/97-ledger-integrity-supervisor/main.py
```

**Reused, not rebuilt:** the journal-entry and bank-reconciliation checks are adapted from the already-shipped standalone examples 44 and 46. The `ProposedAction`/`ApprovalDecision`/`ActionResult` gate shape is copied from the approval-gate pattern (id 90), the same way example 91 reuses it, so each example stays independently deployable.
