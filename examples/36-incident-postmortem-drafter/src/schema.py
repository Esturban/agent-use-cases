from typing import Literal

from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    timestamp: str = Field(description="Event timestamp in ISO-8601 format.")
    event: str = Field(description="Description of what happened at this timestamp.")
    severity: Literal["info", "warning", "critical"] = Field(
        description="Severity classification of this event."
    )
    component: str = Field(description="System component or service affected.")


class IncidentTimeline(BaseModel):
    incident_id: str = Field(description="Unique incident identifier (e.g. INC-2026-001).")
    title: str = Field(description="Short incident title.")
    start_time: str = Field(description="Incident start time in ISO-8601 format.")
    end_time: str = Field(description="Incident resolution time in ISO-8601 format.")
    duration_minutes: int = Field(description="Total incident duration in minutes.")
    events: list[TimelineEvent] = Field(description="Chronological list of incident events.")
    affected_services: list[str] = Field(description="List of services impacted by the incident.")


class Postmortem(BaseModel):
    incident_id: str = Field(description="Unique incident identifier.")
    title: str = Field(description="Short incident title.")
    timeline: IncidentTimeline = Field(description="Parsed incident timeline.")
    root_cause: str = Field(description="Primary root cause of the incident.")
    contributing_factors: list[str] = Field(
        description="Secondary factors that contributed to or amplified the incident."
    )
    impact_summary: str = Field(
        description="2-3 sentence summary of customer and business impact."
    )
    action_items: list[str] = Field(
        description="Specific, actionable remediation steps with owners and deadlines where possible."
    )
    detection_improvements: list[str] = Field(
        description="Specific improvements to monitoring or alerting to detect this class of incident faster."
    )
    executive_summary: str = Field(
        description="1-2 paragraph executive summary suitable for leadership communication."
    )
