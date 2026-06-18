"""
Client intel -- multi-source intelligence brief.

A LangGraph ReAct agent pulls signals from four mock sources
(news, filings, leadership, market) then structures a typed
ClientIntelBrief for account team use.
"""
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from .schema import ClientIntelBrief

_SYSTEM = SystemMessage(
    """You are a client intelligence analyst. Use the research tools to gather
signals on the target company from multiple sources, then summarise all
findings in a single comprehensive brief.

Steps:
1. Call search_news for recent press coverage.
2. Call search_regulatory_filings for any regulatory activity.
3. Call search_leadership_changes for executive moves.
4. Call search_market_signals for strategic intent signals.
5. Summarise all findings in plain English."""
)

_NEWS: dict[str, str] = {
    "acme corp": (
        "Acme Corp raised a $120M Series C led by Tiger Global in Q1 2024. "
        "The company also announced a strategic partnership with Microsoft Azure."
    ),
    "beta industries": (
        "Beta Industries announced a $300M debt facility in Q4 2023. "
        "Revenue grew 28% YoY per their investor day presentation."
    ),
}

_FILINGS: dict[str, str] = {
    "acme corp": "Acme Corp is under FTC scrutiny for potential antitrust issues related to its 2023 acquisition of Streamline Inc.",
    "beta industries": "Beta Industries disclosed material climate-related reporting obligations under new SEC rules effective 2025.",
}

_LEADERSHIP: dict[str, str] = {
    "acme corp": "CFO Sarah Lin departed in March 2024. New CFO David Park hired from Goldman Sachs, effective May 2024.",
    "beta industries": "CTO Michael Chen promoted to Chief AI Officer, a newly created role, in January 2024.",
}

_MARKET: dict[str, str] = {
    "acme corp": "Acme Corp publicly stated intent to expand into the APAC market by end of 2024 and is hiring aggressively in Singapore.",
    "beta industries": "Beta Industries filed three patents in Q1 2024 related to autonomous logistics, signalling an AI-first product pivot.",
}


@tool
def search_news(company: str) -> str:
    """Search recent press coverage for a company."""
    return _NEWS.get(company.lower(), f"No significant recent news found for {company}.")


@tool
def search_regulatory_filings(company: str) -> str:
    """Search regulatory filings and compliance actions for a company."""
    return _FILINGS.get(company.lower(), f"No material regulatory filings found for {company}.")


@tool
def search_leadership_changes(company: str) -> str:
    """Search for recent executive and senior leadership changes."""
    return _LEADERSHIP.get(company.lower(), f"No recent leadership changes found for {company}.")


@tool
def search_market_signals(company: str) -> str:
    """Search for strategic signals: patents, partnerships, geographic expansion, product shifts."""
    return _MARKET.get(company.lower(), f"No significant market signals found for {company}.")


def run(company: str) -> ClientIntelBrief:
    """Build a structured intelligence brief for the given company."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [search_news, search_regulatory_filings, search_leadership_changes, search_market_signals]
    agent = create_react_agent(llm, tools, prompt=_SYSTEM)

    result = agent.invoke({"messages": [{"role": "user", "content": f"Build an intelligence brief for: {company}"}]})
    last = result["messages"][-1].content

    structured_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(ClientIntelBrief)
    return structured_llm.invoke(
        f"Convert the following intelligence findings into a ClientIntelBrief object.\n\nCompany: {company}\n\nFindings:\n{last}"
    )
