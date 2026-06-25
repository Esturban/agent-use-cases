"""Schema definitions for the Expense Audit Agent."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ExpenseLine(BaseModel):
    """A single line item on an employee expense report."""

    line_id: str = Field(description="Unique identifier for this expense line")
    date: str = Field(description="Expense date in YYYY-MM-DD format")
    category: Literal[
        "accommodation",
        "meals",
        "transport",
        "entertainment",
        "equipment",
        "other",
    ] = Field(description="Expense category used to select the applicable policy rule")
    amount: float = Field(description="Amount claimed in the report currency")
    city: Optional[str] = Field(
        default=None,
        description="City where the expense was incurred; used to determine tier-based limits",
    )
    description: str = Field(
        description="Free-text description of the expense provided by the employee"
    )
    receipt_attached: bool = Field(
        description="Whether a receipt or invoice was attached to support this line"
    )
    pre_approved: bool = Field(
        default=False,
        description="Whether the expense was pre-approved before being incurred",
    )
    class_of_travel: Optional[Literal["economy", "premium_economy", "business", "first"]] = Field(
        default=None,
        description="Cabin class for transport expenses; required to apply the travel policy rule",
    )


class PolicyViolation(BaseModel):
    """A single policy violation detected for an expense line."""

    line_id: str = Field(description="ID of the expense line that triggered this violation")
    rule_id: str = Field(
        description=(
            "Short code identifying the policy rule breached "
            "(e.g. MEAL-001, HOTEL-002, TRAVEL-003, RECEIPT-001, ENT-001, EQUIP-001)"
        )
    )
    rule_description: str = Field(
        description="Human-readable description of the policy rule that was violated"
    )
    violation_detail: str = Field(
        description="Specific detail about how the line breaches the rule, including amounts"
    )
    severity: Literal["info", "warn", "block"] = Field(
        description=(
            "Severity level: "
            "info=minor note only, "
            "warn=requires approver review, "
            "block=cannot approve as-is"
        )
    )


class AuditResult(BaseModel):
    """Full audit output for a single employee expense report."""

    report_id: str = Field(description="Unique identifier for the expense report being audited")
    employee_name: str = Field(description="Full name of the employee who submitted the report")
    total_claimed: float = Field(
        description="Sum of all amounts claimed across all expense lines"
    )
    violations: List[PolicyViolation] = Field(
        description="List of all policy violations detected; empty if fully compliant"
    )
    compliant_lines: int = Field(
        description="Count of expense lines with no policy violations"
    )
    violation_lines: int = Field(
        description="Count of expense lines that triggered at least one policy violation"
    )
    approval_tier: Literal[
        "auto_approve",
        "line_manager",
        "finance_director",
        "rejected",
    ] = Field(
        description=(
            "Routing decision: "
            "auto_approve=no violations, "
            "line_manager=info/warn only, "
            "finance_director=block violations with total<5000, "
            "rejected=block violations with total>=5000 or missing receipt above threshold"
        )
    )
    audit_summary: str = Field(
        description="Narrative summary of the audit outcome for the approver"
    )
