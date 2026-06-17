from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class DimensionScore(BaseModel):
    score: int = Field(description="0-10 score for this dimension")
    rationale: str = Field(description="Evidence-based reason for the score")
    meets_threshold: bool = Field(description="True if this dimension clears the minimum bar")


class TargetAssessmentCard(BaseModel):
    company_name: str
    sector: str
    geography: str
    strategic_fit: DimensionScore = Field(
        description="How well the target fits the acquirer's strategic direction"
    )
    financial_fit: DimensionScore = Field(
        description="Revenue size, EBITDA margin, growth profile vs. rubric"
    )
    operational_fit: DimensionScore = Field(
        description="Integration complexity, management quality, cultural alignment"
    )
    overall_score: int = Field(description="Weighted composite 0-30")
    recommendation: Literal["proceed", "monitor", "pass"]
    investment_thesis: str = Field(
        description="One sentence on why this target creates value, or why it doesn't"
    )
    key_risks: List[str] = Field(description="Top 2-3 deal risks")
    suggested_next_step: str


class ScreeningResult(BaseModel):
    """Ranked M&A shortlist from multi-criteria screening."""

    acquirer: Optional[str] = None
    rubric_summary: str = Field(
        description="One sentence summarising the screening criteria applied"
    )
    shortlist: List[TargetAssessmentCard] = Field(
        description="Targets that scored above threshold, ranked by overall_score descending"
    )
    screened_out: List[str] = Field(
        description="Company names that failed one or more threshold criteria"
    )
    recommendation: str = Field(
        description="Top-line view on the most attractive target and why"
    )
