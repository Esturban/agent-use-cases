from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from .prompts import CONSULTANT_SYSTEM
from .schema import MarketAnalysis
from .tools import search_competitors, search_market_size, search_regulations


def run(market: str) -> MarketAnalysis:
    """Run a structured market entry analysis for the given market description."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [search_market_size, search_competitors, search_regulations]
    agent = create_react_agent(llm, tools, prompt=CONSULTANT_SYSTEM)

    result = agent.invoke({"messages": [{"role": "user", "content": f"Analyse the market: {market}"}]})
    last = result["messages"][-1].content

    structured_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(MarketAnalysis)
    return structured_llm.invoke(
        f"Convert the following research findings into a MarketAnalysis object.\n\nFindings:\n{last}\n\nMarket: {market}"
    )
