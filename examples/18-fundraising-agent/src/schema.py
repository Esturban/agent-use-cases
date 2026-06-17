from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class FundraisingMaterials(BaseModel):
    target_persona: Literal["vc", "pe", "family_office"]
    investor_thesis: str = Field(
        description="What THIS investor type cares about, framed in their language"
    )
    headline_metrics: List[str] = Field(
        description="3-5 metrics most relevant to this persona (e.g. ARR, NRR for VC; EBITDA for PE)"
    )
    narrative_angle: str = Field(
        description="The framing and story that lands best with this specific audience"
    )
    key_asks: List[str] = Field(
        description="What you are asking for, framed specifically for this persona"
    )
    objection_responses: List[str] = Field(
        description="Pre-emptive responses to the top 2 likely objections from this persona"
    )
    suggested_materials: List[str] = Field(
        description="Which documents to send first to this persona and in what order"
    )


class FundraisingPackage(BaseModel):
    """Audience-targeted fundraising materials generated for three investor personas."""

    company: Optional[str] = None
    round_type: str = Field(description="The fundraising round, e.g. 'Series B'")
    vc_materials: FundraisingMaterials
    pe_materials: FundraisingMaterials
    family_office_materials: FundraisingMaterials
    universal_value_props: List[str] = Field(
        description="Strengths that resonate across all investor personas"
    )
