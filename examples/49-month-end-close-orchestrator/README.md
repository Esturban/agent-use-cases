# 49 -- Month-End Close Orchestrator

DAG-ordered task orchestration for a month-end financial close: a controller does not run every close task at once, and does not run them in an arbitrary order either -- subledgers close before intercompany elimination, elimination and accruals feed consolidation, consolidation feeds reporting. Miss a dependency and a downstream task looks "stuck" when the real problem is one upstream task that never finished.

**Prerequisites:** [22-ai-pmo](../22-ai-pmo), [43-customer-lifecycle-orchestrator](../43-customer-lifecycle-orchestrator)

## What it does

Takes a close task list -- 24 tasks across subledger close, intercompany elimination, accruals posting, FX revaluation, consolidation, and reporting, each with an owner, a dependency list, an SLA in hours, and a current `CloseTaskStatus` (`pending` / `in_progress` / `blocked` / `completed` / `exception`) -- and produces a live `CloseStatus`:

1. **Ready tasks** -- every pending task whose dependencies are all `completed`. Nothing else is eligible to dispatch.
2. **Blocked tasks** -- every `blocked` or `exception` task, with its recorded reason, its own SLA hours as the estimated delay, and every not-yet-completed task downstream of it (the blast radius, not just the one task).
3. **Critical path** -- the longest remaining chain of incomplete work through the dependency graph, computed fresh from the current statuses every time. If a blocked task sits on that path, it is named as the bottleneck and the close-wide delay is exactly that task's SLA hours added to the path.
4. **SLA risk** -- `critical` if the critical path is obstructed by a blocked task, `at_risk` if something is blocked but off the critical path, otherwise `on_track`.
5. **Narrative** -- an executive summary of the above, grounded in the numbers already computed; the model narrates, it does not recompute.

## Architecture

```
main.py
└── src/workflow.py            # run(period, tasks) -> CloseStatus
    ├── src/dag.py              # compute_ready_tasks, compute_blocked_tasks,
    │                           # compute_critical_path -- pure Python, no LLM
    ├── src/agents.py           # close_narrative_synthesizer -- the one LLM call
    ├── src/prompts.py          # CLOSE_NARRATIVE_SYSTEM
    └── src/schema.py           # CloseTask, BlockedTaskInfo, CriticalPathInfo,
                                 # CloseStatus
```

LangGraph wiring is deliberately thin: `compute_status` (deterministic) then `synthesize` (the one LLM call). Everything that has a computable right answer -- readiness, delay, critical path -- is computed in `dag.py`, not asked of the model.

**Harness focus:** DAG-ordered task orchestration with a typed status state machine and dependency gates. Downstream tasks are never marked ready until every upstream dependency reaches `completed`; a blocked task surfaces its reason and delay without silently stalling the tasks behind it; the critical path is re-derived from scratch on every call rather than cached, so resolving a blocker immediately reflects in the next status snapshot.

**Framework:** LangGraph (`StateGraph`, two nodes, no conditional routing needed -- every call takes the same path)

**Comparable patterns:** critical-path method (CPM) scheduling, Airflow/Dagster DAG schedulers, project-management Gantt tooling with dependency gates

## Setup

```bash
pip install -r requirements.txt
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
======================================================================
Scenario 1 -- Clean Close
======================================================================
Period          : 2026-06
Progress        : 14/24 (58.33%)
Ready to dispatch: ['T15']
SLA risk        : on_track
Critical path   : T15 -> T17 -> T18 -> T19 -> T20 -> T23 -> T24 (27.0h remaining)

Narrative:
The close is 58% complete with 14 of 24 tasks finished...

======================================================================
Scenario 2 -- Blocked: IC Out-of-Balance Investigation
======================================================================
Period          : 2026-06
Progress        : 13/24 (54.17%)
Ready to dispatch: []
SLA risk        : critical
Critical path   : T7 -> T15 -> T17 -> T18 -> T19 -> T20 -> T23 -> T24 (30.0h remaining)
Bottleneck      : T7
  BLOCKED T7 (IC out-of-balance investigation): Intercompany discrepancy of $18,750...
    Estimated delay : 3.0h
    Downstream impact: ['T15', 'T16', 'T17', 'T18', 'T19', 'T20', 'T21', 'T22', 'T23', 'T24']

Narrative:
The close is blocked -- T7 is stuck on an unresolved intercompany discrepancy...

======================================================================
Scenario 2 (resolved) -- IC Investigation Cleared
======================================================================
Period          : 2026-06
Progress        : 14/24 (58.33%)
Ready to dispatch: ['T15']
SLA risk        : on_track
Critical path   : T15 -> T17 -> T18 -> T19 -> T20 -> T23 -> T24 (27.0h remaining)

Narrative:
With the intercompany discrepancy resolved, the close is back on track...
```

Note how resolving T7 in the third run drops the critical path straight back to the clean-close path and length -- the orchestrator re-derives it from the current task statuses on every call, it never carries state forward from the previous run.

## Workbook

Open `month_end_close_orchestrator_workbook.ipynb` for an interactive walkthrough.
