"""
Pydantic models for the adaptive investor outreach example.

Covers company input, financial projections, per-persona materials,
and multi-model claim validation results.
"""
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

InvestorPersona = Literal["vc", "pe", "family_office"]


class CompanyBrief(BaseModel):
    company_name: str = Field(description="Legal or trading name of the company.")
    sector: str = Field(description="Industry sector (e.g. 'B2B SaaS', 'Industrial Tech').")
    stage: Literal["seed", "series_a", "series_b", "growth"] = Field(
        description="Current funding stage."
    )
    arr_usd: float = Field(description="Current annual recurring revenue in USD.")
    growth_rate_pct: float = Field(
        description="Trailing ARR growth rate as a percentage (e.g. 80.0 for 80%)."
    )
    ebitda_margin_pct: float = Field(
        description="Current EBITDA margin as a percentage; negative values indicate a loss."
    )
    headcount: int = Field(description="Total full-time employee count.")
    key_differentiator: str = Field(
        description="One to two sentences describing the primary competitive moat."
    )
    use_of_funds: str = Field(
        description="Intended use of the capital being raised (e.g. 'GTM expansion, R&D hiring')."
    )


# ---------------------------------------------------------------------------
# Financial projection
# ---------------------------------------------------------------------------


class FinancialProjection(BaseModel):
    year1_arr: float = Field(description="Projected ARR at end of Year 1 in USD.")
    year2_arr: float = Field(description="Projected ARR at end of Year 2 in USD.")
    year3_arr: float = Field(description="Projected ARR at end of Year 3 in USD.")
    year3_ebitda: float = Field(
        description="Projected EBITDA at end of Year 3 in USD (may be negative)."
    )
    implied_valuation_usd: float = Field(
        description="Implied enterprise valuation derived from Year 3 ARR or EBITDA multiples."
    )
    key_assumptions: list[str] = Field(
        description="3-6 modelling assumptions underpinning the projections. "
        "Flag high-uncertainty items with a '(!)' prefix."
    )


# ---------------------------------------------------------------------------
# Investor materials (per persona)
# ---------------------------------------------------------------------------


class InvestorMaterials(BaseModel):
    persona: InvestorPersona = Field(
        description="Target investor persona: vc, pe, or family_office."
    )
    pitch_angle: str = Field(
        description="One to two sentence framing of why this investment fits the persona's mandate."
    )
    key_metrics_highlighted: list[str] = Field(
        description="3-5 metrics most likely to resonate with this persona (e.g. NRR, EBITDA, IRR)."
    )
    narrative_hook: str = Field(
        description="Opening hook for the outreach -- tailored to the persona's language and priorities."
    )
    risk_framing: str = Field(
        description="How key risks should be presented to this audience to build trust rather than alarm."
    )
    ask_structure: str = Field(
        description="How to frame the raise (ticket size, instrument, timeline) for this persona."
    )


# ---------------------------------------------------------------------------
# Claim validation
# ---------------------------------------------------------------------------


class ClaimValidation(BaseModel):
    claim: str = Field(description="The exact financial claim being assessed.")
    model_used: str = Field(
        description="The model that produced this validation (e.g. openai/gpt-4o-mini)."
    )
    verdict: Literal["confirmed", "disputed", "inconclusive"] = Field(
        description="Whether the model considers the claim defensible given the stated assumptions."
    )
    confidence: float = Field(
        description="Model's self-assessed confidence from 0.0 (none) to 1.0 (certain)."
    )
    note: str = Field(
        description="Brief rationale for the verdict, including any caveats or flagged risks."
    )


class ValidatedClaim(BaseModel):
    claim: str = Field(description="The financial claim that was validated.")
    validated: bool = Field(
        description="True when fewer than 2 of the 3 validation models dispute the claim."
    )
    supporting_validations: list[ClaimValidation] = Field(
        description="One ClaimValidation entry per model queried."
    )
    dissenting_count: int = Field(
        description="Number of models that returned a 'disputed' verdict."
    )


# ---------------------------------------------------------------------------
# Final output
# ---------------------------------------------------------------------------


class OutreachPackage(BaseModel):
    company_name: str = Field(description="Name of the company this package was built for.")
    projection: FinancialProjection = Field(
        description="The 3-year financial projection underpinning all materials."
    )
    materials: list[InvestorMaterials] = Field(
        description="One InvestorMaterials object for each of the three personas."
    )
    validated_claims: list[ValidatedClaim] = Field(
        description="Each key financial claim with its multi-model validation result."
    )
    flagged_claims: list[str] = Field(
        description="Claims where 2 or more validation models returned a 'disputed' verdict."
    )
