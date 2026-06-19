"""
Example 42 -- Adaptive Investor Outreach

Runs two company scenarios through the full pipeline:
  - Scenario A: B2B SaaS at Series A, high-growth, ARR $2M at 80% YoY
  - Scenario B: Growth-stage industrial tech, PE-ready, EBITDA positive

Each scenario produces a validated OutreachPackage with:
  - A conservative 3-year financial projection
  - Tailored investor materials for VC, PE, and family_office personas
  - Key claims validated across 3 models via OpenRouter
  - A list of flagged (disputed) claims
"""
import json
import os

from dotenv import load_dotenv

from src.schema import CompanyBrief
from src.workflow import run

load_dotenv()

# ---------------------------------------------------------------------------
# Scenario A: B2B SaaS -- Series A
# ---------------------------------------------------------------------------

SCENARIO_A = CompanyBrief(
    company_name="ClearPath AI",
    sector="B2B SaaS",
    stage="series_a",
    arr_usd=2_000_000,
    growth_rate_pct=80.0,
    ebitda_margin_pct=-35.0,
    headcount=28,
    key_differentiator=(
        "Proprietary NLP layer trained on 10M+ support tickets enables "
        "90-second ticket resolution vs. industry average of 8 minutes; "
        "net revenue retention of 128% after 18 months live."
    ),
    use_of_funds="GTM expansion (AEs, SDRs), product engineering (AI roadmap), 18-month runway.",
)

# ---------------------------------------------------------------------------
# Scenario B: Industrial Tech -- Growth / PE-ready
# ---------------------------------------------------------------------------

SCENARIO_B = CompanyBrief(
    company_name="IronBridge Dynamics",
    sector="Industrial Tech",
    stage="growth",
    arr_usd=18_000_000,
    growth_rate_pct=32.0,
    ebitda_margin_pct=14.0,
    headcount=120,
    key_differentiator=(
        "Sensor-fusion platform for predictive maintenance in heavy manufacturing "
        "reduces unplanned downtime by 60%; 5-year contracts with top-10 auto OEMs "
        "provide highly visible, recurring revenue."
    ),
    use_of_funds="International expansion (EU & SE Asia), M&A pipeline for adjacent sensor data assets.",
)


def _print_package(package) -> None:
    """Print a concise summary of an OutreachPackage."""
    print(f"\n{'=' * 70}")
    print(f"OUTREACH PACKAGE: {package.company_name}")
    print(f"{'=' * 70}")

    proj = package.projection
    print("\n[Financial Projection]")
    print(f"  Year 1 ARR   : ${proj.year1_arr:>14,.0f}")
    print(f"  Year 2 ARR   : ${proj.year2_arr:>14,.0f}")
    print(f"  Year 3 ARR   : ${proj.year3_arr:>14,.0f}")
    print(f"  Year 3 EBITDA: ${proj.year3_ebitda:>14,.0f}")
    print(f"  Implied EV   : ${proj.implied_valuation_usd:>14,.0f}")
    print("  Assumptions:")
    for assumption in proj.key_assumptions:
        print(f"    - {assumption}")

    print("\n[Investor Materials]")
    for mat in package.materials:
        print(f"\n  -- {mat.persona.upper()} --")
        print(f"  Pitch angle : {mat.pitch_angle}")
        print(f"  Hook        : {mat.narrative_hook}")
        print(f"  Key metrics : {', '.join(mat.key_metrics_highlighted)}")
        print(f"  Risk framing: {mat.risk_framing}")
        print(f"  Ask         : {mat.ask_structure}")

    print("\n[Claim Validation]")
    for vc in package.validated_claims:
        status = "PASS" if vc.validated else "FLAG"
        print(f"\n  [{status}] {vc.claim}")
        print(f"  Dissenters: {vc.dissenting_count} / {len(vc.supporting_validations)}")
        for cv in vc.supporting_validations:
            print(f"    {cv.model_used:<45} {cv.verdict:<14} conf={cv.confidence:.2f}")

    if package.flagged_claims:
        print("\n[Flagged Claims -- 2+ models disputed]")
        for claim in package.flagged_claims:
            print(f"  ! {claim}")
    else:
        print("\n[No claims flagged -- all passed multi-model validation]")


def main() -> None:
    for env_var in ("OPENAI_API_KEY", "OPENROUTER_API_KEY"):
        if not os.environ.get(env_var):
            raise EnvironmentError(f"{env_var} is not set. Check your .env file.")

    scenarios = [SCENARIO_A, SCENARIO_B]
    for brief in scenarios:
        print(f"\nProcessing: {brief.company_name} ({brief.stage}, {brief.sector}) ...")
        package = run(brief)
        _print_package(package)

        out_path = f"{brief.company_name.lower().replace(' ', '_')}_outreach.json"
        with open(out_path, "w") as fh:
            json.dump(package.model_dump(), fh, indent=2)
        print(f"\n  Full package written to: {out_path}")


if __name__ == "__main__":
    main()
