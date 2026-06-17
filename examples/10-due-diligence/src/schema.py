from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class DocumentFindings(BaseModel):
    """Raw findings extracted from a single due diligence document."""

    document_name: str
    document_type: Literal[
        "financials", "contract", "management_bio", "regulatory", "corporate", "other"
    ]
    key_findings: List[str] = Field(
        description="Concrete facts extracted from this document, each as one sentence"
    )
    red_flags: List[str] = Field(
        description="Issues in this document that warrant closer scrutiny"
    )
    questions_raised: List[str] = Field(
        description="Questions this document raises that need to be answered"
    )


class RiskItem(BaseModel):
    area: Literal[
        "financial", "commercial", "operational", "legal", "management", "regulatory"
    ]
    severity: Literal["critical", "high", "medium", "low"]
    likelihood: Literal["high", "medium", "low"]
    title: str = Field(description="Short title for this risk, e.g. 'Revenue concentration'")
    finding: str = Field(
        description="Specific evidence from the documents that supports this risk"
    )
    source_document: str = Field(
        description="Which document(s) this finding came from"
    )
    mitigation: str = Field(
        description="Recommended mitigation or further investigation required"
    )


class DDReport(BaseModel):
    """Unified commercial due diligence report synthesised from multiple documents."""

    target_company: Optional[str] = Field(
        default=None, description="Name of the company being reviewed if identifiable"
    )
    documents_reviewed: List[str] = Field(
        description="List of documents that were analysed"
    )
    overall_assessment: Literal["proceed", "proceed_with_conditions", "do_not_proceed"]
    executive_summary: str = Field(
        description="3-4 sentence summary for a deal committee"
    )
    risk_items: List[RiskItem] = Field(
        description="All identified risks sorted by severity then likelihood"
    )
    key_conditions: List[str] = Field(
        description="Conditions that must be satisfied before proceeding (if any)"
    )
    further_investigation: List[str] = Field(
        description="Areas requiring deeper diligence before a final decision"
    )
