from langchain_openai import ChatOpenAI

from .agents import extract_document, synthesise_findings
from .schema import DDReport


def run(documents: dict) -> DDReport:
    """
    Run commercial due diligence over multiple documents.

    Args:
        documents: Mapping of document_name -> document_text.

    Returns:
        DDReport with a unified risk register (severity x likelihood matrix),
        overall assessment, conditions, and further investigation areas.
    """
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    all_findings = [extract_document(llm, name, text) for name, text in documents.items()]
    return synthesise_findings(llm, all_findings)
