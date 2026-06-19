"""Pydantic models for the regulatory change tracker."""

from typing import Literal

from pydantic import BaseModel, Field


class Obligation(BaseModel):
    """A single compliance obligation in the existing register."""

    id: str = Field(description="Unique identifier for the obligation (e.g. OBL-001).")
    text: str = Field(description="Full text of the obligation as written in the source regulation.")
    source_article: str = Field(
        description="Article or section reference in the regulation (e.g. 'Article 17(1)')."
    )
    category: str = Field(
        description="Obligation category (e.g. 'data-retention', 'consent', 'disclosure')."
    )
    effective_date: str = Field(
        description="ISO date from which the obligation is effective (e.g. '2024-01-01')."
    )
    status: Literal["active", "pending", "superseded"] = Field(
        description="Lifecycle status of the obligation."
    )


class ObligationRegister(BaseModel):
    """The existing set of tracked compliance obligations before the new update."""

    jurisdiction: str = Field(
        description="Jurisdiction covered by this register (e.g. 'EU', 'UK', 'US-CA')."
    )
    obligations: list[Obligation] = Field(
        description="All obligations currently tracked in the register."
    )


class RegulatoryUpdate(BaseModel):
    """A new regulatory update to be ingested and diffed against the register."""

    update_id: str = Field(
        description="Unique identifier for this regulatory update (e.g. 'GDPR-AMD-2024-03')."
    )
    title: str = Field(description="Human-readable title of the regulatory update.")
    effective_date: str = Field(
        description="ISO date from which the update takes effect (e.g. '2025-01-01')."
    )
    jurisdiction: str = Field(
        description="Jurisdiction the update applies to (e.g. 'EU', 'UK', 'US-CA')."
    )
    raw_text: str = Field(
        description="Full text of the regulatory update as received from the official source."
    )
    summary: str = Field(
        description="A 1-3 sentence plain-English summary of what has changed in this update."
    )


class NewObligation(BaseModel):
    """A net-new obligation extracted from the regulatory update — not yet in the register."""

    text: str = Field(
        description="Full text of the new obligation as extracted from the update."
    )
    source_article: str = Field(
        description="Article or section reference in the update that introduces this obligation."
    )
    category: str = Field(
        description="Obligation category (e.g. 'data-retention', 'breach-notification', 'audit')."
    )
    effective_date: str = Field(
        description="ISO date from which this obligation is effective."
    )


class ContractExposure(BaseModel):
    """Exposure assessment for a single contract against one new obligation."""

    contract_name: str = Field(
        description="Human-readable name or identifier of the assessed contract."
    )
    exposed_clauses: list[str] = Field(
        description=(
            "List of clause references or short excerpts in the contract that conflict with "
            "or are inadequate for the new obligation. Empty list if no exposure found."
        )
    )
    impact: Literal["none", "moderate", "severe"] = Field(
        description=(
            "Severity of exposure: 'none' means the contract already satisfies the obligation, "
            "'moderate' means minor gaps requiring amendment, "
            "'severe' means fundamental conflict or missing provisions."
        )
    )
    remediation_action: str = Field(
        description=(
            "Specific action required to bring the contract into compliance. "
            "Use 'No action required' when impact is none."
        )
    )


class ObligationImpact(BaseModel):
    """Full impact assessment for one net-new obligation across all contracts."""

    obligation: NewObligation = Field(
        description="The net-new obligation being assessed."
    )
    contract_exposures: list[ContractExposure] = Field(
        description="Exposure assessments for each contract in the corpus."
    )
    overall_impact: Literal["none", "moderate", "severe"] = Field(
        description=(
            "Rolled-up severity across all contracts: the highest severity level "
            "found in any single contract exposure."
        )
    )
    action_item: str = Field(
        description=(
            "A single, prioritised remediation action item to address the most "
            "severe exposure. Should be specific enough to assign to a person."
        )
    )


class ComplianceState(BaseModel):
    """Versioned compliance tracker object — updated after each regulatory change cycle."""

    version: int = Field(
        description="Monotonically increasing version number incremented on every update."
    )
    last_updated: str = Field(
        description="ISO date of the most recent update to this state object (e.g. '2025-01-15')."
    )
    jurisdiction: str = Field(
        description="Jurisdiction covered by this compliance state."
    )
    obligations: list[Obligation] = Field(
        description="Complete list of all active and pending obligations after this update cycle."
    )
    pending_actions: list[str] = Field(
        description="Ordered list of outstanding remediation action items across all obligations."
    )
    last_update_summary: str = Field(
        description="Plain-English summary of what changed in the most recent update cycle."
    )


class ChangeTrackerResult(BaseModel):
    """Final output of one regulatory change tracking run."""

    update_id: str = Field(
        description="Identifier of the regulatory update that was processed."
    )
    net_new_count: int = Field(
        description="Number of net-new obligations identified that were not in the prior register."
    )
    impact_assessments: list[ObligationImpact] = Field(
        description="Full impact assessment for each net-new obligation."
    )
    updated_state: ComplianceState = Field(
        description="The versioned compliance state object after incorporating this update."
    )
    summary: str = Field(
        description=(
            "2-4 sentence executive summary: how many new obligations were found, "
            "highest severity level encountered, and top priority action."
        )
    )
