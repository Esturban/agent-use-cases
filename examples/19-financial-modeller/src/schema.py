from pydantic import BaseModel, Field


class FinancialAssumptions(BaseModel):
    revenue_y1: float = Field(description="Year 1 revenue in USD.")
    revenue_growth_rate: float = Field(description="Annual revenue growth rate as a decimal (0.15 = 15%).")
    cogs_pct: float = Field(description="Cost of goods sold as a fraction of revenue (0.40 = 40%).")
    opex_y1: float = Field(description="Year 1 operating expenses in USD, excluding COGS.")
    opex_growth_rate: float = Field(description="Annual opex growth rate as a decimal.")
    tax_rate: float = Field(description="Effective tax rate as a decimal. Applied to positive EBITDA only.")
    capex_y1: float = Field(description="Year 1 capital expenditure in USD.")
    depreciation_y1: float = Field(description="Year 1 depreciation in USD.")
    debt_service_annual: float = Field(
        description="Annual debt service in USD. Use 0.0 if no debt."
    )


class YearlyProjection(BaseModel):
    year: int = Field(description="Projection year (1, 2, or 3).")
    revenue: float = Field(description="Total revenue in USD.")
    cogs: float = Field(description="Cost of goods sold in USD.")
    gross_profit: float = Field(description="Revenue minus COGS.")
    opex: float = Field(description="Operating expenses in USD.")
    ebitda: float = Field(description="Earnings before interest, tax, depreciation, and amortisation.")
    tax: float = Field(description="Tax charge in USD. Zero if EBITDA is negative.")
    net_income: float = Field(description="EBITDA minus tax.")
    fcf: float = Field(description="Free cash flow: EBITDA - tax - capex + depreciation.")


class FinancialModel(BaseModel):
    assumptions: FinancialAssumptions = Field(description="Assumptions extracted from the business brief.")
    projections: list[YearlyProjection] = Field(description="3-year P&L and cash flow projections.")
    dscr: float = Field(
        description="Debt service coverage ratio: average EBITDA / annual debt service. 0.0 if no debt."
    )
    is_viable: bool = Field(
        description="True if net income positive by year 3 and FCF positive by year 2."
    )
    viability_notes: str = Field(description="Plain-English summary of viability assessment.")
