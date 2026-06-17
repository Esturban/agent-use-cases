from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .schema import Proposal, ProposalOutline

SUPERVISOR_SYSTEM = SystemMessage(
    """You are a proposal director reviewing an RFP before your team drafts a response.

Your job is to produce a structured decomposition of the RFP:
1. Extract every requirement, marking which are mandatory pass/fail criteria
2. Identify 2-4 win themes -- the strategic angles that should run through the whole proposal
3. Identify how the client will evaluate and score proposals
4. List the sections the proposal should contain, in order

Be precise. Requirements you miss now become compliance failures later."""
)

WRITER_SYSTEM = SystemMessage(
    """You are a senior proposal writer crafting a winning RFP response.

You will receive:
- The original RFP text
- A structured outline (win themes, requirements, evaluation criteria)

Your draft must:
- Lead every section with the client's problem, not your firm's capabilities
- Weave the win themes consistently through all sections
- Be specific about methodology -- no generic consulting language
- Address all mandatory requirements explicitly in the compliance_statement
- Keep the executive_summary under 200 words and punchy

Write to win, not to comply."""
)


def _outline(llm, rfp_text: str) -> ProposalOutline:
    supervisor = SUPERVISOR_SYSTEM | llm.with_structured_output(ProposalOutline)
    return supervisor.invoke(HumanMessage(content="RFP to decompose:\n\n" + rfp_text))


def _draft(llm, rfp_text: str, outline: ProposalOutline) -> Proposal:
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


def run(rfp_text: str) -> dict:
    """
    Multi-agent proposal writer: Supervisor decomposes the RFP, Writer drafts the response.

    Returns:
        {"outline": ProposalOutline, "proposal": Proposal}
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    outline = _outline(llm, rfp_text)
    proposal = _draft(llm, rfp_text, outline)
    return {"outline": outline, "proposal": proposal}
