import os

from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("Set OPENAI_API_KEY in .env")

# Synthetic excerpt from the fictional "Digital Markets Conduct Regulation 2024"
SAMPLE_REGULATION = """
DIGITAL MARKETS CONDUCT REGULATION 2024 (DMCR 2024)
Jurisdiction: United Kingdom
In force: 1 January 2025

PART II: OBLIGATIONS ON DESIGNATED UNDERTAKINGS

Article 4 -- Data Portability
4(1) A designated undertaking shall provide end-users with the ability to export
their personal data and content in a commonly used, machine-readable format within
30 days of a written request.
4(2) The export mechanism must be made available continuously and must not
be subject to unreasonable technical barriers.

Article 7 -- Interoperability
7(1) A designated undertaking operating a core platform service shall ensure that
third-party services can interoperate with its platform on fair, reasonable, and
non-discriminatory (FRAND) terms.
7(2) The undertaking must publish interoperability technical specifications within
90 days of designation and keep them updated.

Article 11 -- Self-Preferencing Prohibition
11(1) A designated undertaking shall not rank its own products or services more
favourably than those of third parties in search results, listings, or
recommendations on its core platform service.
11(2) Ranking criteria must be transparent and applied consistently to all
third parties.

PART III: REPORTING OBLIGATIONS

Article 15 -- Periodic Reporting
15(1) A designated undertaking shall submit a compliance report to the Authority
on a quarterly basis.
15(2) Each quarterly report must be submitted within 30 days of the end of the
relevant quarter.
15(3) The report must include: (a) evidence of compliance with Articles 4, 7,
and 11; (b) details of any complaints received; (c) any changes to technical
specifications under Article 7(2).

PART V: ENFORCEMENT AND PENALTIES

Article 22 -- Financial Penalties
22(1) Where the Authority finds that a designated undertaking has breached any
obligation under this Regulation, it may impose a financial penalty not exceeding
10% of the undertaking's total worldwide annual turnover in the preceding
financial year.
22(2) In the case of a repeated infringement, the maximum financial penalty shall
be 20% of total worldwide annual turnover.

Article 23 -- Periodic Penalty Payments
23(1) To compel compliance, the Authority may impose a periodic penalty payment
not exceeding 5% of the average daily worldwide turnover of the designated
undertaking for each day of non-compliance, commencing from the date specified
in the Authority's decision.
"""

if __name__ == "__main__":
    result = run(SAMPLE_REGULATION)

    print("=" * 65)
    print(f"COMPLIANCE SUMMARY | {result.regulation_name}")
    print("=" * 65)
    print(f"Jurisdiction: {result.jurisdiction}")
    if result.in_force_date:
        print(f"In force: {result.in_force_date}")

    print(f"\nOBLIGATIONS ({len(result.obligations)}):")
    for o in result.obligations:
        ongoing = "ongoing" if o.is_ongoing else "one-off"
        print(f"\n  [{o.source_article}] ({ongoing}) {o.obligation}")
        print(f"  Applies to: {o.applies_to}")
        if o.deadline:
            print(f"  Deadline: {o.deadline}")

    print(f"\nKEY DEADLINES ({len(result.key_deadlines)}):")
    for d in result.key_deadlines:
        print(f"  - {d}")

    print(f"\nPENALTIES ({len(result.penalties)}):")
    for p in result.penalties:
        print(f"\n  [{p.source_article}] Trigger: {p.trigger}")
        if p.maximum_fine:
            print(f"  Max fine: {p.maximum_fine}")
        if p.other_consequences:
            print(f"  Other: {', '.join(p.other_consequences)}")

    if result.high_priority_gaps:
        print(f"\nHIGH-PRIORITY GAPS ({len(result.high_priority_gaps)}):")
        for g in result.high_priority_gaps:
            print(f"  - {g}")
