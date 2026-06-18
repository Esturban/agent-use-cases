from typing import Literal

from pydantic import BaseModel, Field


class EmailTriage(BaseModel):
    urgency: Literal["high", "medium", "low"] = Field(
        description="How urgently this email needs a response."
    )
    category: Literal["billing", "technical", "general", "spam"] = Field(
        description="The primary topic category of the email."
    )
    summary: str = Field(
        description="One-sentence plain-English summary of what the email is about."
    )
    recommended_action: str = Field(
        description="Concrete next step the recipient should take (e.g. 'Escalate to billing team')."
    )
