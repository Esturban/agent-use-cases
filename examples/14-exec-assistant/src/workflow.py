from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .schema import ExecOutput

ASSISTANT_SYSTEM = SystemMessage(
    """You are a world-class executive assistant.

From the input (either an email thread or a meeting transcript) produce ALL of the
following in one pass:

1. draft_reply      -- A polished, ready-to-send reply or acknowledgement.
                       If there is nothing substantive to reply to, draft a brief
                       acknowledgement that shows the email was read and understood.
2. action_items     -- Every discrete task mentioned or implied. Name the owner and
                       deadline where the text makes them identifiable. Priority:
                       "high" = blocking or time-sensitive, "medium" = this week,
                       "low" = nice-to-have.
3. follow_up_tracker -- Items that need monitoring but are not direct tasks yet
                       (e.g. "waiting for legal to respond", "call scheduled TBC").
4. meeting_summary  -- Populate only if the input is a meeting transcript.
5. subject_line     -- Populate only if the input is an email thread.

Set input_type = "email_thread" or "meeting_transcript" based on the content.
Every output must be populated -- no empty lists."""
)


def run(input_text: str) -> ExecOutput:
    """
    Fan-out executive assistant: one input produces a draft reply,
    extracted action items, and a follow-up tracker simultaneously.

    Returns:
        ExecOutput with draft_reply, action_items, follow_up_tracker
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    assistant = ASSISTANT_SYSTEM | llm.with_structured_output(ExecOutput)
    return assistant.invoke(
        HumanMessage(content="Input to process:\n\n" + input_text)
    )
