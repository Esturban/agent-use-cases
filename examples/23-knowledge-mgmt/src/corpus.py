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

CORPUS_INDEX = "\n".join(
    f'[{doc["id"]}] {doc["title"]}: {doc["summary"]}' for doc in CORPUS
)
