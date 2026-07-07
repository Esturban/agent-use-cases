"""Typed schemas for the security operations supervisor.

ProposedAction / ApprovalDecision / ActionResult are copied and adapted from
the approval-gate pattern (id 90) per this repo's replication convention --
every example that gates on a human decision reuses this shape rather than
importing across example folders, so each example stays independently
deployable.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AuthEvent(BaseModel):
    identity: str = Field(description="User or service account identity, e.g. 'svc-backup-01' or 'jdoe'")
    event_type: str = Field(
        description="SIEM event category, e.g. 'admin_login', 'impossible_travel', 'off_hours_login'"
    )
    detail: str = Field(description="Human-readable detail: source IP/location and timestamp")
    flagged: bool = Field(description="True if the SIEM flagged this event as anomalous")


class CVEDelta(BaseModel):
    package: str = Field(description="Affected package or dependency name")
    cve_id: str = Field(description="CVE identifier, e.g. 'CVE-2026-1234'")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="CVSS-derived severity tier"
    )
    actively_exploited: bool = Field(
        description="True if this CVE has a known active-exploitation indicator"
    )


class IAMChange(BaseModel):
    identity: str = Field(description="Identity affected by the access change")
    change_type: Literal["new_admin_grant", "orphaned_account"] = Field(
        description="Category of privilege-escalation signal"
    )
    role: str = Field(description="The role or privilege involved in the change")
    detail: str = Field(
        description="e.g. days since last login for an orphaned account, or the change-ticket "
        "reference for a new grant (empty string if none on file)"
    )


class IncidentTicket(BaseModel):
    ticket_id: str = Field(description="Open incident ticket identifier")
    description: str = Field(description="Free-text description of the incident")
    severity: Literal["low", "medium", "high", "critical"] = Field(description="Incident severity")
    status: str = Field(description="Current ticket status, e.g. 'open', 'contained'")


class SecuritySignalDigest(BaseModel):
    auth_events: list[AuthEvent] = Field(
        default_factory=list, description="SIEM-style auth events for the day"
    )
    cve_deltas: list[CVEDelta] = Field(
        default_factory=list, description="New or changed CVEs from the dependency scan"
    )
    iam_changes: list[IAMChange] = Field(
        default_factory=list, description="Privilege changes since the prior IAM snapshot"
    )
    open_incident: Optional[IncidentTicket] = Field(
        default=None, description="An open incident ticket, if any exist today"
    )


class SecurityFindingReport(BaseModel):
    domain: Literal[
        "threat_triage",
        "access_governance",
        "vulnerability_remediation",
        "incident_commander",
        "compliance_evidence",
    ] = Field(description="Which specialist subagent produced this report")
    severity: Literal["P0", "P1", "P2", "P3"] = Field(
        description="Priority tier -- P0 is highest, demands immediate action"
    )
    summary: str = Field(description="One or two sentence summary of the finding")
    recommended_action: str = Field(description="The concrete action recommended to resolve the finding")
    requires_approval: bool = Field(
        description="True if severity is P0/P1 and the recommendation must clear the approval "
        "gate before it is treated as actionable rather than merely advisory"
    )


class SecurityPostureBrief(BaseModel):
    dispatched_domains: list[str] = Field(
        description="Which domains had active signal in the digest and were dispatched"
    )
    findings: list[SecurityFindingReport] = Field(description="Typed reports from every dispatched subagent")
    cross_domain_correlations: list[str] = Field(
        default_factory=list,
        description="Patterns spanning more than one domain, e.g. the same identity appearing in "
        "both an anomalous-login finding and an orphaned-account finding",
    )
    overall_posture: Literal["green", "amber", "red"] = Field(
        description="Aggregate posture -- red if any P0 finding is open, amber if only P1/P2, "
        "green otherwise"
    )


class ProposedAction(BaseModel):
    action_type: Literal["revoke_access", "apply_patch", "send_notice"] = Field(
        description="The category of irreversible action being proposed"
    )
    summary: str = Field(description="One-sentence human-readable summary of what this action does")
    payload: dict = Field(
        description="Action-specific parameters a downstream system would need to execute the action"
    )
    risk_level: Literal["low", "medium", "high"] = Field(
        description="Risk tier used to decide whether the gate is mandatory or advisory"
    )


class ApprovalDecision(BaseModel):
    decision: Literal["approve", "edit", "reject"] = Field(
        description="The human reviewer's resolution of the proposed action"
    )
    edited_payload: Optional[dict] = Field(
        default=None, description="Replacement payload when decision='edit'; ignored otherwise"
    )
    rationale: str = Field(description="The human's reason for the decision -- always logged")


class ActionResult(BaseModel):
    executed: bool = Field(description="True only if the action actually fired")
    final_payload: Optional[dict] = Field(
        default=None, description="The payload that was actually executed, after any human edit"
    )
    decision_log: str = Field(description="Audit-trail entry: what was proposed, decided, and why")
