from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

TOPICS = [
    "Should a mid-market B2B SaaS company prioritise EMEA expansion or double down on the US market?",
    "What is the best pricing strategy for a bootstrapped AI developer tools company entering an enterprise market?",
]


def main() -> None:
    for topic in TOPICS:
        print(f"\n{'=' * 60}")
        print(f"Topic: {topic}")
        print("=" * 60)
        consensus = run(topic)

        print(f"\nModels queried ({len(consensus.opinions)}):")
        for opinion in consensus.opinions:
            print(f"\n  [{opinion.model}] confidence={opinion.confidence}")
            print(f"  Recommendation: {opinion.recommendation}")
            if opinion.key_risks:
                print(f"  Risks: {' | '.join(opinion.key_risks)}")
            if opinion.key_opportunities:
                print(f"  Opportunities: {' | '.join(opinion.key_opportunities)}")

        if consensus.points_of_agreement:
            print("\nPoints of agreement:")
            for point in consensus.points_of_agreement:
                print(f"  + {point}")

        if consensus.points_of_disagreement:
            print("\nPoints of disagreement:")
            for point in consensus.points_of_disagreement:
                print(f"  ! {point}")

        print(f"\nConsolidated recommendation:\n  {consensus.synthesised_recommendation}")


if __name__ == "__main__":
    main()
