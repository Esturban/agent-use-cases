"""
Deterministic DAG algorithms for the month-end close -- no LLM.

Every number the orchestrator reports (readiness, critical path, blocked-task
delay) is computed here in plain Python. The LLM in agents.py is only handed
the already-computed figures and asked to narrate them, never to re-derive
them -- the same "don't trust the model with arithmetic" convention used by
the deterministic checks in example 97.
"""

from .schema import BlockedTaskInfo, CloseTask, CriticalPathInfo


def topological_order(tasks: list[CloseTask]) -> list[str]:
    """Kahn's algorithm. Raises ValueError if the task list is not a DAG."""
    by_id = {t.task_id: t for t in tasks}
    in_degree = {t.task_id: 0 for t in tasks}
    children: dict[str, list[str]] = {t.task_id: [] for t in tasks}

    for task in tasks:
        for dep in task.depends_on:
            if dep not in by_id:
                raise ValueError(f"{task.task_id} depends on unknown task {dep!r}")
            children[dep].append(task.task_id)
            in_degree[task.task_id] += 1

    queue = sorted(task_id for task_id, deg in in_degree.items() if deg == 0)
    order: list[str] = []

    while queue:
        queue.sort()
        current = queue.pop(0)
        order.append(current)
        for child in children[current]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if len(order) != len(tasks):
        raise ValueError("Close task list contains a dependency cycle")

    return order


def compute_ready_tasks(tasks: list[CloseTask]) -> list[str]:
    """A task is ready to dispatch when it is pending and every dependency is completed."""
    by_id = {t.task_id: t for t in tasks}
    ready = []
    for task in tasks:
        if task.status != "pending":
            continue
        if all(by_id[dep].status == "completed" for dep in task.depends_on):
            ready.append(task.task_id)
    return sorted(ready)


def _descendants(task_id: str, children: dict[str, list[str]], by_id: dict[str, CloseTask]) -> list[str]:
    """Every not-yet-completed task reachable downstream of task_id."""
    seen: set[str] = set()
    stack = list(children.get(task_id, []))
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(children.get(node, []))
    return sorted(node for node in seen if by_id[node].status != "completed")


def compute_blocked_tasks(tasks: list[CloseTask]) -> list[BlockedTaskInfo]:
    """Surface every blocked/exception task with a reason and estimated delay.

    estimated_delay_hours is the task's own remaining sla_hours -- the close
    cannot finish faster than the blocked task's budgeted duration once it is
    unblocked. downstream_impact lists every incomplete task that transitively
    depends on it, so the caller sees the blast radius, not just the one task.
    """
    by_id = {t.task_id: t for t in tasks}
    children: dict[str, list[str]] = {t.task_id: [] for t in tasks}
    for task in tasks:
        for dep in task.depends_on:
            children[dep].append(task.task_id)

    blocked = []
    for task in tasks:
        if task.status not in ("blocked", "exception"):
            continue
        blocked.append(
            BlockedTaskInfo(
                task_id=task.task_id,
                name=task.name,
                reason=task.blocked_reason or "No reason recorded.",
                estimated_delay_hours=task.sla_hours,
                downstream_impact=_descendants(task.task_id, children, by_id),
            )
        )
    return sorted(blocked, key=lambda b: b.task_id)


def compute_critical_path(tasks: list[CloseTask]) -> CriticalPathInfo:
    """Longest remaining chain of incomplete work through the DAG.

    Duration of a completed task is 0 -- it no longer contributes to time
    remaining. dist[task_id] is the hours needed to finish that task counting
    from now, including everything upstream of it that is still incomplete.
    The critical path is the path ending at the task with the largest dist.
    """
    order = topological_order(tasks)
    by_id = {t.task_id: t for t in tasks}

    dist: dict[str, float] = {}
    prev: dict[str, str | None] = {}

    for task_id in order:
        task = by_id[task_id]

        if task.status == "completed":
            dist[task_id] = 0.0
            prev[task_id] = None
            continue

        best_dep_dist = 0.0
        best_dep: str | None = None
        for dep in task.depends_on:
            dep_dist = dist.get(dep, 0.0)
            if dep_dist >= best_dep_dist:
                best_dep_dist = dep_dist
                best_dep = dep

        dist[task_id] = task.sla_hours + best_dep_dist
        prev[task_id] = best_dep if best_dep_dist > 0 else None

    incomplete_ids = [t.task_id for t in tasks if t.status != "completed"]
    if not incomplete_ids:
        return CriticalPathInfo(path=[], total_remaining_hours=0.0, bottleneck_task_id=None)

    sink = max(incomplete_ids, key=lambda tid: dist[tid])

    path: list[str] = []
    node: str | None = sink
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()

    bottleneck = next(
        (tid for tid in path if by_id[tid].status in ("blocked", "exception")), None
    )

    return CriticalPathInfo(
        path=path,
        total_remaining_hours=round(dist[sink], 2),
        bottleneck_task_id=bottleneck,
    )
