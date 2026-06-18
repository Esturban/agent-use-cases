from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

QUESTIONS = [
    "What is (3 + 4) * 5?",
    "What is 100 + (6 * 7)?",
    "If I have 12 items and each costs $8.50, what is the total cost?",
]


def main() -> None:
    for question in QUESTIONS:
        print(f"Q: {question}")
        answer, trace = run(question)
        for step in trace:
            if step.action == "final":
                print(f"  [step {step.step}] ANSWER → {step.input}")
            else:
                print(f"  [step {step.step}] {step.action}({step.input}) = {step.observation}")
        print(f"Final: {answer}")
        print()


if __name__ == "__main__":
    main()
