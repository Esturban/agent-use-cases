from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from .prompts import ANALYST_SYSTEM
from .schema import ClientIntelBrief
from .tools import (
    search_leadership_changes,
    search_market_signals,
    search_news,
    search_regulatory_filings,
)


def run(company: str) -> ClientIntelBrief:
    """Build a structured intelligence brief for the given company."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [search_news, search_regulatory_filings, search_leadership_changes, search_market_signals]
    agent = create_react_agent(llm, tools, prompt=ANALYST_SYSTEM)

    result = agent.invoke({"messages": [{"role": "user", "content": f"Build an intelligence brief for: {company}"}]})
    last = result["messages"][-1].content

    structured_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(ClientIntelBrief)
    return structured_llm.invoke(
        f"Convert the following intelligence findings into a ClientIntelBrief object.\n\nCompany: {company}\n\nFindings:\n{last}"
    )
