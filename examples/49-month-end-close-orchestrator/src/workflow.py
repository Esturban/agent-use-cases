"""DAG-ordered task orchestration for the month-end close.

Graph: compute_status -> synthesize.

compute_status is pure deterministic graph math (dag.py): it derives which
tasks are ready to dispatch, which are blocked with a reason and estimated
delay, and the current critical path -- re-derived fresh on every call from
whatever CloseTask statuses are passed in, never carried over from a
previous run. synthesize is the one LLM call, turning that typed snapshot
into an executive narrative.
"""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .agents import close_narrative_synthesizer
from .dag import compute_blocked_tasks, compute_critical_path, compute_ready_tasks
from .schema import CloseStatus, CloseTask


class GraphState(TypedDict):
    period: str
    tasks: list[dict]
    status: dict


def _compute_status(state: GraphState) -> dict:
    tasks = [CloseTask.model_validate(t) for t in state["tasks"]]

    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "completed")
    overall_progress_pct = round((completed_tasks / total_tasks) * 100, 2) if total_tasks else 0.0

    ready_tasks = compute_ready_tasks(tasks)
    blocked_tasks = compute_blocked_tasks(tasks)
    critical_path = compute_critical_path(tasks)

    if critical_path.bottleneck_task_id is not None:
        sla_risk = "critical"
    elif blocked_tasks:
        sla_risk = "at_risk"
    else:
        sla_risk = "on_track"

    status = CloseStatus(
        period=state["period"],
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        overall_progress_pct=overall_progress_pct,
        ready_tasks=ready_tasks,
        blocked_tasks=blocked_tasks,
        critical_path=critical_path,
        sla_risk=sla_risk,
        narrative=None,
    )
    return {"status": status.model_dump()}


def _synthesize(state: GraphState) -> dict:
    narrative = close_narrative_synthesizer(state["status"])
    status = dict(state["status"])
    status["narrative"] = narrative
    return {"status": status}


def _build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("compute_status", _compute_status)
    graph.add_node("synthesize", _synthesize)
    graph.add_edge(START, "compute_status")
    graph.add_edge("compute_status", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile()


_APP = _build_graph()


def run(period: str, tasks: list[CloseTask]) -> CloseStatus:
    """Run one orchestration pass over the current task list and return a live CloseStatus.

    Call again with an updated task list (e.g. after a blocker resolves) to
    re-derive readiness and critical path from scratch.
    """
    result = _APP.invoke({"period": period, "tasks": [t.model_dump() for t in tasks]})
    return CloseStatus.model_validate(result["status"])
