from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from .schema import DDReport, DocumentFindings

EXTRACTOR_SYSTEM = SystemMessage(
    """You are a due diligence analyst extracting structured findings from a single document.

Be specific and factual. Every key_finding must be a concrete, verifiable statement from
the document -- not an interpretation or inference. Every red_flag must cite specific
evidence. Do not repeat the same finding in both key_findings and red_flags."""
)

SYNTHESISER_SYSTEM = SystemMessage(
    """You are a senior M&A advisor synthesising multiple due diligence document reviews
into a unified risk register for a deal committee.

Your output must:
- Consolidate overlapping findings from different documents into single risk items
- Score each risk on BOTH severity (impact if it materialises) AND likelihood
- Source every risk item to the document(s) it came from
- Make a clear overall_assessment: proceed / proceed_with_conditions / do_not_proceed
- List only conditions and further_investigation items that are genuinely material

Do not pad the report with low-quality observations. Quality over quantity."""
)


def _extract(llm, doc_name: str, doc_text: str) -> DocumentFindings:
    extractor = EXTRACTOR_SYSTEM | llm.with_structured_output(DocumentFindings)
    return extractor.invoke(
        f"Document name: {doc_name}\n\nDocument text:\n{doc_text}"
    )


def _synthesise(llm, all_findings: list) -> DDReport:
    findings_text = "\n\n".join(
        "=== " + f.document_name + " (" + f.document_type + ") ===\n"
        "Key findings:\n" + "\n".join("- " + x for x in f.key_findings) + "\n"
        "Red flags:\n" + "\n".join("- " + x for x in f.red_flags) + "\n"
        "Questions raised:\n" + "\n".join("- " + x for x in f.questions_raised)
        for f in all_findings
    )
    synthesiser = SYNTHESISER_SYSTEM | llm.with_structured_output(DDReport)
    return synthesiser.invoke(
        "Synthesise the following per-document findings into a unified DD report:\n\n"
        + findings_text
    )


def run(documents: dict) -> DDReport:
    """
    Run commercial due diligence over multiple documents.

    Args:
        documents: Mapping of document_name -> document_text.

    Returns:
        DDReport with a unified risk register (severity x likelihood matrix),
        overall assessment, conditions, and further investigation areas.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    all_findings = [_extract(llm, name, text) for name, text in documents.items()]
    return _synthesise(llm, all_findings)
