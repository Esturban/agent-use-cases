from langchain_openai import ChatOpenAI

from .prompts import EXTRACTOR_SYSTEM, SYNTHESISER_SYSTEM
from .schema import DDReport, DocumentFindings


def extract_document(llm: ChatOpenAI, doc_name: str, doc_text: str) -> DocumentFindings:
    """Extract structured findings from a single due diligence document."""
    extractor = EXTRACTOR_SYSTEM | llm.with_structured_output(DocumentFindings)
    return extractor.invoke(f"Document name: {doc_name}\n\nDocument text:\n{doc_text}")


def synthesise_findings(llm: ChatOpenAI, all_findings: list) -> DDReport:
    """Synthesise per-document findings into a unified DD risk register."""
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
