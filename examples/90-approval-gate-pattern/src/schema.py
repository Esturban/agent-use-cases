"""Typed schemas for the human-in-the-loop approval-gate pattern."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ProposedAction(BaseModel):
    action_type: Literal[
        "post_journal_entry", "revoke_access", "send_collection_notice"
    ] = Field(description="The category of irreversible action being proposed")
    summary: str = Field(
        description="One-sentence human-readable summary of what this action does"
    )
    payload: dict = Field(
        description=(
            "The action-specific parameters that would execute if approved, "
            "e.g. {'account': '2100', 'amount': 4200.0}"
        )
    )
    risk_level: Literal["low", "medium", "high"] = Field(
        description="Risk tier used to decide whether the gate is mandatory or advisory"
    )


class ApprovalDecision(BaseModel):
    decision: Literal["approve", "edit", "reject"] = Field(
        description="The human reviewer's resolution of the proposed action"
    )
    edited_payload: Optional[dict] = Field(
        default=None,
        description="Replacement payload when decision='edit'; ignored otherwise",
    )
    rationale: str = Field(
        description="The human's reason for the decision -- always logged, even on approve"
    )


class ActionResult(BaseModel):
    executed: bool = Field(
        description="True only if the action actually fired; false for reject or any failure"
    )
    final_payload: Optional[dict] = Field(
        default=None, description="The payload that was actually executed, after any human edit"
    )
    decision_log: str = Field(
        description="Audit-trail entry: what was proposed, what the human decided, and why"
    )
