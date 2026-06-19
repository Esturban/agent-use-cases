from langchain_openai import ChatOpenAI

from .prompts import EXTRACTOR_SYSTEM
from .schema import FinancialAssumptions


def extract_assumptions(brief: str) -> FinancialAssumptions:
    """Extract structured financial assumptions from an unstructured business brief."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = EXTRACTOR_SYSTEM | llm.with_structured_output(FinancialAssumptions)
    return chain.invoke(brief)
