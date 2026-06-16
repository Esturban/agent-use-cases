from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.workflow import create_workflow

load_dotenv()


def main():
    agent = create_workflow()
    inputs = {"messages": [HumanMessage("What is (3 + 4) multiplied by 5?")]}
    for step in agent.stream(inputs, stream_mode="values"):
        step["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
