"""Domain subagent factory functions -- each takes the LLM plus its slice of the
daily signal digest and returns a typed SecurityFindingReport.
"""

import json

from langchain_openai import ChatOpenAI

from .prompts import (
    ACCESS_GOVERNANCE_SYSTEM,
    COMPLIANCE_EVIDENCE_SYSTEM,
    INCIDENT_COMMANDER_SYSTEM,
    THREAT_TRIAGE_SYSTEM,
    VULNERABILITY_REMEDIATION_SYSTEM,
)
from .schema import (
    AuthEvent,
    CVEDelta,
    IAMChange,
    IncidentTicket,
    SecurityFindingReport,
)


def _run(
    llm: ChatOpenAI, system, payload, domain: str, always_advisory: bool = False
) -> SecurityFindingReport:
    """Force `domain` and `requires_approval` deterministically rather than
    trusting the model to set them -- both are fully determined by information
    already known at the call site (which agent this is, and what severity it
    assigned), so there is nothing for the model to correctly infer. Observed
    in practice: the model sometimes echoes a different domain's label back
    (e.g. compliance_evidence copying "access_governance" from its input), and
    separately does not reliably follow a "requires_approval=true only for
    P0/P1" instruction -- for compliance_evidence this could wrongly trigger
    the gate on a quiet day, and for the other four domains it could just as
    easily suppress a genuine P0 and let a revoke_access/apply_patch
    recommendation skip the gate entirely, which is the exact failure the gate
    exists to prevent.
    """
    structured = llm.with_structured_output(SecurityFindingReport, method="function_calling")
    result = structured.invoke([system, ("human", json.dumps(payload))])
    requires_approval = False if always_advisory else result.severity in ("P0", "P1")
    return result.model_copy(update={"domain": domain, "requires_approval": requires_approval})


def threat_triage_agent(llm: ChatOpenAI, auth_events: list[AuthEvent]) -> SecurityFindingReport:
    payload = [e.model_dump() for e in auth_events if e.flagged]
    return _run(llm, THREAT_TRIAGE_SYSTEM, payload, domain="threat_triage")


def access_governance_agent(llm: ChatOpenAI, iam_changes: list[IAMChange]) -> SecurityFindingReport:
    return _run(
        llm, ACCESS_GOVERNANCE_SYSTEM, [c.model_dump() for c in iam_changes], domain="access_governance"
    )


def vulnerability_remediation_agent(
    llm: ChatOpenAI, cve_deltas: list[CVEDelta]
) -> SecurityFindingReport:
    return _run(
        llm,
        VULNERABILITY_REMEDIATION_SYSTEM,
        [d.model_dump() for d in cve_deltas],
        domain="vulnerability_remediation",
    )


def incident_commander_agent(llm: ChatOpenAI, incident: IncidentTicket) -> SecurityFindingReport:
    return _run(llm, INCIDENT_COMMANDER_SYSTEM, incident.model_dump(), domain="incident_commander")


def compliance_evidence_agent(
    llm: ChatOpenAI, findings: list[SecurityFindingReport]
) -> SecurityFindingReport:
    return _run(
        llm,
        COMPLIANCE_EVIDENCE_SYSTEM,
        [f.model_dump() for f in findings],
        domain="compliance_evidence",
        always_advisory=True,
    )
