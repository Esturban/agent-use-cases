from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    description: str = Field(description="What needs to be done")
    owner: Optional[str] = Field(default=None, description="Person responsible")
    due_date: Optional[str] = Field(default=None, description="Deadline, e.g. 'Friday 20 Jun'")
    priority: Literal["high", "medium", "low"]


class FollowUpEntry(BaseModel):
    topic: str = Field(description="What is being tracked")
    waiting_on: Optional[str] = Field(default=None, description="Who must act next")
    check_in_by: Optional[str] = Field(default=None, description="When to chase if no update")
    notes: str = Field(description="Context needed to follow up effectively")


class ExecOutput(BaseModel):
    """Structured executive assistant output from an email thread or meeting transcript."""

    input_type: Literal["email_thread", "meeting_transcript"]
    draft_reply: str = Field(
        description="A polished draft reply or acknowledgement ready to send"
    )
    subject_line: Optional[str] = Field(
        default=None,
        description="Suggested email subject line (email_thread inputs only)",
    )
    action_items: List[ActionItem] = Field(
        description="All discrete tasks extracted, with owner and deadline where identifiable"
    )
    follow_up_tracker: List[FollowUpEntry] = Field(
        description="Items that need monitoring but are not direct action items yet"
    )
    meeting_summary: Optional[str] = Field(
        default=None,
        description="2-4 sentence summary (meeting_transcript inputs only)",
    )
