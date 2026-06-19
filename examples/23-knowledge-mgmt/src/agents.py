from langchain_openai import ChatOpenAI

from .prompts import RETRIEVAL_SYSTEM, SYNTHESIS_SYSTEM
from .schema import KnowledgeBrief, Precedent


def retrieve_precedents(query: str) -> list[Precedent]:
    """Select the most relevant corpus documents for the given query."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    result: KnowledgeBrief = llm.with_structured_output(KnowledgeBrief).invoke(
        [RETRIEVAL_SYSTEM, {"role": "user", "content": f"Query: {query}"}]
    )
    return result.precedents


def synthesise_brief(query: str, precedents: list[Precedent]) -> KnowledgeBrief:
    """Synthesise retrieved precedents into a grounded KnowledgeBrief."""
    precedent_text = "\n\n".join(
        f"[{p.source_id}] {p.title}\n{p.excerpt}\nRelevance: {p.relevance_reason}"
        for p in precedents
    ) or "No precedents retrieved."

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    brief: KnowledgeBrief = llm.with_structured_output(KnowledgeBrief).invoke(
        [
            SYNTHESIS_SYSTEM,
            {
                "role": "user",
                "content": (
                    f"Query: {query}\n\n"
                    f"Precedents retrieved:\n{precedent_text}"
                ),
            },
        ]
    )
    brief.precedents = precedents
    return brief
