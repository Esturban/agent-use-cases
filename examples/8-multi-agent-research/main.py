from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

TOPIC = "The impact of AI agents on software development workflows"


def main():
    print(f"Topic: {TOPIC}\n")
    print("Running: Supervisor → Researcher → Writer...")
    print("-" * 60)

    result = run(TOPIC)

    print("\n[SUPERVISOR] Refined question:")
    print(f"  {result['refined_question']}\n")

    research = result["research"]
    print(f"[RESEARCHER] Findings on: {research.topic}")
    print(f"\n  Key facts ({len(research.key_facts)}):")
    for f in research.key_facts:
        print(f"    - {f}")
    print(f"\n  Trends ({len(research.trends)}):")
    for t in research.trends:
        print(f"    - {t}")
    print(f"\n  Gaps ({len(research.gaps)}):")
    for g in research.gaps:
        print(f"    - {g}")

    brief = result["brief"]
    print(f"\n[WRITER] Brief: {brief.title}")
    print(f"\n  Executive Summary:\n  {brief.executive_summary}\n")
    print("  Key Takeaways:")
    for kt in brief.key_takeaways:
        print(f"    * {kt}")
    print("\n  Further Reading:")
    for fr in brief.further_reading:
        print(f"    - {fr}")

    print("\n--- Full Brief ---\n")
    print(brief.body)


if __name__ == "__main__":
    main()
