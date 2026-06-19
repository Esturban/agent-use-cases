# 40 — Self-Healing CI Agent

Bounded agentic repair loop: reads CI failure logs, classifies the error type, selects a repair strategy, applies it, re-validates, and loops up to N retries — emitting a structured postmortem on terminal failure.

## Prerequisites

- **#25** — Manual ReAct loop (bounded reason-act-observe pattern)
- **#28** — Dependency vulnerability scanner (dependency error classification)
- **#36** — Incident postmortem drafter (structured postmortem generation)

## What it does

Each CI failure is processed through four steps, repeated up to `max_retries` times:

1. **Classify** — the LLM reads the raw log snippet and returns a `FailureClassification`: error type (dependency, config, code, test, flaky, or unknown), one-sentence root cause, suggested strategy, and confidence score.
2. **Propose** — given the classification and all prior attempts, the LLM produces a `RepairAttempt`: the exact action to take, a patch description, and the strategy applied.
3. **Validate** — a second LLM call assesses whether the proposed patch would actually resolve the original failure, filling `validation_result` ("pass" / "fail" / "inconclusive") and explanatory notes.
4. **Loop or halt** — if the validation passes, the agent returns a resolved `HealingResult`. If retries are exhausted, the agent calls a final LLM pass to write a `RepairPostmortem` and returns an unresolved `HealingResult` with the postmortem attached.

## Architecture

```
main.py
└── src/workflow.py          # run(failure, max_retries) -> HealingResult
    ├── _classify()          # CIFailure -> FailureClassification
    ├── _propose_repair()    # CIFailure + classification + history -> RepairAttempt
    ├── _validate()          # CIFailure + attempt -> fills validation_result + notes
    └── _write_postmortem()  # CIFailure + classification + attempts -> RepairPostmortem
    ├── src/prompts.py       # CLASSIFY_SYSTEM, REPAIR_SYSTEM, VALIDATE_SYSTEM, POSTMORTEM_SYSTEM
    └── src/schema.py        # CIFailure, FailureClassification, RepairAttempt,
                             # RepairPostmortem, HealingResult
```

## Framework

Direct OpenAI SDK (`openai` Python package). No LangChain, no LangGraph — the loop is explicit Python.

## Comparable patterns

| Framework | Equivalent construct |
|-----------|----------------------|
| LangGraph | Conditional edges + state machine with a retry counter in graph state |
| LangChain | Agent executor with memory and a custom retry tool |
| CrewAI | Sequential tasks with retry logic wired between crew steps |

## Setup

```bash
pip install openai pydantic python-dotenv
```

Create a `.env` file in this directory:

```
OPENAI_API_KEY=your_openai_key
```

## Usage

```bash
python main.py
```

## Output examples

**Scenario A — resolved (dependency conflict)**

```
============================================================
Scenario A: build / install-dependencies
============================================================
Job:           build
Resolved:      True
Attempts:      1
Final strategy: pin_dependency
```

**Scenario B — terminal failure (flaky test)**

```
============================================================
Scenario B: test / run-unit-tests
============================================================
Job:           test
Resolved:      False
Attempts:      3

--- Postmortem ---
Error type:      flaky
Root cause:      Intermittent network timeout to api.stripe.com exhausts all retries
                 and cannot be resolved by a code-level patch.
Recommended fix: Mock the Stripe HTTP call in CI using responses or pytest-httpserver
                 so the test is no longer network-dependent.
Escalation:      All three retry attempts applied the "retry" strategy but the
                 test continued to fail due to external network instability. A human
                 engineer should introduce a test double for the Stripe API and
                 re-enable the test. Check CI runner outbound firewall rules as a
                 secondary investigation path.

Attempts made: 3
  [1] retry -> fail: Re-run the failing test step without changes
  [2] retry -> fail: Re-run with increased pytest timeout (--timeout=30)
  [3] skip_test -> fail: Mark test as xfail pending network isolation fix
```

## Workbook

Open `self_healing_ci_agent_workbook.ipynb` for an interactive walkthrough.
