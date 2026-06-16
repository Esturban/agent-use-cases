from typing import List, Literal

from pydantic import BaseModel, Field


class LeadScore(BaseModel):
    company: str
    score: int = Field(ge=1, le=10, description="ICP fit score from 1 (no fit) to 10 (perfect fit)")
    tier: Literal["hot", "warm", "cold"]
    criteria_met: List[str]
    criteria_missed: List[str]
    recommended_action: str
    reasoning: str
