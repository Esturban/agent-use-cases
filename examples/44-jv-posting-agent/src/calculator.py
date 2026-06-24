"""Deterministic balance validator."""


def check_balance(debits: list, credits: list, tolerance: float = 0.01) -> bool:
    """Return True when total debits and total credits are within tolerance."""
    return abs(sum(debits) - sum(credits)) <= tolerance
