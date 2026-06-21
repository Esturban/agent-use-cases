"""
Supplier Risk Scorer -- geopolitical risk from real World Bank data, no API key.

Step 1: Resolve each supplier's country to an ISO alpha-3 code.
Step 2: Fetch World Bank Worldwide Governance Indicators (WGI) for each country.
Step 3: LLM converts raw WGI scores into a composite risk score, tier, and mitigation action.
"""
import json
import os

from openai import OpenAI

from .schema import SupplierRiskRegister
from .wb_client import fetch_data_year, fetch_wgi, resolve_country_code

_SCORING_SYSTEM = (
    "You are a supply chain risk analyst. Given World Bank Worldwide Governance Indicators (WGI) "
    "for a set of countries, produce a supplier risk register:\n"
    "- Convert WGI scores (range -2.5 to +2.5) into a composite geopolitical_risk_score 0-100\n"
    "  (lower WGI scores = higher risk; a score of -2.5 maps to ~90-100 risk, +2.5 maps to ~5-10)\n"
    "- Assign risk_tier: LOW (0-25), MEDIUM (26-50), HIGH (51-75), CRITICAL (76-100)\n"
    "- List up to 3 key_risks specific to the country's governance profile\n"
    "- Suggest one concrete mitigation action matching the risk tier\n"
    "- Sort all suppliers by risk score descending\n"
    "- Write a 2-3 sentence portfolio_summary naming the highest-risk suppliers and priority action\n"
    "Use only the WGI data provided. Country-specific knowledge about current events may supplement."
)


def score(suppliers: list[tuple[str, str]]) -> SupplierRiskRegister:
    """
    Score a list of suppliers by geopolitical risk using World Bank governance data.

    Args:
        suppliers: List of (supplier_name, country) tuples.

    Returns:
        SupplierRiskRegister with ranked risk assessments and portfolio summary.
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    supplier_data: list[dict] = []
    for name, country in suppliers:
        code = resolve_country_code(country)
        scores = fetch_wgi(code)
        data_year = fetch_data_year(code)
        supplier_data.append({
            "supplier": name,
            "country": country,
            "country_code": code,
            "governance_indicators": {**scores, "data_year": data_year},
        })

    user_content = (
        f"Suppliers to assess: {len(suppliers)}\n\n"
        f"Supplier governance data:\n{json.dumps(supplier_data, indent=2)}"
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": _SCORING_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        response_format=SupplierRiskRegister,
    )
    register: SupplierRiskRegister = completion.choices[0].message.parsed
    register.suppliers_assessed = len(suppliers)
    return register
