from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .agents import create_researcher, create_supervisor, create_writer
from .schema import ResearchFindings


def run(topic: str) -> dict:
    """
    Supervisor -> Researcher -> Writer pipeline.

    Returns:
        {
            "refined_question": str,
            "research": ResearchFindings,
            "brief": WrittenBrief
        }
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Stage 1: Supervisor refines the question
    refined = create_supervisor(llm).invoke(HumanMessage(content=f"Topic: {topic}"))
    refined_question = refined.content.strip()

    # Stage 2: Researcher gathers findings
    research: ResearchFindings = create_researcher(llm).invoke(
        f"Research question: {refined_question}"
    )

    # Stage 3: Writer turns findings into a brief
    writer_input = (
        f"Research question: {refined_question}\n\n"
        "Key facts:\n" + "\n".join(f"- {f}" for f in research.key_facts) + "\n\n"
        "Trends:\n" + "\n".join(f"- {t}" for t in research.trends) + "\n\n"
        "Gaps:\n" + "\n".join(f"- {g}" for g in research.gaps)
    )
    brief = create_writer(llm).invoke(writer_input)

    return {
        "refined_question": refined_question,
        "research": research,
        "brief": brief,
    }
