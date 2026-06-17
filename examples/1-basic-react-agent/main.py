from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.workflow import create_workflow

load_dotenv()

QUERIES = [
    "What is (3 + 4) multiplied by 5?",
    "Add 15 and 27, then multiply the result by 3.",
    (
        "A team of 7 earns 450 per person per month. "
        "3 of them receive a 120 bonus this month. "
        "What is the total monthly payroll?"
    ),
]


def main():
    agent = create_workflow()
    for query in QUERIES:
        print(f"\nQ: {query}")
        print("-" * 60)
        inputs = {"messages": [HumanMessage(query)]}
        for step in agent.stream(inputs, stream_mode="values"):
            step["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
