from typing import List, Optional

from pydantic import BaseModel, Field


class RFPRequirement(BaseModel):
    section: str = Field(description="Which section or question this requirement comes from")
    requirement: str = Field(description="The specific thing the client is asking for")
    mandatory: bool = Field(description="True if this is a pass/fail requirement")


class ProposalOutline(BaseModel):
    """Structured decomposition of an RFP produced by the supervisor."""

    client_name: Optional[str] = None
    rfp_title: str
    submission_deadline: Optional[str] = None
    requirements: List[RFPRequirement] = Field(
        description="All requirements extracted from the RFP, mandatory ones first"
    )
    win_themes: List[str] = Field(
        description="2-4 strategic themes that should run through the whole proposal"
    )
    evaluation_criteria: List[str] = Field(
        description="How the client will score proposals, in priority order"
    )
    sections_to_write: List[str] = Field(
        description="Ordered list of proposal sections that need to be drafted"
    )


class Proposal(BaseModel):
    """Final assembled proposal document."""

    client_name: Optional[str] = None
    rfp_title: str
    win_themes: List[str]
    executive_summary: str = Field(
        description="Why we win -- lead with the client's problem and our unique answer"
    )
    our_approach: str = Field(
        description="Methodology and how we would deliver the work"
    )
    team_and_credentials: str = Field(
        description="Relevant experience, key personnel, and why we are best placed to deliver"
    )
    timeline: str = Field(
        description="Phased project plan with key milestones and deliverables"
    )
    commercial: str = Field(
        description="Pricing structure, value drivers, and commercial terms"
    )
    why_us: str = Field(
        description="Differentiators -- what we offer that competitors cannot match"
    )
    key_differentiators: List[str] = Field(
        description="3-5 bullet-point differentiators for the cover page or summary slide"
    )
    compliance_statement: str = Field(
        description="Confirmation that all mandatory requirements are met"
    )
