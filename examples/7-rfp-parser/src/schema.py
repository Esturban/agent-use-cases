from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Deadline(BaseModel):
    label: str = Field(description="What this deadline is for, e.g. 'Proposal submission'")
    date: str = Field(description="Date in YYYY-MM-DD format if parseable, otherwise the raw text")
    is_hard: bool = Field(description="True if missing this deadline disqualifies the submission")


class ScoringCriterion(BaseModel):
    criterion: str = Field(description="Name of the evaluation criterion")
    weight_percent: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Percentage weight if stated in the RFP, else null",
    )
    description: str = Field(description="What the evaluators are looking for")


class Requirement(BaseModel):
    id: str = Field(description="Short identifier, e.g. 'REQ-01'")
    category: Literal["technical", "administrative", "legal", "financial"]
    text: str = Field(description="The requirement as stated")
    mandatory: bool = Field(description="True if explicitly required, False if preferred/nice-to-have")


class RFPExtraction(BaseModel):
    title: str = Field(description="Official name or title of the RFP")
    issuing_agency: str
    budget_ceiling: Optional[str] = Field(
        default=None,
        description="Maximum contract value if stated, as a string (e.g. '$500,000')",
    )
    contract_duration: Optional[str] = Field(
        default=None,
        description="Length of the contract period if stated",
    )
    deadlines: List[Deadline]
    requirements: List[Requirement]
    scoring_criteria: List[ScoringCriterion]
    summary: str = Field(description="Two-sentence plain-English summary of what is being procured")
