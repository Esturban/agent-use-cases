"""Typed schemas for the ledger-integrity period-close supervisor.

ControlException is the common shape every domain check (adapted from ids 44,
46, plus new fixed-asset, fraud, and SoD checks) reports into, so the
supervisor can rank and correlate across domains without caring which check
produced which finding. ProposedAction / ApprovalDecision / ActionResult are
copied and adapted from the approval-gate pattern (id 90), same as id 91,
per this repo's replication convention.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class JournalLine(BaseModel):
    side: Literal["debit", "credit"] = Field(description="Debit or credit side")
    account_code: str = Field(description="4-digit GL account code, e.g. '2100'")
    amount: float = Field(description="Positive posting amount", gt=0)
    prepared_by: str = Field(description="Identity that prepared this entry")


class JournalEntry(BaseModel):
    entry_id: str
    description: str
    counterparty: str = Field(description="Vendor or customer this entry relates to")
    lines: list[JournalLine]


class BankTransaction(BaseModel):
    txn_id: str
    date: str = Field(description="YYYY-MM-DD")
    amount: float = Field(description="Signed: positive=inflow, negative=outflow")
    counterparty: str


class GLCashEntry(BaseModel):
    entry_id: str
    date: str = Field(description="YYYY-MM-DD")
    amount: float = Field(description="Signed: positive=debit to cash, negative=credit")
    reference: str


class FixedAsset(BaseModel):
    asset_id: str
    cost: float
    accumulated_depreciation: float
    useful_life_years: int
    disposed: bool = False
    disposal_proceeds: Optional[float] = None


class PaymentTransaction(BaseModel):
    txn_id: str
    date: str = Field(description="YYYY-MM-DD")
    payee: str
    amount: float
    is_new_payee: bool = False


class SoDRoleGrant(BaseModel):
    identity: str
    role: str


class ControlException(BaseModel):
    domain: Literal[
        "jv_posting",
        "bank_reconciliation",
        "fixed_asset",
        "fraud_screening",
        "segregation_of_duties",
    ] = Field(description="Which control check produced this exception")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="Control severity -- critical/high are candidates for the approval gate"
    )
    description: str = Field(description="What the check found")
    financial_exposure: float = Field(
        description="Dollar amount at risk -- used to rank exceptions and select the gated one"
    )
    entities_involved: list[str] = Field(
        default_factory=list,
        description="Identities, vendors, or account codes implicated -- used for cross-domain correlation",
    )
    recommended_action: str = Field(description="What a controller should do about this")
    requires_approval: bool = Field(
        description="True once financial_exposure crosses the materiality threshold"
    )


class ControlsExceptionRegister(BaseModel):
    period: str
    exceptions: list[ControlException]
    cross_domain_correlations: list[str] = Field(default_factory=list)
    total_exposure: float
    close_status: Literal["blocked", "conditionally_closed", "closed"]
    audit_narrative: Optional[str] = Field(
        default=None, description="Citation-grounded narrative from the audit-trail synthesizer"
    )


class ProposedAction(BaseModel):
    action_type: Literal["reverse_entry", "escalate_to_investigations", "adjust_book_value"] = Field(
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
        description="The human controller's resolution of the proposed action"
    )
    edited_payload: Optional[dict] = Field(
        default=None, description="Replacement payload when decision='edit'; ignored otherwise"
    )
    rationale: str = Field(description="The controller's reason for the decision -- always logged")


class ActionResult(BaseModel):
    executed: bool = Field(description="True only if the action actually fired")
    final_payload: Optional[dict] = Field(
        default=None, description="The payload that was actually executed, after any human edit"
    )
    decision_log: str = Field(description="Audit-trail entry: what was proposed, decided, and why")
