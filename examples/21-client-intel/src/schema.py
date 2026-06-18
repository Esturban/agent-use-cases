from typing import Literal

from pydantic import BaseModel, Field


class FundingEvent(BaseModel):
    round_type: str = Field(description="Funding round type, e.g. Series B, debt facility.")
    amount_usd_m: float = Field(description="Amount raised in USD millions.")
    date: str = Field(description="Approximate date, e.g. Q2 2024.")
    lead_investor: str = Field(description="Lead investor name, or 'undisclosed'.")


class LeadershipChange(BaseModel):
    role: str = Field(description="Job title affected, e.g. CFO, CTO.")
    change_type: Literal["hire", "departure", "promotion"] = Field(
        description="Nature of the leadership change."
    )
    name: str = Field(description="Person's name, or 'undisclosed'.")
    date: str = Field(description="Approximate date.")


class RegulatoryExposure(BaseModel):
    topic: str = Field(description="Regulatory area, e.g. GDPR, antitrust, emissions.")
    severity: Literal["low", "medium", "high"] = Field(
        description="Estimated business impact severity."
    )
    summary: str = Field(description="One-sentence description of the exposure.")


class StrategicSignal(BaseModel):
    signal: str = Field(
        description="Plain-English description of a strategic move or intent signal."
    )
    implication: str = Field(
        description="Why this matters for relationship or opportunity planning."
    )


class ClientIntelBrief(BaseModel):
    company: str = Field(description="Company name.")
    funding_events: list[FundingEvent] = Field(
        description="Recent funding rounds or capital events."
    )
    leadership_changes: list[LeadershipChange] = Field(
        description="Recent C-suite or senior leadership changes."
    )
    regulatory_exposures: list[RegulatoryExposure] = Field(
        description="Material regulatory risks or obligations."
    )
    strategic_signals: list[StrategicSignal] = Field(
        description="Strategic moves, partnerships, or stated priorities."
    )
    relationship_actions: list[str] = Field(
        description="Concrete recommended next steps for the account team, highest priority first."
    )
