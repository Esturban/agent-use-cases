import os

from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("Set OPENAI_API_KEY in .env")

SAMPLE_BOARD_PACK = """
NEXUS RETAIL GROUP PLC
BOARD OF DIRECTORS MEETING
12 March 2025 | 09:00 GMT

AGENDA
1. Minutes of previous meeting (approval)
2. CEO Update
3. Financial Performance (FY2024 results and Q1 2025 trading)
4. Proposed acquisition of FreshLocal Ltd
5. Audit & Risk Committee report
6. Any other business

---

ITEM 2: CEO UPDATE

Trading conditions in Q4 2024 were challenging across all formats. The digital
channel grew 22% year-on-year, now representing 31% of total revenue.

The leadership transition following Sarah Chen's resignation as CFO in January 2025
is progressing. An interim CFO, Mark Patel, was appointed on 3 February 2025.
The permanent search is ongoing. No further details are provided in this pack.

The Board is asked to note the update.

---

ITEM 3: FINANCIAL PERFORMANCE

FY2024 RESULTS (UNAUDITED)
Revenue:          GBP 2.41bn  (-3.2% vs FY2023)
Gross margin:     28.1%       (-1.4pp vs FY2023)
EBITDA:           GBP 89m     (-18% vs FY2023)
Net debt:         GBP 312m    (leverage: 3.5x EBITDA)
Interest cover:   2.1x        (covenant: 2.0x minimum)

Note: The FY2024 audit is not yet complete. Numbers are subject to change.

Q1 2025 TRADING (4 weeks to 28 February 2025)
Like-for-like sales: -1.8% vs prior year
Digital: +19%
Gross margin: no data provided for Q1 at time of pack preparation.

Dividend: Management proposes maintaining the full-year dividend of 12p per share.
The Board is asked to approve the dividend recommendation.

---

ITEM 4: PROPOSED ACQUISITION -- FRESHLOCAL LTD

Management proposes to acquire FreshLocal Ltd, a premium online grocery delivery
business, for a total consideration of GBP 95m (GBP 85m cash, GBP 10m deferred).

FreshLocal FY2024 financials:
Revenue:    GBP 38m
EBITDA:     GBP 2.1m  (margin: 5.5%)
Net assets: GBP 12m

The acquisition multiple is 45x EV/EBITDA. Management's rationale is strategic
acceleration of the digital channel. No integration plan is included in this pack.
No synergy case is quantified. No funding plan is provided.

The Board is asked to approve the acquisition in principle, subject to final
due diligence and financing terms to be confirmed.

---

ITEM 5: AUDIT & RISK COMMITTEE REPORT

The Audit Committee met on 28 February 2025. Key matters discussed:

External audit: KPMG has indicated a potential emphasis of matter paragraph in the
audit opinion relating to going concern assessment given current leverage levels.
Management is in discussion with KPMG. Further detail is not included in this pack.

Data breach: A cybersecurity incident in November 2024 resulted in the exposure
of approximately 180,000 customer payment records. The incident has been reported
to the ICO. A GBP 2.1m provision has been raised. Regulatory outcome pending.

Whistleblower report: One whistleblower report was received in Q4 2024 relating to
procurement practices. The matter is under investigation. No further detail provided.

The Board is asked to note the Audit Committee report.
"""

if __name__ == "__main__":
    briefing = run(SAMPLE_BOARD_PACK)

    SEV = {"critical": "CRIT", "high": "HIGH", "medium": "MED "}

    print("=" * 65)
    print(f"DIRECTOR BRIEFING | Pack quality: {briefing.overall_pack_quality.upper()}")
    print("=" * 65)
    print(f"\n{briefing.executive_assessment}")

    print(f"\nTOP RISKS ({len(briefing.top_risks)}):")
    for r in briefing.top_risks:
        print(f"\n  [{r.rank}] [{SEV[r.severity]}] [{r.area.upper()}] {r.title}")
        print(f"      Source: {r.source_section}")
        print(f"      {r.detail}")
        print(f"      Q: {r.suggested_question}")

    if briefing.information_gaps:
        print(f"\nINFORMATION GAPS ({len(briefing.information_gaps)}):")
        for g in briefing.information_gaps:
            print(f"\n  [{g.section}] {g.missing}")
            print(f"  Why it matters: {g.why_it_matters}")

    if briefing.decisions_required:
        print(f"\nDECISIONS REQUIRED ({len(briefing.decisions_required)}):")
        for d in briefing.decisions_required:
            print(f"\n  DECISION: {d.item}")
            print(f"  Context: {d.context}")
            if d.recommendation:
                print(f"  Management recommends: {d.recommendation}")
            print(f"  Key consideration: {d.key_consideration}")

    if briefing.questions_for_management:
        print("\nSUGGESTED QUESTIONS FOR MANAGEMENT:")
        for i, q in enumerate(briefing.questions_for_management, 1):
            print(f"  {i}. {q}")
