import json
import urllib.request

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


def resolve_country_code(country: str) -> str:
    """Map country name to ISO alpha-3. Falls back to uppercased first 3 chars if unknown."""
    return _COUNTRY_MAP.get(country.lower().strip(), country.upper()[:3])


def fetch_wgi(country_code: str) -> dict[str, float | None]:
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


def fetch_data_year(country_code: str) -> int | None:
    """Return the most recent data year available for a country's WGI data."""
    for indicator in _WGI_INDICATORS.values():
        url = _WB_URL.format(code=country_code.lower(), indicator=indicator)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "agent-use-cases"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            if len(data) >= 2 and data[1]:
                year = data[1][0].get("date")
                if year:
                    return int(year)
        except Exception:
            pass
    return None
