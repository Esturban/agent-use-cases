import os

from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("Set OPENAI_API_KEY in .env")

SAMPLE_BRIEF = """
ACQUIRER: Apex Capital Partners

Apex Capital is a UK mid-market private equity firm seeking bolt-on acquisitions
for its existing B2B SaaS portfolio company. Screening criteria:

  - Sector       : B2B SaaS only (horizontal or vertical software)
  - Revenue      : GBP 10m - 50m ARR or recurring revenue
  - EBITDA margin: 15%+ (proof of unit economics)
  - Geography    : UK or EU (no US/APAC at this stage)
  - Integration  : Must be operable as a standalone bolt-on within 6 months

TARGETS FOR SCREENING:

1. FieldSense Ltd
   Geography: UK  |  Sector: Field service management SaaS
   Revenue: GBP 18m  |  EBITDA margin: 22%  |  Growth: +31% YoY
   Notes: 85% recurring revenue, 120 NRR, ISO 27001 certified, 45 employees

2. LogiFlow GmbH
   Geography: Germany  |  Sector: Logistics route optimisation SaaS
   Revenue: GBP 12m  |  EBITDA margin: 8%  |  Growth: +18% YoY
   Notes: Strong product but high R&D burn, 60% of revenue from one customer

3. RetailAI Ltd
   Geography: UK  |  Sector: Retail demand forecasting tech
   Revenue: GBP 45m  |  EBITDA margin: -3%  |  Growth: +12% YoY
   Notes: Large revenue base but loss-making; heavy capex roadmap ahead

4. CloudOps Nordic AB
   Geography: Sweden  |  Sector: Cloud infrastructure management SaaS
   Revenue: GBP 22m  |  EBITDA margin: 19%  |  Growth: +24% YoY
   Notes: EU-domiciled, 92% recurring revenue, low churn (4% annual), 60 employees

5. DataBridge Inc
   Geography: USA  |  Sector: Enterprise data integration SaaS
   Revenue: GBP 35m  |  EBITDA margin: 24%  |  Growth: +28% YoY
   Notes: Excellent margins but US-incorporated with no EU entity; would require
          cross-border structure
"""

if __name__ == "__main__":
    result = run(SAMPLE_BRIEF)

    print("=" * 65)
    print(f"M&A SCREENING RESULT | Acquirer: {result.acquirer or 'Apex Capital'}")
    print("=" * 65)
    print(f"\nRubric: {result.rubric_summary}")
    print(f"\nTop-line: {result.recommendation}")

    print(f"\nSHORTLIST ({len(result.shortlist)} targets):")
    for t in result.shortlist:
        print(f"\n  [{t.overall_score}/30] {t.company_name} ({t.geography})")
        print(f"  Recommendation: {t.recommendation.upper()}")
        print(f"  Thesis: {t.investment_thesis}")
        print(
            f"  Scores -- Strategic: {t.strategic_fit.score}/10 "
            f"| Financial: {t.financial_fit.score}/10 "
            f"| Operational: {t.operational_fit.score}/10"
        )
        print(f"  Key risks: {', '.join(t.key_risks)}")
        print(f"  Next step: {t.suggested_next_step}")

    if result.screened_out:
        print(f"\nSCREENED OUT: {', '.join(result.screened_out)}")
