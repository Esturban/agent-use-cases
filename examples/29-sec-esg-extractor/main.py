from dotenv import load_dotenv

from src.workflow import analyse

load_dotenv()

COMPANIES = [
    ("MSFT", "Microsoft Corporation"),
    ("XOM", "Exxon Mobil Corporation"),
]


def main() -> None:
    for ticker, name in COMPANIES:
        print(f"\n{'=' * 60}")
        print(f"Analysing: {name} ({ticker})")
        print("=" * 60)

        report = analyse(ticker, company_name=name)

        print(f"\n{report.company} — {report.filing_year} 10-K")
        print(f"CSRD Coverage Score: {report.csrd_coverage_score}/100")
        print(f"Disclosures found: {len(report.disclosures)}")

        if report.strongest_areas:
            print(f"\nStrongest areas: {' | '.join(report.strongest_areas)}")

        if report.critical_gaps:
            print(f"Critical gaps:   {' | '.join(report.critical_gaps)}")

        if report.disclosures:
            print("\nDisclosures (top 5):")
            for d in report.disclosures[:5]:
                print(f"\n  [{d.completeness}] {d.category} — {d.topic}")
                print(f"  Section: {d.source_section}")
                preview = d.disclosure_text[:200].replace("\n", " ")
                print(f"  Text: {preview}...")
                if d.gaps:
                    print(f"  Gaps: {'; '.join(d.gaps[:2])}")

        print(f"\nAnalyst note:\n  {report.analyst_note}")


if __name__ == "__main__":
    main()
