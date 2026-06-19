from typing import Literal

from pydantic import BaseModel, Field


class PatientCriteria(BaseModel):
    condition: str = Field(description="Medical condition or disease to search for.")
    age: int = Field(description="Patient age in years.", ge=0, le=120)
    location: str = Field(default="", description="Optional location filter (city, state, or country).")
    exclusions: list[str] = Field(
        default_factory=list,
        description="Conditions or characteristics that would exclude the patient (e.g. 'prior chemotherapy').",
    )


class TrialMatch(BaseModel):
    nct_id: str = Field(description="ClinicalTrials.gov NCT identifier (e.g. NCT01234567).")
    title: str = Field(description="Official study title.")
    phase: str = Field(description="Trial phase (e.g. Phase 1, Phase 2, Phase 3, N/A).")
    status: str = Field(description="Recruitment status (e.g. Recruiting, Active not recruiting).")
    eligibility_summary: str = Field(
        description="Plain-language 2-3 sentence summary of key eligibility criteria."
    )
    match_confidence: Literal["high", "medium", "low"] = Field(
        description=(
            "Confidence that this patient meets eligibility: "
            "high = clearly matches all criteria; medium = likely matches but some ambiguity; "
            "low = may match but significant criteria unclear."
        )
    )
    why_matches: str = Field(
        description="One sentence explaining why this trial is a good match for the given criteria."
    )


class TrialSearchResult(BaseModel):
    condition: str = Field(description="Medical condition searched.")
    trials_found: int = Field(description="Total number of trials returned by the API.")
    matches: list[TrialMatch] = Field(
        description="Ranked list of trials filtered and scored for eligibility fit."
    )
