from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class RiskFinding(BaseModel):
    severity: Literal["critical", "high", "medium", "low"]
    category: Literal[
        "liability",
        "payment",
        "ip",
        "termination",
        "confidentiality",
        "governance",
        "compliance",
        "other",
    ]
    clause_reference: str = Field(
        description="Section or clause number where this risk appears, e.g. 'Section 8.2'"
    )
    issue: str = Field(description="One sentence describing what creates the risk")
    implication: str = Field(description="Business impact if this risk materializes")
    recommended_redline: str = Field(
        description="Specific language change or addition to address this risk"
    )


class MissingProtection(BaseModel):
    protection: str = Field(
        description="Standard protection absent from this contract, e.g. 'limitation of liability cap'"
    )
    why_needed: str = Field(description="Why this protection matters for this contract type")
    suggested_clause: str = Field(description="Draft language to add")


class NegotiationPoint(BaseModel):
    priority: Literal["must_have", "should_have", "nice_to_have"]
    topic: str
    current_position: str = Field(description="What the contract currently says on this point")
    target_position: str = Field(description="What you should push for in negotiation")


class ContractReview(BaseModel):
    contract_type: str = Field(
        description="Type of contract, e.g. 'Professional Services Agreement'"
    )
    counterparty: Optional[str] = Field(
        default=None, description="Name of the other party if identifiable in the document"
    )
    governing_law: Optional[str] = Field(
        default=None, description="Governing law and jurisdiction if stated"
    )
    overall_risk: Literal["high", "medium", "low"]
    executive_summary: str = Field(
        description="2-3 sentence summary of the contract's key risks for a senior executive"
    )
    risk_findings: List[RiskFinding] = Field(
        description="All identified risk clauses sorted by severity, each citing its clause reference"
    )
    missing_protections: List[MissingProtection] = Field(
        description="Standard protections that are absent from this contract"
    )
    negotiation_points: List[NegotiationPoint] = Field(
        description="Prioritized list of points to raise in negotiation"
    )
