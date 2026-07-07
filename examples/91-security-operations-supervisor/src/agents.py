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


def _run(llm: ChatOpenAI, system, payload, domain: str) -> SecurityFindingReport:
    """Force `domain` deterministically rather than trusting the model to echo it
    back correctly -- observed in practice that compliance_evidence, given a
    payload full of other domains' labels, sometimes copies one of those instead
    of setting its own.
    """
    structured = llm.with_structured_output(SecurityFindingReport, method="function_calling")
    result = structured.invoke([system, ("human", json.dumps(payload))])
    return result.model_copy(update={"domain": domain})


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
    )
