"""
Pydantic models for the month-end close orchestrator.

CloseTask is the atomic unit of work in the close cycle DAG -- it carries its
own dependency list (depends_on) so the orchestrator can compute readiness
and critical path without a separate adjacency structure. BlockedTaskInfo and
CriticalPathInfo are the two derived-state objects the orchestrator recomputes
after every status change. CloseStatus is the live aggregate object returned
to the caller: overall progress, SLA risk, and the current critical path.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

CloseTaskStatus = Literal["pending", "in_progress", "blocked", "completed", "exception"]

CloseTaskCategory = Literal[
    "subledger_close",
    "intercompany_elimination",
    "accruals_posting",
    "fx_revaluation",
    "consolidation",
    "reporting",
]

SLARisk = Literal["on_track", "at_risk", "critical"]


class CloseTask(BaseModel):
    task_id: str = Field(description="Unique identifier for this close task, e.g. 'T15'.")
    name: str = Field(description="Human-readable task name.")
    category: CloseTaskCategory = Field(description="Which stage of the close this task belongs to.")
    owner: str = Field(description="Team or role responsible for executing this task.")
    depends_on: list[str] = Field(
        default_factory=list,
        description="task_id values that must reach status='completed' before this task can start.",
    )
    sla_hours: float = Field(
        description="Hours this task is budgeted to take once it starts.", gt=0
    )
    status: CloseTaskStatus = Field(description="Current status of this task.")
    blocked_reason: Optional[str] = Field(
        default=None,
        description="Why this task is blocked or in exception. Required when status is 'blocked' or 'exception'.",
    )


class BlockedTaskInfo(BaseModel):
    task_id: str = Field(description="task_id of the blocked or exception task.")
    name: str = Field(description="Human-readable task name, for display without a second lookup.")
    reason: str = Field(description="Why the task cannot proceed.")
    estimated_delay_hours: float = Field(
        description="Estimated hours the close will slip if this task is not unblocked, ge=0."
    )
    downstream_impact: list[str] = Field(
        default_factory=list,
        description="task_id values of not-yet-completed tasks that transitively depend on this task.",
    )


class CriticalPathInfo(BaseModel):
    path: list[str] = Field(
        default_factory=list,
        description="task_id values in order, the longest remaining chain of incomplete work to close.",
    )
    total_remaining_hours: float = Field(
        description="Sum of sla_hours across every task on the critical path, ge=0."
    )
    bottleneck_task_id: Optional[str] = Field(
        default=None,
        description=(
            "task_id of the blocked or exception task sitting on the critical path, if any. "
            "None means the critical path is not currently obstructed."
        ),
    )


class CloseStatus(BaseModel):
    period: str = Field(description="Close period this status applies to, e.g. '2026-06'.")
    total_tasks: int = Field(description="Total number of tasks in the close task list.")
    completed_tasks: int = Field(description="Number of tasks with status='completed'.")
    overall_progress_pct: float = Field(
        description="completed_tasks / total_tasks as a percentage, 0-100.", ge=0.0, le=100.0
    )
    ready_tasks: list[str] = Field(
        default_factory=list,
        description="task_id values that are pending with all dependencies completed -- next to dispatch.",
    )
    blocked_tasks: list[BlockedTaskInfo] = Field(
        default_factory=list, description="Every task currently blocked or in exception."
    )
    critical_path: CriticalPathInfo = Field(
        description="The current longest remaining chain of incomplete work, re-derived on every call."
    )
    sla_risk: SLARisk = Field(
        description=(
            "'critical' if a blocked/exception task sits on the critical path, 'at_risk' if any "
            "task is blocked but off the critical path, otherwise 'on_track'."
        )
    )
    narrative: Optional[str] = Field(
        default=None,
        description="Executive narrative summarizing progress, SLA risk, and recommended action.",
    )
