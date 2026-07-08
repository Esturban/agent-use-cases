"""Runs the month-end close orchestrator over two scenarios.

Scenario 1 is a clean close: every task through fx_revaluation is complete,
nothing is blocked, and the orchestrator identifies the one task ready to
dispatch next plus the current critical path to sign-off.

Scenario 2 injects a blocked task: the intercompany out-of-balance
investigation (T7) is stuck on an unresolved discrepancy. Because
consolidation (T15) depends on T7, the entire downstream chain is gated --
ready_tasks is empty and the critical path routes straight through the
blocker, extending total_remaining_hours by exactly T7's SLA. The scenario
then resolves T7 and re-runs the orchestrator to show the critical path
re-derived from scratch, matching the clean-close path.
"""

import os

from dotenv import load_dotenv

from src.schema import CloseTask
from src.workflow import run

load_dotenv()

PERIOD = "2026-06"

# task_id -> (name, category, owner, depends_on, sla_hours)
_TASK_DEFS: dict[str, tuple[str, str, str, list[str], float]] = {
    "T1": ("AP subledger close", "subledger_close", "AP Team", [], 4),
    "T2": ("AR subledger close", "subledger_close", "AR Team", [], 4),
    "T3": ("Fixed assets subledger close", "subledger_close", "Fixed Assets Team", [], 3),
    "T4": ("Inventory subledger close", "subledger_close", "Inventory Team", [], 5),
    "T5": ("IC transaction matching", "intercompany_elimination", "Intercompany Team", ["T1", "T2"], 6),
    "T6": ("IC elimination entries", "intercompany_elimination", "Intercompany Team", ["T5"], 4),
    "T7": (
        "IC out-of-balance investigation",
        "intercompany_elimination",
        "Intercompany Team",
        ["T5"],
        3,
    ),
    "T8": ("Payroll accrual", "accruals_posting", "Payroll Team", ["T1"], 3),
    "T9": ("Bonus accrual true-up", "accruals_posting", "Payroll Team", ["T8"], 2),
    "T10": ("Vendor accrual true-up", "accruals_posting", "AP Team", ["T1"], 4),
    "T11": ("Revenue accrual", "accruals_posting", "AR Team", ["T2"], 3),
    "T12": ("FX rate table load", "fx_revaluation", "Treasury", [], 1),
    "T13": (
        "Balance sheet FX revaluation",
        "fx_revaluation",
        "Treasury",
        ["T12", "T1", "T2", "T3", "T4"],
        5,
    ),
    "T14": ("Intercompany balance FX revaluation", "fx_revaluation", "Treasury", ["T12", "T6"], 3),
    "T15": (
        "Trial balance roll-up",
        "consolidation",
        "Consolidation Team",
        ["T7", "T8", "T9", "T10", "T11", "T13", "T14"],
        6,
    ),
    "T16": ("Minority interest calculation", "consolidation", "Consolidation Team", ["T15"], 2),
    "T17": ("Consolidation adjustments", "consolidation", "Consolidation Team", ["T15"], 4),
    "T18": ("Elimination review sign-off", "consolidation", "Controller", ["T6", "T17"], 2),
    "T19": ("Draft financial statements", "reporting", "Reporting Team", ["T16", "T17", "T18"], 5),
    "T20": ("Management review", "reporting", "CFO", ["T19"], 3),
    "T21": ("Audit support package", "reporting", "Reporting Team", ["T19"], 4),
    "T22": ("Board reporting package", "reporting", "Reporting Team", ["T20"], 3),
    "T23": ("Regulatory filing prep", "reporting", "Compliance Team", ["T20"], 6),
    "T24": ("Final close sign-off", "reporting", "Controller", ["T21", "T22", "T23"], 1),
}


def _build_tasks(completed_ids: set[str], blocked: dict[str, str] | None = None) -> list[CloseTask]:
    """Build the full 24-task close list. Tasks in completed_ids are marked
    completed, tasks in blocked (task_id -> reason) are marked blocked, and
    everything else defaults to pending.
    """
    blocked = blocked or {}
    tasks = []
    for task_id, (name, category, owner, depends_on, sla_hours) in _TASK_DEFS.items():
        if task_id in blocked:
            status, reason = "blocked", blocked[task_id]
        elif task_id in completed_ids:
            status, reason = "completed", None
        else:
            status, reason = "pending", None
        tasks.append(
            CloseTask(
                task_id=task_id,
                name=name,
                category=category,
                owner=owner,
                depends_on=depends_on,
                sla_hours=sla_hours,
                status=status,
                blocked_reason=reason,
            )
        )
    return tasks


def _print_status(label: str, status) -> None:
    print(f"\n{'=' * 70}\n{label}\n{'=' * 70}")
    print(f"Period          : {status.period}")
    print(f"Progress        : {status.completed_tasks}/{status.total_tasks} ({status.overall_progress_pct}%)")
    print(f"Ready to dispatch: {status.ready_tasks}")
    print(f"SLA risk        : {status.sla_risk}")
    print(
        f"Critical path   : {' -> '.join(status.critical_path.path)} "
        f"({status.critical_path.total_remaining_hours}h remaining)"
    )
    if status.critical_path.bottleneck_task_id:
        print(f"Bottleneck      : {status.critical_path.bottleneck_task_id}")
    for b in status.blocked_tasks:
        print(f"  BLOCKED {b.task_id} ({b.name}): {b.reason}")
        print(f"    Estimated delay : {b.estimated_delay_hours}h")
        print(f"    Downstream impact: {b.downstream_impact}")
    print(f"\nNarrative:\n{status.narrative}")


def main() -> None:
    # ------------------------------------------------------------------
    # Scenario 1 -- clean close, nothing blocked
    # ------------------------------------------------------------------
    clean_completed = {f"T{n}" for n in range(1, 15)}
    clean_tasks = _build_tasks(clean_completed)
    clean_status = run(PERIOD, clean_tasks)
    _print_status("Scenario 1 -- Clean Close", clean_status)

    # ------------------------------------------------------------------
    # Scenario 2 -- IC out-of-balance investigation (T7) blocked,
    # gating the entire consolidation/reporting chain
    # ------------------------------------------------------------------
    blocked_completed = {"T1", "T2", "T3", "T4", "T5", "T6", "T8", "T9", "T10", "T11", "T12", "T13", "T14"}
    blocked_reasons = {
        "T7": (
            "Intercompany discrepancy of $18,750 between US and UK entities is unresolved -- "
            "awaiting bank confirmation from UK treasury."
        )
    }
    blocked_tasks_list = _build_tasks(blocked_completed, blocked_reasons)
    blocked_status = run(PERIOD, blocked_tasks_list)
    _print_status("Scenario 2 -- Blocked: IC Out-of-Balance Investigation", blocked_status)

    # ------------------------------------------------------------------
    # Resolve the blocker and re-run to show the critical path re-derived
    # ------------------------------------------------------------------
    resolved_completed = blocked_completed | {"T7"}
    resolved_tasks_list = _build_tasks(resolved_completed)
    resolved_status = run(PERIOD, resolved_tasks_list)
    _print_status("Scenario 2 (resolved) -- IC Investigation Cleared", resolved_status)


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set -- copy .env.example to .env")
    main()
