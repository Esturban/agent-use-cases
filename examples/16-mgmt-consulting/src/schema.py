from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    title: str = Field(description="Short descriptive name for this recommendation")
    category: Literal["process", "technology", "people", "structure"]
    effort: Literal["low", "medium", "high"]
    impact: Literal["low", "medium", "high"]
    quadrant: Literal["quick_win", "major_project", "fill_in", "thankless_task"] = Field(
        description=(
            "quick_win=low effort+high impact, major_project=high effort+high impact, "
            "fill_in=low effort+low impact, thankless_task=high effort+low impact"
        )
    )
    estimated_annual_saving: Optional[str] = Field(
        default=None,
        description="Estimated annual saving in SAR where quantifiable, e.g. 'SAR 180k' or 'SAR 1.2m'. Always SAR.",
    )
    rationale: str = Field(description="Why this is an inefficiency and what fixing it achieves")
    implementation_steps: List[str] = Field(
        description="Concrete ordered steps to implement this recommendation"
    )


class CostOptimizationReport(BaseModel):
    """Management consulting cost optimization assessment with 2x2 effort-impact ranking."""

    company: Optional[str] = None
    total_addressable_saving: Optional[str] = Field(
        default=None,
        description="Sum of all quantified annual savings across all recommendations, in SAR, e.g. 'SAR 4.2m'",
    )
    executive_summary: str = Field(
        description="3-4 sentences for a C-suite audience: what was found and the priority action"
    )
    quick_wins: List[Recommendation] = Field(
        description="Low effort, high impact -- highest ROI, do first"
    )
    major_projects: List[Recommendation] = Field(
        description="High effort, high impact -- worth doing, need a project plan"
    )
    fill_ins: List[Recommendation] = Field(
        description="Low effort, low impact -- do when bandwidth allows"
    )
    thankless_tasks: List[Recommendation] = Field(
        description="High effort, low impact -- avoid or deprioritise"
    )
    prioritization_note: str = Field(
        description="Guidance on sequencing: which quick win to tackle first and why"
    )
