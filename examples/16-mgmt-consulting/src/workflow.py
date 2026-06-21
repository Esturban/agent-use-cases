from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .prompts import CONSULTANT_SYSTEM
from .schema import CostOptimizationReport


def run(operational_profile: str) -> CostOptimizationReport:
    """
    Single-call cost optimization consultant: reads the operational profile,
    returns a CostOptimizationReport with recommendations ranked in a 2x2 matrix.

    Returns:
        CostOptimizationReport with quick_wins, major_projects, fill_ins, thankless_tasks
    """
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    consultant = CONSULTANT_SYSTEM | llm.with_structured_output(CostOptimizationReport)
    return consultant.invoke(
        HumanMessage(content="Operational profile:\n\n" + operational_profile)
    )
