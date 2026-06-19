from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .prompts import PERSONA_PROMPTS
from .schema import FundraisingMaterials


def draft_for_persona(
    llm: ChatOpenAI,
    brief: str,
    persona: Literal["vc", "pe", "family_office"],
) -> FundraisingMaterials:
    """Draft fundraising materials tailored to the given investor persona."""
    system = SystemMessage(PERSONA_PROMPTS[persona])
    drafter = system | llm.with_structured_output(FundraisingMaterials)
    return drafter.invoke(
        HumanMessage(
            content=f"Company brief:\n\n{brief}\n\nDraft materials for target_persona='{persona}'"
        )
    )
