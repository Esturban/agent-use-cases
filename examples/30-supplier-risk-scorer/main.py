from dotenv import load_dotenv

from src.workflow import score

load_dotenv()

# Apparel manufacturer with suppliers across Southeast Asia and South Asia
APPAREL_SUPPLIERS = [
    ("Apex Textiles", "Bangladesh"),
    ("Golden Thread Co.", "Vietnam"),
    ("Sunrise Fabrics", "Myanmar"),
    ("Pacific Yarn Ltd.", "Taiwan"),
    ("Continental Mills", "Germany"),
]

# Electronics manufacturer with a China-heavy supply chain
ELECTRONICS_SUPPLIERS = [
    ("Shenzhen Components", "China"),
    ("Chennai Circuit Board", "India"),
    ("Kyoto Precision Parts", "Japan"),
    ("Manila Electronics", "Philippines"),
    ("Lagos Assembly Works", "Nigeria"),
]


def main() -> None:
    for label, suppliers in [
        ("Apparel manufacturer supply chain", APPAREL_SUPPLIERS),
        ("Electronics manufacturer supply chain", ELECTRONICS_SUPPLIERS),
    ]:
        print(f"\n{'=' * 60}")
        print(f"Scoring: {label}")
        print("=" * 60)

        register = score(suppliers)

        print(f"\nSuppliers assessed: {register.suppliers_assessed}")
        print(f"Critical: {register.critical_count}  |  High: {register.high_count}")

        print("\nRisk register (sorted by score):")
        for s in register.suppliers:
            gi = s.governance_indicators
            print(f"\n  [{s.risk_tier}] {s.supplier} — {s.country} ({s.country_code})")
            print(f"  Risk score: {s.geopolitical_risk_score}/100")
            if gi.political_stability is not None:
                print(
                    f"  WGI: stability={gi.political_stability:+.2f}  "
                    f"rule_of_law={gi.rule_of_law:+.2f}  "
                    f"corruption={gi.control_of_corruption:+.2f}"
                )
            if s.key_risks:
                print(f"  Key risks: {' | '.join(s.key_risks)}")
            print(f"  Mitigation: {s.mitigation}")

        print(f"\nPortfolio summary:\n  {register.portfolio_summary}")


if __name__ == "__main__":
    main()
