from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .prompts import ADVISOR_SYSTEM
from .schema import ReadinessReport


def run(company_brief: str) -> ReadinessReport:
    """
    Multi-dimension transaction readiness advisor: evaluates governance, financials,
    market_position, legal, and narrative with a go/no-go gate per dimension.

    Returns:
        ReadinessReport with dimensional scores, gates, and prioritized critical path
    """
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    advisor = ADVISOR_SYSTEM | llm.with_structured_output(ReadinessReport)
    return advisor.invoke(
        HumanMessage(content="Company brief:\n\n" + company_brief)
    )
