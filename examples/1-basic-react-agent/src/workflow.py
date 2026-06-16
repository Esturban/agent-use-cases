from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from .tools import add, multiply

SYSTEM_PROMPT = SystemMessage(
    "You are a math assistant. Solve problems using only the provided tools. "
    "Do not compute answers yourself."
)


def create_workflow():
    """Build a ReAct agent with the add and multiply tools."""
    llm = ChatOpenAI(model="gpt-5-nano")
    return create_react_agent(model=llm, prompt=SYSTEM_PROMPT, tools=[add, multiply])
