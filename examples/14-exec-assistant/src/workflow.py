from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .prompts import ASSISTANT_SYSTEM
from .schema import ExecOutput


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
