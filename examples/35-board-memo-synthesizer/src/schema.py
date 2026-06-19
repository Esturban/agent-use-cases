from typing import Literal

from pydantic import BaseModel, Field


class AnalystOpinion(BaseModel):
    lens: Literal["bull", "bear", "risk"] = Field(
        description="The analytical lens used: bull (upside case), bear (downside case), or risk (risk assessment)."
    )
    key_points: list[str] = Field(description="3-5 key points supporting this analyst's position.")
    conclusion: str = Field(description="One paragraph conclusion from this lens.")
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence in this analysis given the available information."
    )


class BoardMemo(BaseModel):
    topic: str = Field(description="The strategic topic or decision under review.")
    bull_case: AnalystOpinion = Field(description="Bull case analysis (upside opportunities).")
    bear_case: AnalystOpinion = Field(description="Bear case analysis (downside risks).")
    risk_case: AnalystOpinion = Field(description="Risk assessment (key risks and mitigations).")
    recommended_position: Literal["proceed", "pause", "reject"] = Field(
        description="Board-level recommendation synthesised from all three lenses."
    )
    executive_summary: str = Field(
        description="2-3 paragraph executive summary suitable for a board memo, citing all three analyst views."
    )
    one_sentence_verdict: str = Field(
        description="One sentence that encapsulates the recommended position and primary rationale."
    )
