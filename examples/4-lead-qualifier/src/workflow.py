from langchain_openai import ChatOpenAI

from .prompts import ICP_RUBRIC
from .schema import LeadScore


def create_workflow():
    """Return a runnable that scores a lead description against the ICP rubric."""
    llm = ChatOpenAI(model="gpt-4o-mini")
    return ICP_RUBRIC | llm.with_structured_output(LeadScore)
