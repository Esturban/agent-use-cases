from typing import Literal

from pydantic import BaseModel, Field


class NpsResponse(BaseModel):
    customer_id: str = Field(description="Unique customer identifier.")
    score: int = Field(description="NPS score from 0 to 10.", ge=0, le=10)
    comment: str = Field(description="Customer's open-text feedback.")


class RoutedResponse(BaseModel):
    customer_id: str = Field(description="Unique customer identifier.")
    score: int = Field(description="NPS score from 0 to 10.")
    comment: str = Field(description="Customer's open-text feedback.")
    segment: Literal["retain", "neutral", "escalate"] = Field(
        description=(
            "Routing segment: 'escalate' for detractors (0-6) with strong churn signal, "
            "'retain' for promoters (9-10), 'neutral' for passives (7-8) or mixed signals."
        )
    )
    follow_up_draft: str = Field(
        description="Personalised follow-up message draft tailored to the segment and comment."
    )
    reasoning: str = Field(
        description="One sentence explaining why this segment was chosen."
    )


class ChurnBatch(BaseModel):
    total: int = Field(description="Total number of NPS responses processed.")
    retain_count: int = Field(description="Number of responses routed to retain.")
    neutral_count: int = Field(description="Number of responses routed to neutral.")
    escalate_count: int = Field(description="Number of responses routed to escalate.")
    responses: list[RoutedResponse] = Field(description="Per-response routing and follow-up.")
