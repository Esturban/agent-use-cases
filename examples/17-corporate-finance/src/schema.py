from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class DimensionAssessment(BaseModel):
    dimension: Literal["governance", "financials", "market_position", "legal", "narrative"]
    score: int = Field(description="0-10 readiness score for this dimension")
    gate: Literal["pass", "conditional", "fail"] = Field(
        description=(
            "pass=ready now, conditional=fixable within 6 months, "
            "fail=structural blocker requiring major remediation"
        )
    )
    strengths: List[str] = Field(description="Positive factors in this dimension")
    blockers: List[str] = Field(
        description="Specific issues that must be resolved before transaction"
    )
    remediation: List[str] = Field(
        description="Concrete steps to address each blocker"
    )


class ReadinessReport(BaseModel):
    """Capital markets transaction readiness assessment across five dimensions."""

    company: Optional[str] = None
    transaction_type: Literal["ipo", "series_a", "series_b", "growth_equity", "pe_buyout"]
    overall_status: Literal["ready", "ready_with_conditions", "not_ready"] = Field(
        description=(
            "ready=all gates pass, ready_with_conditions=one or more conditional but no fail, "
            "not_ready=at least one fail gate"
        )
    )
    executive_summary: str = Field(
        description="3-4 sentences: overall readiness verdict and the single biggest blocker"
    )
    dimensions: List[DimensionAssessment] = Field(
        description="All five dimensions assessed, in order: governance, financials, "
        "market_position, legal, narrative"
    )
    critical_path: List[str] = Field(
        description="Ordered actions the company must take to reach 'ready' status"
    )
    estimated_time_to_ready: str = Field(
        description="Realistic estimate, e.g. '4-6 months', 'ready now', '12+ months'"
    )
    key_value_drivers: List[str] = Field(
        description="What makes this company attractive to investors despite the blockers"
    )
