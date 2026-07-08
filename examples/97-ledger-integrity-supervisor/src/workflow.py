"""LangGraph supervisor for the period-close controls cycle.

Graph: run_checks -> [human_review -> resolve_gate] -> synthesize.

run_checks always runs all five domain checks (unlike id 91's conditional
dispatch -- period-close controls run every cycle regardless of signal, they
don't get skipped). Any exception whose financial_exposure crosses the
materiality threshold routes through human_review, a real interrupt()/
Command(resume=...) gate copied from id 90, before the close can be marked
anything but blocked. synthesize calls the one LLM step in this example --
the audit-trail narrative -- after the gate resolves.
"""

from __future__ import annotations

import uuid
from typing import Literal, Optional, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .agents import audit_trail_synthesizer
from .checks import (
    check_bank_reconciliation,
    check_fixed_assets,
    check_fraud_signals,
    check_jv_postings,
    check_segregation_of_duties,
)
from .schema import (
    ActionResult,
    ApprovalDecision,
    BankTransaction,
    ControlException,
    ControlsExceptionRegister,
    FixedAsset,
    GLCashEntry,
    JournalEntry,
    PaymentTransaction,
    ProposedAction,
    SoDRoleGrant,
)

_ACTION_TYPE_BY_DOMAIN = {
    "jv_posting": "reverse_entry",
    "bank_reconciliation": "escalate_to_investigations",
    "fixed_asset": "adjust_book_value",
    "fraud_screening": "escalate_to_investigations",
    "segregation_of_duties": "escalate_to_investigations",
}


class CloseCycleData(TypedDict):
    period: str
    materiality_threshold: float
    journal_entries: list[dict]
    bank_transactions: list[dict]
    gl_entries: list[dict]
    fixed_assets: list[dict]
    payment_transactions: list[dict]
    sod_role_grants: list[dict]


class GraphState(TypedDict):
    close_data: dict
    exceptions: list[dict]
    correlations: list[str]
    gated_exception: Optional[dict]
    decision: Optional[dict]
    gate_result: Optional[dict]
    register: Optional[dict]


def _detect_correlations(exceptions: list[ControlException]) -> list[str]:
    """Deterministic cross-reference -- no LLM. Flags any entity (identity,
    vendor, account) appearing in exceptions from 2+ distinct domains.
    """
    entity_domains: dict[str, set[str]] = {}
    for exc in exceptions:
        for entity in exc.entities_involved:
            entity_domains.setdefault(entity, set()).add(exc.domain)

    correlations = []
    for entity, domains in sorted(entity_domains.items()):
        if len(domains) >= 2:
            correlations.append(
                f"{entity!r} appears in exceptions from {len(domains)} domains "
                f"({', '.join(sorted(domains))}) -- investigate as one connected issue, "
                "not separate findings."
            )
    return correlations


def _run_checks(state: GraphState) -> dict:
    data = CloseCycleData(**state["close_data"])
    materiality = data["materiality_threshold"]

    journal_entries = [JournalEntry.model_validate(e) for e in data["journal_entries"]]
    bank_txns = [BankTransaction.model_validate(t) for t in data["bank_transactions"]]
    gl_entries = [GLCashEntry.model_validate(g) for g in data["gl_entries"]]
    assets = [FixedAsset.model_validate(a) for a in data["fixed_assets"]]
    payments = [PaymentTransaction.model_validate(p) for p in data["payment_transactions"]]
    role_grants = [SoDRoleGrant.model_validate(r) for r in data["sod_role_grants"]]

    exceptions: list[ControlException] = []
    exceptions += check_jv_postings(journal_entries, materiality)
    exceptions += check_bank_reconciliation(bank_txns, gl_entries, materiality)
    exceptions += check_fixed_assets(assets)
    exceptions += check_fraud_signals(payments, materiality)
    exceptions += check_segregation_of_duties(journal_entries, role_grants)

    correlations = _detect_correlations(exceptions)

    return {
        "exceptions": [e.model_dump() for e in exceptions],
        "correlations": correlations,
    }


def _route_after_checks(state: GraphState) -> Literal["human_review", "synthesize"]:
    exceptions = [ControlException.model_validate(e) for e in state["exceptions"]]
    return "human_review" if any(e.requires_approval for e in exceptions) else "synthesize"


def _human_review(state: GraphState) -> dict:
    """Halt the graph and surface the single most material exception requiring approval."""
    exceptions = [ControlException.model_validate(e) for e in state["exceptions"]]
    gated = sorted(
        (e for e in exceptions if e.requires_approval),
        key=lambda e: e.financial_exposure,
        reverse=True,
    )
    top = gated[0]
    proposed = ProposedAction(
        action_type=_ACTION_TYPE_BY_DOMAIN.get(top.domain, "escalate_to_investigations"),
        summary=top.recommended_action,
        payload={
            "domain": top.domain,
            "severity": top.severity,
            "financial_exposure": top.financial_exposure,
            "description": top.description,
        },
        risk_level="high" if top.severity in ("critical", "high") else "medium",
    )
    decision = interrupt({"proposed_action": proposed.model_dump(), "exception": top.model_dump()})
    return {"decision": decision, "gated_exception": top.model_dump()}


def _resolve_gate(state: GraphState) -> dict:
    top = ControlException.model_validate(state["gated_exception"])
    decision = ApprovalDecision.model_validate(state["decision"])

    if decision.decision == "reject":
        result = ActionResult(
            executed=False,
            final_payload=None,
            decision_log=f"REJECTED: {top.recommended_action!r}. Reason: {decision.rationale}",
        )
    else:
        payload = (
            decision.edited_payload
            if decision.decision == "edit" and decision.edited_payload is not None
            else {"domain": top.domain, "financial_exposure": top.financial_exposure}
        )
        verb = "EDITED-THEN-EXECUTED" if decision.decision == "edit" else "EXECUTED"
        result = ActionResult(
            executed=True,
            final_payload=payload,
            decision_log=f"{verb}: {top.recommended_action!r}. Reason: {decision.rationale}",
        )
    return {"gate_result": result.model_dump()}


def _synthesize(state: GraphState) -> dict:
    exceptions = [ControlException.model_validate(e) for e in state["exceptions"]]
    gated_exception = (
        ControlException.model_validate(state["gated_exception"])
        if state.get("gated_exception")
        else None
    )
    gate_result = ActionResult.model_validate(state["gate_result"]) if state.get("gate_result") else None

    total_exposure = round(sum(e.financial_exposure for e in exceptions), 2)
    narrative = audit_trail_synthesizer(
        exceptions, gated_exception, gate_result, total_exposure, state["correlations"]
    )

    if not exceptions:
        close_status: Literal["blocked", "conditionally_closed", "closed"] = "closed"
    elif gate_result is not None and not gate_result.executed:
        close_status = "blocked"
    else:
        close_status = "conditionally_closed"

    register = ControlsExceptionRegister(
        period=state["close_data"]["period"],
        exceptions=exceptions,
        cross_domain_correlations=state["correlations"],
        total_exposure=total_exposure,
        close_status=close_status,
        audit_narrative=narrative,
    )
    return {"register": register.model_dump()}


def _build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("run_checks", _run_checks)
    graph.add_node("human_review", _human_review)
    graph.add_node("resolve_gate", _resolve_gate)
    graph.add_node("synthesize", _synthesize)
    graph.add_edge(START, "run_checks")
    graph.add_conditional_edges(
        "run_checks",
        _route_after_checks,
        {"human_review": "human_review", "synthesize": "synthesize"},
    )
    graph.add_edge("human_review", "resolve_gate")
    graph.add_edge("resolve_gate", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile(checkpointer=InMemorySaver())


_APP = _build_graph()


def propose(close_data: CloseCycleData) -> dict:
    """Run the graph. Returns status='complete' with a register, or
    status='paused' with a proposed_action/exception/thread_id awaiting resume().
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    result = _APP.invoke({"close_data": dict(close_data)}, config=config)

    if "__interrupt__" in result:
        value = result["__interrupt__"][0].value
        return {
            "status": "paused",
            "proposed_action": ProposedAction.model_validate(value["proposed_action"]),
            "exception": ControlException.model_validate(value["exception"]),
            "thread_id": thread_id,
        }
    return {
        "status": "complete",
        "register": ControlsExceptionRegister.model_validate(result["register"]),
    }


def resume(thread_id: str, decision: ApprovalDecision) -> dict:
    """Resume a paused run with a human controller's ApprovalDecision."""
    config = {"configurable": {"thread_id": thread_id}}
    result = _APP.invoke(Command(resume=decision.model_dump()), config=config)
    return {
        "register": ControlsExceptionRegister.model_validate(result["register"]),
        "gate_result": ActionResult.model_validate(result["gate_result"]),
    }
