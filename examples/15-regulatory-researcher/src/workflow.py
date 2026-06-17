from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .schema import ComplianceSummary

RESEARCHER_SYSTEM = SystemMessage(
    """You are a regulatory compliance analyst specialising in extracting structured
compliance intelligence from regulatory texts.

Extract every obligation, deadline, and penalty from the regulation text provided.

CITATION RULE (mandatory):
  Every item in `obligations` and `penalties` MUST include the exact source_article
  (e.g. 'Article 5(1)(f)' or 'Section 12(3)'). If you cannot point to a specific
  article or section in the provided text, do not include the finding.
  Cite precisely; never paraphrase article numbers or invent references.

EXTRACTION RULES:
  - obligations  : what regulated parties must do (ongoing or one-off)
  - key_deadlines: combine article reference with the deadline text, e.g.
                   "Article 15(2): quarterly report within 30 days of quarter end"
  - penalties    : what happens when obligations are breached (cite source_article)
  - high_priority_gaps: what compliance teams most commonly overlook in practice

Do not speculate beyond what the text states."""
)


def run(regulation_text: str) -> ComplianceSummary:
    """
    Citation-grounded regulatory extractor: every obligation, deadline, and
    penalty in the output must cite its source article.

    Returns:
        ComplianceSummary with fully cited obligations, deadlines, and penalties
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    researcher = RESEARCHER_SYSTEM | llm.with_structured_output(ComplianceSummary)
    return researcher.invoke(
        HumanMessage(content="Regulation text to analyse:\n\n" + regulation_text)
    )
