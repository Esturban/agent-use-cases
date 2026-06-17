import os

from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("Set OPENAI_API_KEY in .env")

# Same Volt Energy Technologies brief from example 17, now used for fundraising
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

TRANSACTION:
  Seeking Series B: GBP 15m
  Use of proceeds: 12 new enterprise sales hires + product expansion into EU market

MARKET:
  210 customers (largest = 31% of ARR)
  Addressable market: UK commercial energy management GBP 2.8bn
  Differentiation: AI-driven anomaly detection; 3 VC-backed competitors
  NRR 118%; annual churn <5%

TEAM:
  CEO (founder, ex-energy sector 12 years)
  CTO (co-founder, ex-Google DeepMind)
  CFO (appointed 8 months ago, ex-Big 4)
  No independent board members yet
"""

if __name__ == "__main__":
    package = run(SAMPLE_BRIEF)

    company = package.company or "Volt Energy Technologies"
    print("=" * 65)
    print(f"FUNDRAISING PACKAGE | {company} | {package.round_type}")
    print("=" * 65)

    if package.universal_value_props:
        print("\nUNIVERSAL VALUE PROPS (resonate across all audiences):")
        for v in package.universal_value_props:
            print(f"  + {v}")

    def print_persona(label: str, mat: object) -> None:
        print(f"\n{'=' * 40}")
        print(f"FOR: {label}")
        print(f"{'=' * 40}")
        print(f"\nThesis: {mat.investor_thesis}")
        print("\nHeadline metrics:")
        for m in mat.headline_metrics:
            print(f"  - {m}")
        print(f"\nNarrative angle: {mat.narrative_angle}")
        print("\nKey asks:")
        for a in mat.key_asks:
            print(f"  - {a}")
        print("\nObjection responses:")
        for o in mat.objection_responses:
            print(f"  - {o}")
        print("\nSuggested materials (in order):")
        for s in mat.suggested_materials:
            print(f"  - {s}")

    print_persona("VENTURE CAPITAL", package.vc_materials)
    print_persona("PRIVATE EQUITY", package.pe_materials)
    print_persona("FAMILY OFFICE", package.family_office_materials)
