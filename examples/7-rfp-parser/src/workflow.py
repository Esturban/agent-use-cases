from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from .schema import RFPExtraction

SYSTEM_PROMPT = SystemMessage(
    """You are a procurement analyst who extracts structured data from government and enterprise RFPs.

Given RFP text, extract:
- title: official name of the RFP
- issuing_agency: who published it
- budget_ceiling: maximum contract value if mentioned (as a string, e.g. "$500,000")
- contract_duration: how long the contract runs if mentioned
- deadlines: all dates and milestones — label, date (YYYY-MM-DD if parseable), is_hard
- requirements: all requirements — assign each an ID (REQ-01, REQ-02...), categorize as
    technical | administrative | legal | financial, and flag mandatory vs preferred
- scoring_criteria: evaluation criteria with weight_percent if stated, and what evaluators look for
- summary: two sentences plain English on what is being procured

If a field is not mentioned in the RFP, use null (for optional fields) or an empty list.
For dates, convert to YYYY-MM-DD when possible. If the year is not stated, use the context year.
Extract ALL requirements and criteria, not just a sample."""
)


def create_parser():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return SYSTEM_PROMPT | llm.with_structured_output(RFPExtraction)


def parse(rfp_text: str) -> RFPExtraction:
    parser = create_parser()
    return parser.invoke(rfp_text)
