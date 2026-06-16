from langchain_core.tools import tool


@tool
def word_count(text: str) -> int:
    """Count the number of words in the given text."""
    return len(text.split())


@tool
def reverse_text(text: str) -> str:
    """Reverse the characters in the given text."""
    return text[::-1]
