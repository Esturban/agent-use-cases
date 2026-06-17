from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class TopRisk(BaseModel):
    rank: int = Field(description="Priority rank: 1 is the highest concern")
    area: Literal[
        "financial", "operational", "strategic", "regulatory", "governance", "reputational"
    ]
    severity: Literal["critical", "high", "medium"]
    title: str
    detail: str = Field(description="What specifically is the risk and why it matters to the board")
    source_section: str = Field(description="Which section of the board pack this comes from")
    suggested_question: str = Field(
        description="Question a non-executive director should ask management on this risk"
    )


class InformationGap(BaseModel):
    section: str = Field(description="Which section has the gap")
    missing: str = Field(description="What information is absent or unclear")
    why_it_matters: str = Field(description="Why the board needs this before deciding")


class DecisionRequired(BaseModel):
    item: str = Field(description="The specific decision or approval the board is being asked to make")
    context: str = Field(description="Background a director needs to vote on this item")
    recommendation: Optional[str] = Field(
        default=None,
        description="Management's stated recommendation, if provided"
    )
    key_consideration: str = Field(
        description="The one thing a director must weigh before approving"
    )


class DirectorBriefing(BaseModel):
    """Structured board pack review framed for a non-executive director."""

    company: Optional[str] = None
    meeting_date: Optional[str] = None
    overall_pack_quality: Literal["strong", "adequate", "weak"] = Field(
        description="Overall quality of the board pack as a governance document"
    )
    executive_assessment: str = Field(
        description="3-4 sentence summary for a NED arriving five minutes before the meeting"
    )
    top_risks: List[TopRisk] = Field(
        description="Up to five risks ranked by severity -- framed as NED concerns, not management euphemisms"
    )
    information_gaps: List[InformationGap] = Field(
        description="Material information absent from the pack that the board needs"
    )
    decisions_required: List[DecisionRequired] = Field(
        description="Items requiring board approval or formal decision"
    )
    questions_for_management: List[str] = Field(
        description="Suggested questions for the meeting -- probing, not procedural"
    )
