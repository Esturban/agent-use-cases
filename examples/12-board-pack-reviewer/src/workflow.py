from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .schema import DirectorBriefing

REVIEWER_SYSTEM = SystemMessage(
    """You are an experienced non-executive director reviewing a board pack before a meeting.

Your job is to produce a structured briefing that helps fellow directors cut through
management language and focus on what actually matters.

Rules:
- Frame every risk as a board concern, not a management update
- Name information gaps explicitly -- "the pack does not disclose X" is more useful than silence
- Questions for management must be probing: challenge assumptions, not process
- overall_pack_quality reflects governance fitness, not length or formatting
- If something looks like it has been sanitised or is missing context, say so

You serve shareholders and stakeholders, not management."""
)


def run(board_pack_text: str) -> DirectorBriefing:
    """
    Single-agent board pack reviewer: reads the full pack, returns a structured
    DirectorBriefing framed for a non-executive director.

    Returns:
        DirectorBriefing with top_risks, information_gaps, decisions_required,
        and questions_for_management
    """
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    reviewer = REVIEWER_SYSTEM | llm.with_structured_output(DirectorBriefing)
    return reviewer.invoke(
        HumanMessage(content="Board pack to review:\n\n" + board_pack_text)
    )
