from typing import List, Optional

from pydantic import BaseModel, Field


class RegulatoryObligation(BaseModel):
    source_article: str = Field(
        description="Exact article or section reference, e.g. 'Article 32(1)(a)'"
    )
    obligation: str = Field(description="What the regulated firm must do")
    applies_to: str = Field(description="Who this obligation applies to")
    is_ongoing: bool = Field(description="True if the obligation is continuous, not one-off")
    deadline: Optional[str] = Field(
        default=None, description="Specific deadline if stated in the regulation"
    )


class RegulatoryPenalty(BaseModel):
    source_article: str = Field(
        description="Exact article or section reference for this penalty"
    )
    trigger: str = Field(description="What violation triggers this penalty")
    maximum_fine: Optional[str] = Field(
        default=None, description="Maximum financial penalty as stated in the text"
    )
    other_consequences: List[str] = Field(
        description="Non-financial consequences (e.g. suspension, public censure)"
    )


class ComplianceSummary(BaseModel):
    """Structured compliance extraction from a regulatory document."""

    regulation_name: str
    jurisdiction: str
    in_force_date: Optional[str] = Field(
        default=None, description="When the regulation takes effect"
    )
    obligations: List[RegulatoryObligation] = Field(
        description="All obligations found, each with exact article citation"
    )
    key_deadlines: List[str] = Field(
        description="Each deadline must include the article reference, e.g. 'Article 15: quarterly reporting within 30 days'"
    )
    penalties: List[RegulatoryPenalty] = Field(
        description="All penalties found, each with exact article citation"
    )
    high_priority_gaps: List[str] = Field(
        description="What firms most commonly miss or underestimate in compliance"
    )
