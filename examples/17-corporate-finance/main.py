import os

from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("Set OPENAI_API_KEY in .env")

SAMPLE_BRIEF = """
COMPANY: Volt Energy Technologies Ltd

Business: B2B energy management SaaS platform for commercial and industrial sites.
Founded: 2019  |  HQ: Bristol, UK  |  Employees: 38

FINANCIAL PROFILE:
  ARR: GBP 8.2m  (+67% YoY)
  Gross margin: 74%
  Net revenue retention: 118%
  Burn rate: GBP 380k/month
  Runway: 14 months
  Last audited accounts: FY2022 (filed 4 months late; FY2023 and FY2024 unaudited)

TRANSACTION TARGET:
  Series B fundraise: GBP 15m
  Use of proceeds: product expansion + 12 new enterprise sales hires

GOVERNANCE:
  Directors: CEO (founder), CTO (co-founder), CFO (appointed 8 months ago)
  No independent non-executive directors
  No audit committee
  No formal board meeting cadence (ad hoc only)

LEGAL / IP:
  Core platform built 2019-2021 by 2 contractors (one based in India, one in Poland).
  Neither contractor has signed an IP assignment agreement.
  SaaS agreements with customers: standard template, last reviewed 2021.
  No material litigation or regulatory issues.

MARKET:
  210 customers (largest = 31% of ARR -- single logistics firm)
  Target market: UK commercial energy management (GBP 2.8bn addressable)
  Main competitors: 3 VC-backed players; Volt differentiates on AI-driven anomaly detection
  NRR 118%; churn <5% annually

NARRATIVE:
  Strong product-market fit signals (NRR, growth).
  No formal investor materials beyond a 12-slide pitch deck.
  No CFO investor relations experience.
  CEO has presented at 2 industry conferences; no public profile with institutional investors.
"""

if __name__ == "__main__":
    report = run(SAMPLE_BRIEF)

    GATE_ICON = {"pass": "PASS", "conditional": "COND", "fail": "FAIL"}

    company = report.company or "Volt Energy Technologies"
    print("=" * 65)
    print(f"READINESS REPORT | {company} | {report.transaction_type.upper()}")
    print("=" * 65)
    print(f"\nOverall status: {report.overall_status.upper()}")
    print(f"\n{report.executive_summary}")

    print("\nDIMENSION SCORECARD:")
    for d in report.dimensions:
        gate = GATE_ICON[d.gate]
        print(f"\n  [{gate}] {d.dimension.upper()} -- {d.score}/10")
        if d.strengths:
            print(f"  Strengths: {'; '.join(d.strengths)}")
        if d.blockers:
            print(f"  Blockers:  {'; '.join(d.blockers)}")
        if d.remediation:
            print("  Remediation:")
            for step in d.remediation:
                print(f"    - {step}")

    print(f"\nCRITICAL PATH ({len(report.critical_path)} actions):")
    for i, action in enumerate(report.critical_path, 1):
        print(f"  {i}. {action}")

    print(f"\nTime to ready: {report.estimated_time_to_ready}")

    if report.key_value_drivers:
        print("\nKEY VALUE DRIVERS:")
        for v in report.key_value_drivers:
            print(f"  + {v}")
