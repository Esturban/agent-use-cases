from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .schema import ResearchFindings, WrittenBrief

RESEARCHER_SYSTEM = SystemMessage(
    """You are a research analyst. Given a topic, gather what you know and produce structured findings.

Be factual and specific. Prefer concrete data points over vague generalizations.
If you are uncertain about a fact, flag it in gaps rather than stating it as fact.
Do not invent statistics."""
)

WRITER_SYSTEM = SystemMessage(
    """You are a business writer who turns research findings into clear, executive-level briefs.

Style:
- Lead with the most important insight
- Use plain English — no jargon
- Structure: executive summary → context → key findings → implications → takeaways
- Markdown formatting with ## headers
- Do not repeat verbatim content from the findings; synthesize and add framing"""
)

SUPERVISOR_SYSTEM = SystemMessage(
    """You are a research supervisor. You receive a topic and decide how to frame
the research question for the researcher sub-agent.

Turn vague topics into focused, answerable research questions.
Example: "AI in healthcare" → "What are the current applications and adoption barriers of AI in clinical diagnosis?"
Return only the refined research question — one sentence."""
)


def run(topic: str) -> dict:
    """
    Supervisor → Researcher → Writer pipeline.

    Returns:
        {
            "refined_question": str,
            "research": ResearchFindings,
            "brief": WrittenBrief
        }
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Stage 1: Supervisor refines the question
    supervisor = SUPERVISOR_SYSTEM | llm
    refined = supervisor.invoke(HumanMessage(content=f"Topic: {topic}"))
    refined_question = refined.content.strip()

    # Stage 2: Researcher gathers findings
    researcher = RESEARCHER_SYSTEM | llm.with_structured_output(ResearchFindings)
    research: ResearchFindings = researcher.invoke(
        f"Research question: {refined_question}"
    )

    # Stage 3: Writer turns findings into a brief
    writer_input = (
        f"Research question: {refined_question}\n\n"
        f"Key facts:\n" + "\n".join(f"- {f}" for f in research.key_facts) + "\n\n"
        "Trends:\n" + "\n".join(f"- {t}" for t in research.trends) + "\n\n"
        "Gaps:\n" + "\n".join(f"- {g}" for g in research.gaps)
    )
    writer = WRITER_SYSTEM | llm.with_structured_output(WrittenBrief)
    brief: WrittenBrief = writer.invoke(writer_input)

    return {
        "refined_question": refined_question,
        "research": research,
        "brief": brief,
    }
