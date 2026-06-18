from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

COMPANIES = [
    "Acme Corp",
    "Beta Industries",
]


def main() -> None:
    for company in COMPANIES:
        print(f"\n{'=' * 60}")
        print(f"Company: {company}")
        print("=" * 60)
        brief = run(company)

        if brief.funding_events:
            print("\nFunding:")
            for f in brief.funding_events:
                print(f"  {f.date}  {f.round_type}  ${f.amount_usd_m:.0f}M  ({f.lead_investor})")

        if brief.leadership_changes:
            print("\nLeadership:")
            for lc in brief.leadership_changes:
                print(f"  {lc.date}  {lc.role}  {lc.change_type}  -- {lc.name}")

        if brief.regulatory_exposures:
            print("\nRegulatory:")
            for r in brief.regulatory_exposures:
                print(f"  [{r.severity.upper()}] {r.topic}: {r.summary}")

        if brief.strategic_signals:
            print("\nStrategic Signals:")
            for s in brief.strategic_signals:
                print(f"  * {s.signal}")
                print(f"    -> {s.implication}")

        print("\nRecommended Actions:")
        for i, action in enumerate(brief.relationship_actions, 1):
            print(f"  {i}. {action}")


if __name__ == "__main__":
    main()
