"""
Financial modeller -- two-step pipeline.

Step 1: LLM extracts FinancialAssumptions from an unstructured business brief.
Step 2: Deterministic Python computes the 3-year P&L, FCF, DSCR, and viability.
"""
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from .schema import FinancialAssumptions, FinancialModel, YearlyProjection

_EXTRACTOR = SystemMessage(
    """You are a financial analyst. Extract financial assumptions from the business brief.

Rules:
- All rates as decimals: 15% -> 0.15, 40% -> 0.40
- All monetary amounts in USD as floats
- If a value is not stated, estimate based on the business type described
- debt_service_annual: use 0.0 if no debt is mentioned"""
)


def _extract(brief: str) -> FinancialAssumptions:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = _EXTRACTOR | llm.with_structured_output(FinancialAssumptions)
    return chain.invoke(brief)


def _project(a: FinancialAssumptions) -> FinancialModel:
    projections: list[YearlyProjection] = []
    capex = a.capex_y1
    dep = a.depreciation_y1

    for yr in range(1, 4):
        revenue = a.revenue_y1 * (1 + a.revenue_growth_rate) ** (yr - 1)
        cogs = revenue * a.cogs_pct
        gross_profit = revenue - cogs
        opex = a.opex_y1 * (1 + a.opex_growth_rate) ** (yr - 1)
        ebitda = gross_profit - opex
        tax = max(0.0, ebitda * a.tax_rate)
        net_income = ebitda - tax
        fcf = ebitda - tax - capex + dep

        projections.append(
            YearlyProjection(
                year=yr,
                revenue=round(revenue, 2),
                cogs=round(cogs, 2),
                gross_profit=round(gross_profit, 2),
                opex=round(opex, 2),
                ebitda=round(ebitda, 2),
                tax=round(tax, 2),
                net_income=round(net_income, 2),
                fcf=round(fcf, 2),
            )
        )
        capex *= 0.6
        dep *= 1.1

    avg_ebitda = sum(p.ebitda for p in projections) / 3
    dscr = round(avg_ebitda / a.debt_service_annual, 2) if a.debt_service_annual > 0 else 0.0

    y2, y3 = projections[1], projections[2]
    is_viable = y3.net_income > 0 and y2.fcf > 0

    concerns = []
    if y3.net_income <= 0:
        concerns.append("net income negative in year 3")
    if y2.fcf <= 0:
        concerns.append("FCF negative in year 2")
    if a.debt_service_annual > 0 and dscr < 1.25:
        concerns.append(f"DSCR {dscr:.2f}x below 1.25x minimum")

    return FinancialModel(
        assumptions=a,
        projections=projections,
        dscr=dscr,
        is_viable=is_viable,
        viability_notes="Viable" if is_viable else f"Concerns: {', '.join(concerns)}",
    )


def run(brief: str) -> FinancialModel:
    """Build a 3-year financial model from an unstructured business brief."""
    return _project(_extract(brief))
