"""Policy configuration and helper functions for the Expense Audit Agent.

The POLICY dict is the single source of truth for all T&E limits.
Prompts and workflow reference POLICY directly — limits are never hardcoded
in prompt text.
"""

POLICY: dict = {
    "meal_limits": {
        "tier_1": {
            "cities": ["NYC", "SF", "London", "Tokyo", "Dubai"],
            "daily_limit": 120.0,
        },
        "tier_2": {
            "cities": ["Chicago", "LA", "Paris", "Singapore"],
            "daily_limit": 90.0,
        },
        "default": {
            "daily_limit": 60.0,
        },
    },
    "accommodation_limits": {
        "tier_1": {
            "cities": ["NYC", "SF", "London", "Tokyo", "Dubai"],
            "nightly": 350.0,
        },
        "tier_2": {
            "cities": ["Chicago", "LA", "Paris", "Singapore"],
            "nightly": 250.0,
        },
        "default": {
            "nightly": 180.0,
        },
    },
    "receipt_threshold": 25.0,
    "entertainment_limit": 200.0,
    "transport": {
        "requires_pre_approval": ["business", "first"],
    },
    "equipment_limit": 500.0,
}


def get_meal_limit(city: str | None) -> float:
    """Return the applicable daily meal limit for the given city.

    Args:
        city: City name to look up, or None for the default limit.

    Returns:
        Daily meal limit in the report currency.
    """
    if city is None:
        return POLICY["meal_limits"]["default"]["daily_limit"]
    city_upper = city.strip().upper()
    for tier in ("tier_1", "tier_2"):
        tier_cities = [c.upper() for c in POLICY["meal_limits"][tier]["cities"]]
        if city_upper in tier_cities:
            return POLICY["meal_limits"][tier]["daily_limit"]
    return POLICY["meal_limits"]["default"]["daily_limit"]


def get_accommodation_limit(city: str | None) -> float:
    """Return the applicable nightly accommodation limit for the given city.

    Args:
        city: City name to look up, or None for the default limit.

    Returns:
        Nightly accommodation limit in the report currency.
    """
    if city is None:
        return POLICY["accommodation_limits"]["default"]["nightly"]
    city_upper = city.strip().upper()
    for tier in ("tier_1", "tier_2"):
        tier_cities = [c.upper() for c in POLICY["accommodation_limits"][tier]["cities"]]
        if city_upper in tier_cities:
            return POLICY["accommodation_limits"][tier]["nightly"]
    return POLICY["accommodation_limits"]["default"]["nightly"]
