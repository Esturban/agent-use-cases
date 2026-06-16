from typing import List, Literal

from pydantic import BaseModel, Field


class ResumeScore(BaseModel):
    candidate_name: str
    overall_score: int = Field(ge=1, le=10, description="Overall fit score 1-10")
    tier: Literal["strong_yes", "yes", "maybe", "no"]
    years_experience: int = Field(ge=0, description="Estimated years of relevant experience")
    skills_matched: List[str] = Field(description="Job spec skills found in the resume")
    skills_missing: List[str] = Field(description="Job spec skills not found in the resume")
    standout: str = Field(description="One sentence on the strongest signal in this resume")
    concern: str = Field(description="One sentence on the biggest gap or risk")
    recommended_action: Literal["schedule_interview", "hold_for_review", "pass"]
