from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .schema import ScreeningResult

SCREENER_SYSTEM = SystemMessage(
    """You are a senior M&A analyst at a private equity firm.

You are given a description of an acquirer's strategic criteria and a list of
acquisition targets. For EACH target, score it across three dimensions (0-10 each):

  - strategic_fit   : sector alignment, geography, business model match
  - financial_fit   : revenue size, EBITDA margin, growth vs. the stated rubric
  - operational_fit : integration complexity, management depth, cultural alignment

Threshold: a score below 5 on ANY dimension is a fail -- that target is screened out.

overall_score = strategic_fit + financial_fit + operational_fit  (max 30)

recommendation per target:
  - "proceed"  if overall_score >= 20 and no dimension below 5
  - "monitor"  if overall_score 14-19 and no dimension below 5
  - "pass"     if any dimension is below 5 OR overall_score < 14

Rank the shortlist by overall_score descending.
Set meets_threshold = True only when the dimension score >= 5.

Be precise and evidence-based. Quote the specific numbers from the brief."""
)


def run(screening_brief: str) -> ScreeningResult:
    """
    Single-call M&A screener: reads the acquirer brief and target list,
    returns a ScreeningResult with a ranked shortlist and screened-out names.

    Returns:
        ScreeningResult with shortlist ranked by overall_score descending
    """
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    screener = SCREENER_SYSTEM | llm.with_structured_output(ScreeningResult)
    return screener.invoke(
        HumanMessage(content="Screening brief and targets:\n\n" + screening_brief)
    )
