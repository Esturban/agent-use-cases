from langchain_openai import ChatOpenAI

from .agents import draft_proposal, outline_rfp


def run(rfp_text: str) -> dict:
    """
    Multi-agent proposal writer: Supervisor decomposes the RFP, Writer drafts the response.

    Returns:
        {"outline": ProposalOutline, "proposal": Proposal}
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    outline = outline_rfp(llm, rfp_text)
    proposal = draft_proposal(llm, rfp_text, outline)
    return {"outline": outline, "proposal": proposal}
