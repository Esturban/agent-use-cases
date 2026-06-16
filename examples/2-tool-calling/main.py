from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from src.workflow import create_workflow

load_dotenv()


def main():
    agent = create_workflow()
    inputs = {
        "messages": [
            SystemMessage("You are a text assistant. Use tools to answer. Never compute yourself."),
            HumanMessage("How many words are in 'the quick brown fox'? Also reverse the word 'hello'."),
        ]
    }
    for step in agent.stream(inputs, stream_mode="values"):
        step["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
