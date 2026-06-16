from typing import Literal

from langchain_openai import ChatOpenAI
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from .tools import reverse_text, word_count

TOOLS = [word_count, reverse_text]


def create_workflow():
    """Build a tool-calling agent using bind_tools and a manual routing graph."""
    llm = ChatOpenAI(model="gpt-5-nano").bind_tools(TOOLS)
    tool_node = ToolNode(TOOLS)

    def call_model(state: MessagesState):
        return {"messages": [llm.invoke(state["messages"])]}

    def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
        return "tools" if state["messages"][-1].tool_calls else END

    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")
    return graph.compile()
