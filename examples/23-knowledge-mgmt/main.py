from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

QUERIES = [
    "We're pitching a SaaS company on EMEA market expansion. What does our prior work say about go-to-market strategy in Europe?",
    "A manufacturing client wants to do an IoT pilot. What lessons from past engagements should we bring into the scoping conversation?",
]


def main() -> None:
    for query in QUERIES:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print("=" * 60)
        brief = run(query)

        print(f"\nPrecedents retrieved ({len(brief.precedents)}):")
        for p in brief.precedents:
            print(f"  [{p.source_id}] {p.title}")
            print(f"    Relevance: {p.relevance_reason}")

        print(f"\nSynthesis:\n{brief.synthesis}")

        if brief.gaps:
            print(f"\nGaps ({len(brief.gaps)}):")
            for g in brief.gaps:
                print(f"  - {g}")


if __name__ == "__main__":
    main()
