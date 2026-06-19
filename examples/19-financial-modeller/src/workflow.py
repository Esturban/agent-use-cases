from .agents import extract_assumptions
from .calculator import project
from .schema import FinancialModel


def run(brief: str) -> FinancialModel:
    """Build a 3-year financial model from an unstructured business brief."""
    return project(extract_assumptions(brief))
