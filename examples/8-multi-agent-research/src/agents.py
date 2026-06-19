from langchain_openai import ChatOpenAI

from .prompts import RESEARCHER_SYSTEM, SUPERVISOR_SYSTEM, WRITER_SYSTEM
from .schema import ResearchFindings, WrittenBrief


def create_supervisor(llm: ChatOpenAI):
    """Returns a chain that refines a vague topic into a focused research question."""
    return SUPERVISOR_SYSTEM | llm


def create_researcher(llm: ChatOpenAI):
    """Returns a chain that produces structured ResearchFindings from a question."""
    return RESEARCHER_SYSTEM | llm.with_structured_output(ResearchFindings)


def create_writer(llm: ChatOpenAI):
    """Returns a chain that turns research findings into an executive WrittenBrief."""
    return WRITER_SYSTEM | llm.with_structured_output(WrittenBrief)
