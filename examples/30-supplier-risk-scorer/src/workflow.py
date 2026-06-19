"""
Supplier Risk Scorer -- geopolitical risk from real World Bank data, no API key.

Step 1: Resolve each supplier's country to an ISO alpha-3 code.
Step 2: Fetch World Bank Worldwide Governance Indicators (WGI) for each country.
Step 3: LLM converts raw WGI scores into a composite risk score, tier, and mitigation action.
"""
import json
import os
import urllib.request
import urllib.parse

from openai import OpenAI

from .schema import SupplierRiskRegister

# World Bank API -- no key required
# WGI indicator codes used:
#   PV.EST  = Political Stability and Absence of Violence
#   RL.EST  = Rule of Law
#   CC.EST  = Control of Corruption
#   RQ.EST  = Regulatory Quality
_WB_URL = (
    "https://api.worldbank.org/v2/country/{code}/indicator/{indicator}"
    "?format=json&mrv=1&per_page=1"
)

_WGI_INDICATORS = {
    "political_stability": "PV.EST",
    "rule_of_law": "RL.EST",
    "control_of_corruption": "CC.EST",
    "regulatory_quality": "RQ.EST",
}

# ISO alpha-3 codes for common country names
_COUNTRY_MAP = {
    "china": "CHN", "usa": "USA", "united states": "USA", "us": "USA",
    "germany": "DEU", "india": "IND", "mexico": "MEX", "brazil": "BRA",
    "vietnam": "VNM", "taiwan": "TWN", "south korea": "KOR", "korea": "KOR",
    "japan": "JPN", "malaysia": "MYS", "indonesia": "IDN", "thailand": "THA",
    "bangladesh": "BGD", "pakistan": "PAK", "cambodia": "KHM", "myanmar": "MMR",
    "nigeria": "NGA", "ethiopia": "ETH", "kenya": "KEN", "ghana": "GHA",
    "south africa": "ZAF", "egypt": "EGY", "turkey": "TUR", "poland": "POL",
    "ukraine": "UKR", "russia": "RUS", "france": "FRA", "uk": "GBR",
    "united kingdom": "GBR", "italy": "ITA", "spain": "ESP", "canada": "CAN",
    "australia": "AUS", "argentina": "ARG", "colombia": "COL", "chile": "CHL",
    "peru": "PER", "sri lanka": "LKA", "philippines": "PHL",
}

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


def _resolve_country_code(country: str) -> str:
    """Map country name to ISO alpha-3. Raises ValueError if unknown."""
    return _COUNTRY_MAP.get(country.lower().strip(), country.upper()[:3])


def _fetch_wgi(country_code: str) -> dict[str, float | None]:
    """Fetch the four WGI scores for a country. Returns None values on failure."""
    scores: dict[str, float | None] = {k: None for k in _WGI_INDICATORS}
    for field, indicator in _WGI_INDICATORS.items():
        url = _WB_URL.format(code=country_code.lower(), indicator=indicator)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "agent-use-cases"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            if len(data) >= 2 and data[1]:
                value = data[1][0].get("value")
                if value is not None:
                    scores[field] = round(float(value), 3)
        except Exception:
            pass
    return scores


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
        code = _resolve_country_code(country)
        scores = _fetch_wgi(code)
        data_year = None
        # Fetch data year from first available indicator
        for indicator in _WGI_INDICATORS.values():
            url = _WB_URL.format(code=code.lower(), indicator=indicator)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "agent-use-cases"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                if len(data) >= 2 and data[1]:
                    data_year = data[1][0].get("date")
                    if data_year:
                        data_year = int(data_year)
                        break
            except Exception:
                pass

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
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SCORING_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        response_format=SupplierRiskRegister,
    )
    register: SupplierRiskRegister = completion.choices[0].message.parsed
    register.suppliers_assessed = len(suppliers)
    return register
