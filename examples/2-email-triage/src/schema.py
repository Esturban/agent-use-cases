from typing import Literal

from pydantic import BaseModel


class EmailTriage(BaseModel):
    urgency: Literal["high", "medium", "low"]
    category: Literal["billing", "technical", "general", "spam"]
    summary: str
    recommended_action: str
