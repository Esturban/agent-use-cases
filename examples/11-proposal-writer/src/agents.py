from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .prompts import SUPERVISOR_SYSTEM, WRITER_SYSTEM
from .schema import Proposal, ProposalOutline


def outline_rfp(llm: ChatOpenAI, rfp_text: str) -> ProposalOutline:
    """Decompose an RFP into a structured outline with win themes and requirements."""
    supervisor = SUPERVISOR_SYSTEM | llm.with_structured_output(ProposalOutline)
    return supervisor.invoke(HumanMessage(content="RFP to decompose:\n\n" + rfp_text))


def draft_proposal(llm: ChatOpenAI, rfp_text: str, outline: ProposalOutline) -> Proposal:
    """Draft a winning proposal response given the RFP and structured outline."""
    context = (
        "RFP text:\n" + rfp_text + "\n\n"
        "Win themes: " + ", ".join(outline.win_themes) + "\n"
        "Evaluation criteria: " + ", ".join(outline.evaluation_criteria) + "\n"
        "Mandatory requirements:\n"
        + "\n".join(
            "- [" + r.section + "] " + r.requirement
            for r in outline.requirements
            if r.mandatory
        )
    )
    writer = WRITER_SYSTEM | llm.with_structured_output(Proposal)
    return writer.invoke(context)
