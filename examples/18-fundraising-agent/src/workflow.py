from langchain_openai import ChatOpenAI

from .agents import draft_for_persona
from .schema import FundraisingPackage


def run(company_brief: str) -> FundraisingPackage:
    """
    Audience-targeted fundraising generator: runs three persona-specific LLM calls
    (VC, PE, family office) and assembles the results into a FundraisingPackage.

    Returns:
        FundraisingPackage with persona-specific materials and universal value props
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    vc = draft_for_persona(llm, company_brief, "vc")
    pe = draft_for_persona(llm, company_brief, "pe")
    fo = draft_for_persona(llm, company_brief, "family_office")

    return FundraisingPackage(
        round_type="Series B",
        vc_materials=vc,
        pe_materials=pe,
        family_office_materials=fo,
        universal_value_props=vc.headline_metrics[:3],
    )
