"""LangGraph supervisor for the security operations pattern.

Graph: dispatch_domains -> [human_review -> resolve_gate] -> synthesize.

dispatch_domains conditionally calls only the domain subagents whose slice of
the digest has active signal, collecting typed SecurityFindingReport objects.
If any finding has requires_approval=True, the graph routes through
human_review -- a genuine interrupt()/Command(resume=...) gate copied from
the approval-gate pattern (id 90) -- before synthesize runs. A finding stays
advisory-only until it clears that gate; nothing here auto-executes.

Public API mirrors id 90: propose() runs to completion or to the interrupt;
resume() takes the paused thread_id plus a human ApprovalDecision and
finishes the graph.
"""

from __future__ import annotations

import uuid
from typing import Literal, Optional, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .agents import (
    access_governance_agent,
    compliance_evidence_agent,
    incident_commander_agent,
    threat_triage_agent,
    vulnerability_remediation_agent,
)
from .schema import (
    ActionResult,
    ApprovalDecision,
    ProposedAction,
    SecurityFindingReport,
    SecuritySignalDigest,
    SecurityPostureBrief,
)

_MODEL = "gpt-4.1-nano"

_ACTION_TYPE_BY_DOMAIN = {
    "threat_triage": "revoke_access",
    "access_governance": "revoke_access",
    "vulnerability_remediation": "apply_patch",
    "incident_commander": "send_notice",
    "compliance_evidence": "send_notice",
}

_SEVERITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


class GraphState(TypedDict):
    digest: dict
    dispatched_domains: list[str]
    findings: list[dict]
    gated_finding: Optional[dict]
    decision: Optional[dict]
    gate_result: Optional[dict]
    brief: Optional[dict]


def _detect_correlations(digest: SecuritySignalDigest) -> list[str]:
    """Deterministic cross-reference -- no LLM. Flags identities that show up in
    more than one domain's signal (e.g. an orphaned account behind a flagged login).
    """
    orphaned = {c.identity for c in digest.iam_changes if c.change_type == "orphaned_account"}
    flagged = {e.identity for e in digest.auth_events if e.flagged}
    overlap = orphaned & flagged
    return [
        f"Identity '{identity}' is both an orphaned-but-privileged account and the actor in a "
        "flagged anomalous auth event -- investigate as one incident, not two."
        for identity in sorted(overlap)
    ]


def _dispatch_domains(state: GraphState) -> dict:
    digest = SecuritySignalDigest.model_validate(state["digest"])
    llm = ChatOpenAI(model=_MODEL, temperature=0)
    dispatched: list[str] = []
    findings: list[SecurityFindingReport] = []

    if any(e.flagged for e in digest.auth_events):
        dispatched.append("threat_triage")
        findings.append(threat_triage_agent(llm, digest.auth_events))

    if digest.iam_changes:
        dispatched.append("access_governance")
        findings.append(access_governance_agent(llm, digest.iam_changes))

    if digest.cve_deltas:
        dispatched.append("vulnerability_remediation")
        findings.append(vulnerability_remediation_agent(llm, digest.cve_deltas))

    if digest.open_incident is not None:
        dispatched.append("incident_commander")
        findings.append(incident_commander_agent(llm, digest.open_incident))

    if findings:
        dispatched.append("compliance_evidence")
        findings.append(compliance_evidence_agent(llm, findings))

    return {
        "dispatched_domains": dispatched,
        "findings": [f.model_dump() for f in findings],
    }


def _route_after_dispatch(state: GraphState) -> Literal["human_review", "synthesize"]:
    findings = [SecurityFindingReport.model_validate(f) for f in state["findings"]]
    return "human_review" if any(f.requires_approval for f in findings) else "synthesize"


def _human_review(state: GraphState) -> dict:
    """Halt the graph and surface the single most material gated finding."""
    findings = [SecurityFindingReport.model_validate(f) for f in state["findings"]]
    gated = sorted(
        (f for f in findings if f.requires_approval),
        key=lambda f: _SEVERITY_RANK.get(f.severity, 9),
    )
    top = gated[0]
    proposed = ProposedAction(
        action_type=_ACTION_TYPE_BY_DOMAIN.get(top.domain, "send_notice"),
        summary=top.recommended_action,
        payload={"domain": top.domain, "severity": top.severity, "summary": top.summary},
        risk_level="high" if top.severity == "P0" else "medium",
    )
    decision = interrupt({"proposed_action": proposed.model_dump(), "finding": top.model_dump()})
    return {"decision": decision, "gated_finding": top.model_dump()}


def _resolve_gate(state: GraphState) -> dict:
    top = SecurityFindingReport.model_validate(state["gated_finding"])
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
            else {"domain": top.domain, "severity": top.severity, "summary": top.summary}
        )
        verb = "EDITED-THEN-EXECUTED" if decision.decision == "edit" else "EXECUTED"
        result = ActionResult(
            executed=True,
            final_payload=payload,
            decision_log=f"{verb}: {top.recommended_action!r}. Reason: {decision.rationale}",
        )
    return {"gate_result": result.model_dump()}


def _synthesize(state: GraphState) -> dict:
    digest = SecuritySignalDigest.model_validate(state["digest"])
    findings = [SecurityFindingReport.model_validate(f) for f in state["findings"]]
    correlations = _detect_correlations(digest)

    if any(f.severity == "P0" for f in findings):
        posture: Literal["green", "amber", "red"] = "red"
    elif any(f.severity in ("P1", "P2") for f in findings):
        posture = "amber"
    else:
        posture = "green"

    brief = SecurityPostureBrief(
        dispatched_domains=state["dispatched_domains"],
        findings=findings,
        cross_domain_correlations=correlations,
        overall_posture=posture,
    )
    return {"brief": brief.model_dump()}


def _build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("dispatch_domains", _dispatch_domains)
    graph.add_node("human_review", _human_review)
    graph.add_node("resolve_gate", _resolve_gate)
    graph.add_node("synthesize", _synthesize)
    graph.add_edge(START, "dispatch_domains")
    graph.add_conditional_edges(
        "dispatch_domains",
        _route_after_dispatch,
        {"human_review": "human_review", "synthesize": "synthesize"},
    )
    graph.add_edge("human_review", "resolve_gate")
    graph.add_edge("resolve_gate", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile(checkpointer=InMemorySaver())


_APP = _build_graph()


def propose(digest: SecuritySignalDigest) -> dict:
    """Run the graph. Returns a dict with status='complete' and a brief, or
    status='paused' with a proposed_action/finding/thread_id awaiting resume().
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    result = _APP.invoke({"digest": digest.model_dump()}, config=config)

    if "__interrupt__" in result:
        value = result["__interrupt__"][0].value
        return {
            "status": "paused",
            "proposed_action": ProposedAction.model_validate(value["proposed_action"]),
            "finding": SecurityFindingReport.model_validate(value["finding"]),
            "thread_id": thread_id,
        }
    return {"status": "complete", "brief": SecurityPostureBrief.model_validate(result["brief"])}


def resume(thread_id: str, decision: ApprovalDecision) -> dict:
    """Resume a paused run with a human's ApprovalDecision. Returns the final
    brief plus the ActionResult of the gated recommendation.
    """
    config = {"configurable": {"thread_id": thread_id}}
    result = _APP.invoke(Command(resume=decision.model_dump()), config=config)
    return {
        "brief": SecurityPostureBrief.model_validate(result["brief"]),
        "gate_result": ActionResult.model_validate(result["gate_result"]),
    }
