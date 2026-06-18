from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

MARKETS = [
    "B2B SaaS Europe",
    "Industrial IoT USA",
]


def main() -> None:
    for market in MARKETS:
        print(f"\n{'=' * 60}")
        print(f"Market: {market}")
        print("=" * 60)
        analysis = run(market)
        print(f"TAM:          ${analysis.market_size_usd_bn:.1f}B")
        print(f"Growth:       {analysis.growth_rate_pct:.1f}% / year")
        print(f"Verdict:      {analysis.entry_recommendation.upper()}")
        print(f"Rationale:    {analysis.rationale}")
        print(f"\nCompetitors ({len(analysis.competitors)}):")
        for c in analysis.competitors:
            print(f"  {c.name:<22} {c.estimated_market_share_pct:.0f}% share")
        print(f"\nOpportunities & Risks ({len(analysis.opportunities_and_risks)}):")
        for item in sorted(analysis.opportunities_and_risks, key=lambda x: -x.score):
            tag = "+" if item.category == "opportunity" else "-"
            print(f"  [{tag}] {item.score}/10  {item.description}")


if __name__ == "__main__":
    main()
