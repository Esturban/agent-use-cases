from pydantic import BaseModel, Field


class GovernanceIndicators(BaseModel):
    political_stability: float | None = Field(
        description="World Bank Political Stability and Absence of Violence score (-2.5 to 2.5, higher is better)."
    )
    rule_of_law: float | None = Field(
        description="World Bank Rule of Law score (-2.5 to 2.5, higher is better)."
    )
    control_of_corruption: float | None = Field(
        description="World Bank Control of Corruption score (-2.5 to 2.5, higher is better)."
    )
    regulatory_quality: float | None = Field(
        description="World Bank Regulatory Quality score (-2.5 to 2.5, higher is better)."
    )
    data_year: int | None = Field(description="Year of the governance data used.")


class SupplierRisk(BaseModel):
    supplier: str = Field(description="Supplier name.")
    country: str = Field(description="Country of operations (as provided in the input).")
    country_code: str = Field(description="ISO 3166-1 alpha-3 country code used for World Bank API lookup.")
    governance_indicators: GovernanceIndicators = Field(description="Raw World Bank governance scores.")
    geopolitical_risk_score: int = Field(
        description=(
            "Composite geopolitical risk score from 0 (minimal) to 100 (extreme), "
            "derived from the governance indicators. Higher means higher risk."
        )
    )
    risk_tier: str = Field(
        description="Risk classification: LOW (0-25), MEDIUM (26-50), HIGH (51-75), or CRITICAL (76-100)."
    )
    key_risks: list[str] = Field(
        description="Up to 3 specific governance or geopolitical risk factors driving the score."
    )
    mitigation: str = Field(
        description="One concrete mitigation action appropriate for this risk tier."
    )


class SupplierRiskRegister(BaseModel):
    suppliers_assessed: int = Field(description="Total number of suppliers scored.")
    critical_count: int = Field(description="Suppliers rated CRITICAL.")
    high_count: int = Field(description="Suppliers rated HIGH.")
    suppliers: list[SupplierRisk] = Field(
        description="All supplier assessments, sorted by geopolitical_risk_score descending."
    )
    portfolio_summary: str = Field(
        description=(
            "2-3 sentence plain-English summary of the supplier portfolio's overall geopolitical exposure, "
            "the highest-risk suppliers to monitor, and the priority diversification action."
        )
    )
