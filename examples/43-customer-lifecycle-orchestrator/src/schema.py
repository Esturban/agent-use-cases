"""
Pydantic models for the customer lifecycle orchestrator.

Covers the five lifecycle stages, incoming customer signals, the typed
CustomerRecord that accumulates state across invocations, per-stage
specialist outputs, and the top-level OrchestratorResult returned by run().
"""
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Stage & signal enumerations
# ---------------------------------------------------------------------------

LifecycleStage = Literal["lead", "onboarding", "healthy", "at_risk", "renewal"]


class CustomerSignal(BaseModel):
    signal_type: Literal[
        "form_submit",
        "support_ticket",
        "nps_score",
        "login_activity",
        "contract_expiry",
        "churn_indicator",
        "upsell_interest",
    ] = Field(description="Category of the incoming signal.")
    value: str = Field(description="Signal payload as a string (e.g. NPS score, ticket ID, activity count).")
    timestamp: str = Field(description="ISO-8601 timestamp when the signal was recorded.")


# ---------------------------------------------------------------------------
# Core customer record
# ---------------------------------------------------------------------------


class CustomerRecord(BaseModel):
    customer_id: str = Field(description="Unique identifier for the customer account.")
    company_name: str = Field(description="Name of the customer's company.")
    stage: LifecycleStage = Field(description="Current lifecycle stage of the account.")
    health_score: float = Field(
        description="Composite health score between 0.0 (critical) and 1.0 (excellent).",
        ge=0.0,
        le=1.0,
    )
    arr_usd: float = Field(description="Annual recurring revenue in USD.")
    days_since_last_active: int = Field(
        description="Number of days since the account last logged in or used the product."
    )
    open_tickets: int = Field(description="Number of open support tickets for this account.")
    nps_score: int | None = Field(
        default=None, description="Most recent NPS score (0-10), or None if not yet collected."
    )
    notes: list[str] = Field(
        description="Chronological notes from agents or CSMs appended over the account lifetime."
    )
    signals: list[CustomerSignal] = Field(
        description="All signals received for this account in chronological order."
    )


# ---------------------------------------------------------------------------
# Per-stage specialist outputs
# ---------------------------------------------------------------------------


class QualificationResult(BaseModel):
    qualified: bool = Field(
        description="True if the lead meets the ICP threshold and should proceed to onboarding."
    )
    icp_score: float = Field(
        description="ICP fit score between 0.0 (poor fit) and 1.0 (perfect fit).",
        ge=0.0,
        le=1.0,
    )
    reasoning: str = Field(description="One to two sentence explanation of the qualification decision.")
    recommended_next_step: str = Field(
        description="Specific recommended action for the sales or CS team."
    )


class OnboardingStatus(BaseModel):
    tasks_complete: list[str] = Field(
        description="Onboarding tasks already completed or confirmed by the customer."
    )
    tasks_pending: list[str] = Field(description="Onboarding tasks still outstanding.")
    day1_ready: bool = Field(
        description="True if the customer has all prerequisites in place for a successful go-live."
    )
    blockers: list[str] = Field(description="Issues preventing forward progress in onboarding.")


class HealthAssessment(BaseModel):
    health_score: float = Field(
        description="Updated health score between 0.0 and 1.0 based on the latest signals.",
        ge=0.0,
        le=1.0,
    )
    risk_factors: list[str] = Field(
        description="Signals or patterns that are dragging health down."
    )
    positive_signals: list[str] = Field(
        description="Signals or patterns that are supporting a healthy account."
    )
    recommended_action: str = Field(
        description="Specific next action for the CSM or account team."
    )


class ChurnResponse(BaseModel):
    segment: Literal["escalate", "retain", "neutral"] = Field(
        description=(
            "'escalate' for accounts with active churn intent; "
            "'retain' for recoverable at-risk accounts; "
            "'neutral' for ambiguous signals."
        )
    )
    follow_up_draft: str = Field(
        description="Draft outreach message tailored to the segment and account context."
    )
    urgency: Literal["immediate", "this_week", "low"] = Field(
        description="Recommended response urgency for the account team."
    )


class RenewalPackage(BaseModel):
    renewal_probability: float = Field(
        description="Estimated probability (0.0-1.0) that the customer will renew.",
        ge=0.0,
        le=1.0,
    )
    negotiation_levers: list[str] = Field(
        description="Levers available to the CS or sales team to improve renewal odds."
    )
    outreach_draft: str = Field(
        description="Draft renewal outreach email or call script."
    )
    recommended_discount_pct: float = Field(
        description="Recommended discount percentage to offer (0.0 if none recommended).",
        ge=0.0,
        le=100.0,
    )


# ---------------------------------------------------------------------------
# Stage transition & orchestrator envelope
# ---------------------------------------------------------------------------


class StageOutput(BaseModel):
    stage_handled: LifecycleStage = Field(
        description="The stage whose specialist agent produced this output."
    )
    output: dict = Field(description="Raw dict of the specialist agent's structured response.")
    next_stage: LifecycleStage | None = Field(
        default=None,
        description="Stage to transition to, or None if the account remains in the current stage.",
    )
    updated_record: CustomerRecord = Field(
        description="CustomerRecord after applying this stage's updates."
    )


class OrchestratorResult(BaseModel):
    customer_id: str = Field(
        description="Unique identifier of the customer account that was processed."
    )
    previous_stage: LifecycleStage = Field(
        description="Lifecycle stage the account was in before this invocation."
    )
    stage_output: StageOutput = Field(
        description="Output from the specialist agent for the stage that was handled."
    )
    transition_occurred: bool = Field(
        description="True if the orchestrator moved the account to a new lifecycle stage."
    )
