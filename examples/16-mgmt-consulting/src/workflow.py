from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .schema import CostOptimizationReport

CONSULTANT_SYSTEM = SystemMessage(
    """You are a management consultant conducting a cost optimization review.

Analyse the operational profile provided and identify inefficiencies. For each one:

1. Classify by EFFORT to fix: low / medium / high
2. Classify by SAVINGS POTENTIAL (impact): low / medium / high
3. Assign the correct 2x2 quadrant using this exact logic:
   - effort=low  + impact=high  --> quick_win
   - effort=high + impact=high  --> major_project
   - effort=low  + impact=low   --> fill_in
   - effort=high + impact=low   --> thankless_task
   Note: treat "medium" effort as "low" for quadrant purposes; treat "medium" impact
   as "high" for quadrant purposes. The goal is to bias toward action.
4. Estimate annual saving in GBP where the data supports it.
5. List concrete implementation steps (3-5 steps).

Sort quick_wins first -- they are the client's highest ROI actions.
Provide an executive_summary of 3-4 sentences and a prioritization_note."""
)


def run(operational_profile: str) -> CostOptimizationReport:
    """
    Single-call cost optimization consultant: reads the operational profile,
    returns a CostOptimizationReport with recommendations ranked in a 2x2 matrix.

    Returns:
        CostOptimizationReport with quick_wins, major_projects, fill_ins, thankless_tasks
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    consultant = CONSULTANT_SYSTEM | llm.with_structured_output(CostOptimizationReport)
    return consultant.invoke(
        HumanMessage(content="Operational profile:\n\n" + operational_profile)
    )
