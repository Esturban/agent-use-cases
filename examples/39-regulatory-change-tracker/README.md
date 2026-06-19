# 39 — Regulatory Change Tracker

Delta-aware compliance pipeline: diffs a regulatory update against an existing obligation register, cross-references each new obligation against a contract corpus, scores exposure severity, and writes a versioned compliance state object.

## Prerequisites

This example builds on patterns introduced in earlier examples:

- [#7 — RFP Parser](../7-rfp-parser/) — structured extraction from legal/procurement text
- [#9 — Contract Reviewer](../9-contract-reviewer/) — clause-level contract analysis
- [#15 — Regulatory Researcher](../15-regulatory-researcher/) — regulatory text ingestion and summarisation
- [#22 — AI PMO](../22-ai-pmo/) — versioned state management and action tracking

## What it does

1. **Ingest** a `RegulatoryUpdate` — raw text, jurisdiction, and effective date.
2. **Diff** the update against an `ObligationRegister` — the LLM reads both and returns only net-new obligations not already covered by existing register entries.
3. **Extract** each net-new obligation as a typed `NewObligation` with source article citation, category, and effective date.
4. **Assess exposure** — for each net-new obligation, the agent cross-references it against every contract in the corpus in parallel, identifying exposed clauses and scoring impact as `none`, `moderate`, or `severe`.
5. **Score and draft** — each `ObligationImpact` carries contract-level `ContractExposure` objects plus a rolled-up severity score and a concrete remediation action item.
6. **Write versioned state** — a `ComplianceState` object is updated: version incremented, new obligations appended as `pending`, `pending_actions` extended, and `last_update_summary` written.
7. **Return** a `ChangeTrackerResult` — net-new count, all impact assessments, the updated state, and an executive summary.

## Architecture

```
main.py
└── src/workflow.py          run(update, register, contracts, state) -> ChangeTrackerResult
    ├── _extract_obligations()   Stage 1: LLM diff -> list[NewObligation]
    ├── _assess_exposure()       Stage 2: LLM exposure per obligation (parallel)
    ├── _update_state()          Stage 3: LLM state writer -> ComplianceState (versioned)
    ├── src/prompts.py           EXTRACTION_SYSTEM, EXPOSURE_SYSTEM, STATE_UPDATE_SYSTEM
    └── src/schema.py            ObligationRegister, RegulatoryUpdate, NewObligation,
                                 ContractExposure, ObligationImpact, ComplianceState,
                                 ChangeTrackerResult
```

## Harness focus

**Delta-aware stateful extraction.** The key pattern is the three-stage pipeline:

1. The extraction stage does not blindly enumerate all obligations — it diffs the incoming update against the stored register and returns only what is genuinely net-new. This prevents duplicate obligations accumulating across update cycles.
2. The exposure stage runs one LLM call per new obligation in parallel via `ThreadPoolExecutor`, keeping latency proportional to the number of new obligations, not the size of the contract corpus.
3. The state update stage is itself an LLM call that writes a new `ComplianceState` version, preserving immutability — each call produces a new object rather than mutating the previous one.

**Framework:** OpenAI SDK (structured outputs via `response_format` with `json_schema` and `strict: true`).

**Comparable patterns:**
- LangGraph stateful graphs — `ComplianceState` is analogous to a LangGraph `State` annotation; the three stages map to graph nodes with typed edges.
- LangChain with memory — `ObligationRegister` plays the role of a memory store; `_extract_obligations` is the retrieval-augmented diffing step.
- CrewAI sequential tasks — the extraction → exposure → state-update pipeline maps directly to a three-task CrewAI crew with typed output passing between agents.

## Setup

```bash
pip install openai pydantic python-dotenv
```

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_key
```

## Usage

```bash
python main.py
```

## Output

```
Regulatory Change Tracker — Demo Run

Running Scenario A: GDPR Amendment — Data Retention Cap

============================================================
  Scenario A: GDPR Amendment
============================================================
Update ID      : GDPR-AMD-2025-01
Net-new count  : 2

Summary:
  Processed GDPR-AMD-2025-01: 2 net-new obligation(s) identified for EU.
  Highest exposure level: severe.
  Top priority action: Amend DataSync SaaS Agreement Clause 8.1 to reduce retention
  from 36 months to 24 months to comply with Article 5(1)(e) effective 2025-07-01.

Impact Assessments:

  [1] Article 5(1)(e) GDPR (amended) — DATA-RETENTION
      Obligation : Controllers must implement a maximum retention period of 24 months
                   for all personal data processed under a legitimate interest basis...
      Overall    : SEVERE
      Action     : Amend DataSync SaaS Agreement Clause 8.1 to reduce retention...
      Contract   : DataSync SaaS Agreement v3.2 -> severe

  [2] Article 13(2)(a) GDPR (amended) — DISCLOSURE
      Obligation : Privacy notices must explicitly state the 24-month maximum retention period...
      Overall    : MODERATE
      Action     : Update privacy notice template to include 24-month retention cap...

Updated Compliance State (v4):
  Last updated   : 2025-06-19
  Obligations    : 4 total
  Pending actions: 3
    - Review consent capture flows against Article 7(1) requirements before Q1 audit.
    - Amend DataSync SaaS Agreement Clause 8.1 to reduce retention from 36 months...
    - Update privacy notice template to include 24-month retention cap statement...
```

## Workbook

Open `regulatory_change_tracker_workbook.ipynb` for an interactive walkthrough with starter exercises and an answer key.
