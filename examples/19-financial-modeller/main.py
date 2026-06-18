from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

BRIEFS = [
    (
        "SaaS startup",
        """We're a B2B SaaS company launching in 2025. We expect $1.2M in year-1 ARR, growing 45% annually.
Infrastructure and hosting costs are roughly 25% of revenue. Our annual opex (sales, marketing, G&A)
will be $800K in year 1, growing 20% each year. We'll invest $150K in servers and equipment upfront,
with $40K in depreciation per year. We carry no debt. Tax rate is 25%.""",
    ),
    (
        "Manufacturing company",
        """We manufacture industrial components. Year 1 revenue is projected at $4.5M with 12% annual growth.
Material and production costs run at 55% of revenue. Fixed overheads (admin, facilities, sales) are $1.1M
in year 1, growing 8% per year. We need $600K in capital equipment upfront, depreciating $80K per year.
We've taken a $1.5M term loan at 6%, with annual debt service of $280K. Corporate tax rate is 28%.""",
    ),
]


def main() -> None:
    for label, brief in BRIEFS:
        print(f"\n{'=' * 60}")
        print(f"Business: {label}")
        print("=" * 60)
        model = run(brief)
        print(f"Viability: {'VIABLE' if model.is_viable else 'NOT VIABLE'} -- {model.viability_notes}")
        if model.dscr > 0:
            print(f"DSCR:      {model.dscr:.2f}x")
        print(f"\n{'Year':<6} {'Revenue':>12} {'EBITDA':>12} {'Net Income':>12} {'FCF':>12}")
        print("-" * 54)
        for p in model.projections:
            print(
                f"Y{p.year:<5} ${p.revenue:>11,.0f} ${p.ebitda:>11,.0f}"
                f" ${p.net_income:>11,.0f} ${p.fcf:>11,.0f}"
            )


if __name__ == "__main__":
    main()
