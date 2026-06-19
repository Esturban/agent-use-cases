import json

from langchain_core.tools import tool


@tool
def search_market_size(market: str) -> str:
    """Return estimated TAM (USD billions) and annual growth rate for a market."""
    data: dict[str, dict] = {
        "b2b saas europe": {"tam_usd_bn": 42.0, "growth_pct": 18.5},
        "industrial iot usa": {"tam_usd_bn": 31.0, "growth_pct": 22.3},
        "default": {"tam_usd_bn": 15.0, "growth_pct": 12.0},
    }
    result = data.get(market.lower(), data["default"])
    return json.dumps(result)


@tool
def search_competitors(market: str) -> str:
    """Return a list of top competitors with market share and positioning."""
    competitors: dict[str, list] = {
        "b2b saas europe": [
            {
                "name": "Salesforce",
                "share_pct": 19.0,
                "strengths": ["brand", "ecosystem"],
                "weaknesses": ["price", "complexity"],
            },
            {
                "name": "HubSpot",
                "share_pct": 11.0,
                "strengths": ["UX", "SMB focus"],
                "weaknesses": ["enterprise gaps"],
            },
            {
                "name": "Pipedrive",
                "share_pct": 5.0,
                "strengths": ["simplicity", "price"],
                "weaknesses": ["limited integrations"],
            },
        ],
        "industrial iot usa": [
            {
                "name": "Siemens MindSphere",
                "share_pct": 14.0,
                "strengths": ["OT expertise", "global reach"],
                "weaknesses": ["cost", "lock-in"],
            },
            {
                "name": "PTC ThingWorx",
                "share_pct": 10.0,
                "strengths": ["developer platform"],
                "weaknesses": ["steep learning curve"],
            },
            {
                "name": "Rockwell FactoryTalk",
                "share_pct": 9.0,
                "strengths": ["installed base"],
                "weaknesses": ["legacy architecture"],
            },
        ],
    }
    default = [{"name": "Incumbent A", "share_pct": 25.0, "strengths": ["scale"], "weaknesses": ["agility"]}]
    result = competitors.get(market.lower(), default)
    return json.dumps(result)


@tool
def search_regulations(market: str) -> str:
    """Return key regulatory considerations for a market and geography."""
    regs: dict[str, str] = {
        "b2b saas europe": (
            "GDPR data residency requirements; NIS2 cybersecurity obligations "
            "for critical sectors; VAT registration per country."
        ),
        "industrial iot usa": (
            "NIST cybersecurity framework compliance; potential FCC spectrum "
            "licensing; sector-specific OSHA safety obligations."
        ),
    }
    return regs.get(
        market.lower(),
        "Standard commercial regulations apply. No sector-specific blockers identified.",
    )
