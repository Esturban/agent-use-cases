from .agents import retrieve_precedents, synthesise_brief
from .schema import KnowledgeBrief


def run(query: str) -> KnowledgeBrief:
    """Retrieve relevant precedents and synthesise a grounded knowledge brief."""
    precedents = retrieve_precedents(query)
    return synthesise_brief(query, precedents)
