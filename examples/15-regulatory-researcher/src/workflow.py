from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .prompts import RESEARCHER_SYSTEM
from .schema import ComplianceSummary


def run(regulation_text: str) -> ComplianceSummary:
    """
    Citation-grounded regulatory extractor: every obligation, deadline, and
    penalty in the output must cite its source article.

    Returns:
        ComplianceSummary with fully cited obligations, deadlines, and penalties
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    researcher = RESEARCHER_SYSTEM | llm.with_structured_output(ComplianceSummary)
    return researcher.invoke(
        HumanMessage(content="Regulation text to analyse:\n\n" + regulation_text)
    )
