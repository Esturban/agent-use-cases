from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .schema import FundraisingMaterials, FundraisingPackage

PERSONA_PROMPTS = {
    "vc": (
        "You are drafting fundraising materials for a VENTURE CAPITAL investor. "
        "VCs want TAM, growth velocity, and founder-market fit. "
        "Speak in ARR, NRR, burn multiple, and CAC payback. "
        "Frame the story around category creation and long-term compounding."
    ),
    "pe": (
        "You are drafting fundraising materials for a PRIVATE EQUITY investor. "
        "PE firms want EBITDA (actual or near-term path), operational efficiency, "
        "and a clear exit multiple. Avoid hype. "
        "Frame the story around margin expansion, process improvement, and downside protection."
    ),
    "family_office": (
        "You are drafting fundraising materials for a FAMILY OFFICE investor. "
        "Family offices want capital preservation, dividend potential, "
        "and downside protection. They are long-horizon, relationship-driven. "
        "Frame the story around resilience, governance quality, and stable compounding."
    ),
}


def _draft_for_persona(
    llm: ChatOpenAI,
    brief: str,
    persona: Literal["vc", "pe", "family_office"],
) -> FundraisingMaterials:
    system = SystemMessage(PERSONA_PROMPTS[persona])
    drafter = system | llm.with_structured_output(FundraisingMaterials)
    return drafter.invoke(
        HumanMessage(
            content=f"Company brief:\n\n{brief}\n\nDraft materials for target_persona='{persona}'"
        )
    )


def run(company_brief: str) -> FundraisingPackage:
    """
    Audience-targeted fundraising generator: runs three persona-specific LLM calls
    (VC, PE, family office) and assembles the results into a FundraisingPackage.

    Returns:
        FundraisingPackage with persona-specific materials and universal value props
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    vc = _draft_for_persona(llm, company_brief, "vc")
    pe = _draft_for_persona(llm, company_brief, "pe")
    fo = _draft_for_persona(llm, company_brief, "family_office")

    return FundraisingPackage(
        round_type="Series B",
        vc_materials=vc,
        pe_materials=pe,
        family_office_materials=fo,
        universal_value_props=vc.headline_metrics[:3],
    )
