"""
Adaptive investor outreach workflow.

Orchestrates three parallel concerns:
  1. Financial modelling   -- build a conservative 3-year projection
  2. Persona generation    -- fan out InvestorMaterials for VC / PE / family_office
  3. Claim validation      -- fan out each key claim across 3 validation models

All LLM calls that can run in parallel do so via ThreadPoolExecutor.
"""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import get_args

from openai import OpenAI

from .prompts import MATERIALS_SYSTEM, PROJECTION_SYSTEM
from .providers import VALIDATION_MODELS, validate_claim_with_model
from .schema import (
    CompanyBrief,
    FinancialProjection,
    InvestorMaterials,
    InvestorPersona,
    OutreachPackage,
    ValidatedClaim,
)

_PERSONAS: list[InvestorPersona] = list(get_args(InvestorPersona))

_PRIMARY_MODEL = "gpt-4o-mini"


def _get_primary_client() -> OpenAI:
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


# ---------------------------------------------------------------------------
# Step 1: financial projection
# ---------------------------------------------------------------------------


def _build_projection(brief: CompanyBrief) -> FinancialProjection:
    """Generate a conservative 3-year financial projection from a company brief."""
    client = _get_primary_client()
    brief_text = (
        f"Company: {brief.company_name}\n"
        f"Sector: {brief.sector}\n"
        f"Stage: {brief.stage}\n"
        f"Current ARR: ${brief.arr_usd:,.0f}\n"
        f"Growth rate: {brief.growth_rate_pct}% YoY\n"
        f"EBITDA margin: {brief.ebitda_margin_pct}%\n"
        f"Headcount: {brief.headcount}\n"
        f"Key differentiator: {brief.key_differentiator}\n"
        f"Use of funds: {brief.use_of_funds}"
    )
    completion = client.beta.chat.completions.parse(
        model=_PRIMARY_MODEL,
        messages=[
            {"role": "system", "content": PROJECTION_SYSTEM},
            {"role": "user", "content": brief_text},
        ],
        response_format=FinancialProjection,
    )
    return completion.choices[0].message.parsed


# ---------------------------------------------------------------------------
# Step 2: per-persona investor materials
# ---------------------------------------------------------------------------


def _build_materials(
    brief: CompanyBrief,
    projection: FinancialProjection,
    persona: InvestorPersona,
) -> InvestorMaterials:
    """Generate investor materials tailored to a specific persona."""
    client = _get_primary_client()
    projection_text = (
        f"Year 1 ARR: ${projection.year1_arr:,.0f}\n"
        f"Year 2 ARR: ${projection.year2_arr:,.0f}\n"
        f"Year 3 ARR: ${projection.year3_arr:,.0f}\n"
        f"Year 3 EBITDA: ${projection.year3_ebitda:,.0f}\n"
        f"Implied valuation: ${projection.implied_valuation_usd:,.0f}\n"
        f"Key assumptions:\n" + "\n".join(f"  - {a}" for a in projection.key_assumptions)
    )
    user_message = (
        f"Company brief:\n{brief.model_dump_json(indent=2)}\n\n"
        f"3-year projection:\n{projection_text}\n\n"
        f"Target persona: {persona}"
    )
    completion = client.beta.chat.completions.parse(
        model=_PRIMARY_MODEL,
        messages=[
            {"role": "system", "content": MATERIALS_SYSTEM},
            {"role": "user", "content": user_message},
        ],
        response_format=InvestorMaterials,
    )
    result: InvestorMaterials = completion.choices[0].message.parsed
    result.persona = persona
    return result


# ---------------------------------------------------------------------------
# Step 3: claim extraction and multi-model validation
# ---------------------------------------------------------------------------


def _extract_key_claims(projection: FinancialProjection) -> list[str]:
    """Derive the 3-5 most important numeric claims from the projection."""
    return [
        f"ARR will reach ${projection.year1_arr:,.0f} by end of Year 1.",
        f"ARR will reach ${projection.year2_arr:,.0f} by end of Year 2.",
        f"ARR will reach ${projection.year3_arr:,.0f} by end of Year 3.",
        f"EBITDA will reach ${projection.year3_ebitda:,.0f} by Year 3.",
        f"The implied enterprise valuation is ${projection.implied_valuation_usd:,.0f}.",
    ]


def _validate_claim(claim: str, projection: FinancialProjection) -> ValidatedClaim:
    """Fan out claim validation across all VALIDATION_MODELS in parallel."""
    assumptions = projection.key_assumptions
    validations = []

    with ThreadPoolExecutor(max_workers=len(VALIDATION_MODELS)) as executor:
        futures = {
            executor.submit(validate_claim_with_model, claim, assumptions, model): model
            for model in VALIDATION_MODELS
        }
        for future in as_completed(futures):
            validations.append(future.result())

    validations.sort(key=lambda v: VALIDATION_MODELS.index(v.model_used))
    dissenting = sum(1 for v in validations if v.verdict == "disputed")
    return ValidatedClaim(
        claim=claim,
        validated=dissenting < 2,
        supporting_validations=validations,
        dissenting_count=dissenting,
    )


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def run(brief: CompanyBrief) -> OutreachPackage:
    """Build a complete investor outreach package for all three personas.

    Steps:
      1. Generate a 3-year financial projection (sequential -- all else depends on it).
      2. Fan out persona materials for VC, PE, and family_office in parallel.
      3. Extract key claims from the projection.
      4. Fan out claim validation across 3 models for each claim, in parallel.
      5. Flag claims where 2+ models returned 'disputed'.

    Args:
        brief: A CompanyBrief describing the company seeking investment.

    Returns:
        An OutreachPackage containing the projection, per-persona materials,
        validated claims, and a list of flagged (disputed) claims.
    """
    # Step 1: projection (must complete before steps 2-4)
    projection = _build_projection(brief)

    # Step 2: persona materials -- fan out across all personas in parallel
    materials: list[InvestorMaterials] = []
    with ThreadPoolExecutor(max_workers=len(_PERSONAS)) as executor:
        persona_futures = {
            executor.submit(_build_materials, brief, projection, persona): persona
            for persona in _PERSONAS
        }
        for future in as_completed(persona_futures):
            materials.append(future.result())

    materials.sort(key=lambda m: _PERSONAS.index(m.persona))

    # Step 3: extract claims
    claims = _extract_key_claims(projection)

    # Step 4: validate each claim (each internally fans out to 3 models)
    validated_claims: list[ValidatedClaim] = []
    with ThreadPoolExecutor(max_workers=len(claims)) as executor:
        claim_futures = {
            executor.submit(_validate_claim, claim, projection): claim
            for claim in claims
        }
        for future in as_completed(claim_futures):
            validated_claims.append(future.result())

    validated_claims.sort(key=lambda vc: claims.index(vc.claim))

    # Step 5: collect flagged claims
    flagged = [vc.claim for vc in validated_claims if vc.dissenting_count >= 2]

    return OutreachPackage(
        company_name=brief.company_name,
        projection=projection,
        materials=materials,
        validated_claims=validated_claims,
        flagged_claims=flagged,
    )
