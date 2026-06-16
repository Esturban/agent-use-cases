from typing import Literal

from pydantic import BaseModel, Field


class TicketClassification(BaseModel):
    ticket_type: Literal["billing", "technical", "account", "feature_request", "other"]
    urgency: Literal["critical", "high", "medium", "low"]
    team: Literal["billing", "engineering", "account_management", "product", "general_support"]
    confidence: float = Field(ge=0.0, le=1.0, description="Classifier confidence 0-1")
    reasoning: str = Field(description="One sentence explaining the routing decision")


class DraftReply(BaseModel):
    subject: str
    body: str
    internal_note: str = Field(description="Note for the support agent, not sent to customer")
    escalate: bool = Field(description="True if this needs a human to review before sending")
