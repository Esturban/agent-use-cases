import os

from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("Set OPENAI_API_KEY in .env")

SAMPLE_PROFILE = """
COMPANY: Meridian Logistics Ltd
Employees: 280  |  Revenue: GBP 42m  |  Sector: B2B logistics and freight

IDENTIFIED OPERATIONAL ISSUES:

1. Manual invoice processing
   - 12 FTE processing invoices manually across three regional offices
   - Average cycle time: 3 days per invoice (industry benchmark: 4 hours)
   - Error rate: 8% requiring rework, causing supplier disputes
   - Current cost: ~GBP 720k per annum in processing staff

2. SaaS subscription sprawl
   - 14 separate SaaS subscriptions with significant feature overlap
   - Estimated duplication: project management (3 tools), communication (4 tools)
   - No central procurement policy; department heads sign contracts independently
   - Annual spend: GBP 310k; estimated 40% redundancy

3. Warehouse shift scheduling in Excel
   - Shift scheduling done manually in Excel by 4 depot managers
   - 22% overtime premium above base because of poor demand forecasting
   - 2-3 hours per manager per week spent on scheduling adjustments
   - Overtime cost last year: GBP 890k (vs GBP 730k budgeted)

4. Legacy ERP integration middleware
   - 8-year-old ERP system requires custom middleware for every system integration
   - Each new integration costs GBP 35k-80k and takes 3-6 months
   - 3 integrations planned for next 18 months
   - Maintenance cost: GBP 120k per annum

5. Three CRM systems in sales team
   - Sales team of 22 uses 3 different CRMs (legacy fragmentation from acquisitions)
   - No single view of customer; data duplication and missed cross-sell
   - Estimated lost revenue from missed cross-sell: GBP 400k per annum

6. Manual HR onboarding
   - No automated onboarding workflow; HR team takes average 2 weeks per hire
   - 45 hires per year; total HR onboarding burden: ~90 person-weeks
   - New starter productivity delayed by average 3 days due to access provisioning

7. Print-based approval workflows in finance
   - Purchase orders, expense claims, and supplier approvals all require printed
     sign-off; documents physically routed between offices
   - Approvals take 4-7 days; creates cash flow uncertainty
   - Printer/paper/postage cost: GBP 18k per annum (minor but visible)
"""

if __name__ == "__main__":
    report = run(SAMPLE_PROFILE)

    company = report.company or "Meridian Logistics Ltd"
    print("=" * 65)
    print(f"COST OPTIMIZATION REPORT | {company}")
    print("=" * 65)
    print(f"\n{report.executive_summary}")

    if report.total_addressable_saving:
        print(f"\nTotal addressable saving: {report.total_addressable_saving}")

    def print_recs(label: str, recs: list) -> None:
        if not recs:
            return
        print(f"\n{label} ({len(recs)}):")
        for r in recs:
            saving = f" | Saving: {r.estimated_annual_saving}" if r.estimated_annual_saving else ""
            print(f"\n  [{r.effort.upper()} effort / {r.impact.upper()} impact]{saving}")
            print(f"  {r.title} [{r.category}]")
            print(f"  {r.rationale}")
            print("  Steps:")
            for step in r.implementation_steps:
                print(f"    - {step}")

    print_recs("QUICK WINS", report.quick_wins)
    print_recs("MAJOR PROJECTS", report.major_projects)
    print_recs("FILL-INS", report.fill_ins)
    print_recs("THANKLESS TASKS (avoid)", report.thankless_tasks)

    print(f"\nPRIORITIZATION: {report.prioritization_note}")
