from langchain_core.tools import tool


@tool
def add(x: int, y: int) -> int:
    """Add two integers and return their sum."""
    return x + y


@tool
def multiply(x: int, y: int) -> int:
    """Multiply two integers and return their product."""
    return x * y
