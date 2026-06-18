"""
Knowledge management -- retrieval-augmented generation.

Step 1: LLM-as-retriever selects relevant documents from the corpus.
Step 2: LLM synthesises a KnowledgeBrief that cites the selected precedents.

No vector database. The LLM reads the corpus index and picks the most
relevant docs -- good enough for small-to-medium corpora.
"""
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from .schema import KnowledgeBrief, Precedent

CORPUS: list[dict[str, str]] = [
    {
        "id": "DOC-001",
        "title": "EMEA SaaS Go-to-Market Playbook (2022)",
        "summary": (
            "Covers channel strategy, pricing localisation, and regulatory considerations "
            "for B2B SaaS expansion across the UK, Germany, and France. Key finding: "
            "partner-led motion outperformed direct sales in mid-market segment by 2.4x."
        ),
    },
    {
        "id": "DOC-002",
        "title": "FinTech Regulatory Compliance Engagement (2023)",
        "summary": (
            "Assessment of PSD2 and GDPR obligations for a payment processing client. "
            "Produced a gap analysis, remediation roadmap, and data flow mapping. "
            "Timeline: 14 weeks from scoping to final report."
        ),
    },
    {
        "id": "DOC-003",
        "title": "Manufacturing Digital Transformation -- Phase 1 Close-out (2023)",
        "summary": (
            "IoT sensor rollout across three production facilities. Lessons learned: "
            "change management was the critical path, not technology. Recommend a "
            "dedicated change champion per site for any future phase."
        ),
    },
    {
        "id": "DOC-004",
        "title": "Investor Readiness Review -- Series B Candidate (2024)",
        "summary": (
            "Assessed a SaaS HR-tech company against typical Series B investor criteria. "
            "Key gaps: weak unit economics narrative, no clear path to profitability in "
            "18 months. Recommendations: restructure MRR/CAC/LTV story, prepare a "
            "financial bridge scenario."
        ),
    },
    {
        "id": "DOC-005",
        "title": "Strategic Sourcing Review -- Global Logistics Provider (2022)",
        "summary": (
            "Benchmark of procurement function across 12 categories. Identified "
            "$14M in savings opportunities. Recommended a category management operating "
            "model and supplier consolidation in packaging and freight."
        ),
    },
]

_INDEX = "\n".join(
    f'[{doc["id"]}] {doc["title"]}: {doc["summary"]}' for doc in CORPUS
)

_RETRIEVAL_SYSTEM = SystemMessage(
    f"""You are a knowledge retrieval specialist. Given a query, select the 2-4 most
relevant documents from the following corpus index.

For each selected document, return:
- source_id: the document ID (e.g. DOC-001)
- title: as listed
- excerpt: the most relevant sentence or phrase from the summary
- relevance_reason: one sentence explaining why this document is relevant to the query

Only select documents that genuinely address the query.

Corpus:
{_INDEX}

Return a KnowledgeBrief with an empty synthesis and empty gaps for now.
Set query to the user's query."""
)

_SYNTHESIS_SYSTEM = SystemMessage(
    """You are a senior knowledge management analyst. Given a query and a set of
retrieved precedents, synthesise a concise, structured response that:
1. Directly addresses the query.
2. Explicitly cites precedents by title when drawing on them.
3. Notes any gaps where the precedents do not cover the query.

Return a KnowledgeBrief object."""
)


def _retrieve(query: str) -> list[Precedent]:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    result: KnowledgeBrief = llm.with_structured_output(KnowledgeBrief).invoke(
        [
            _RETRIEVAL_SYSTEM,
            {"role": "user", "content": f"Query: {query}"},
        ]
    )
    return result.precedents


def run(query: str) -> KnowledgeBrief:
    """Retrieve relevant precedents and synthesise a grounded knowledge brief."""
    precedents = _retrieve(query)

    precedent_text = "\n\n".join(
        f"[{p.source_id}] {p.title}\n{p.excerpt}\nRelevance: {p.relevance_reason}"
        for p in precedents
    ) or "No precedents retrieved."

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    brief: KnowledgeBrief = llm.with_structured_output(KnowledgeBrief).invoke(
        [
            _SYNTHESIS_SYSTEM,
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
