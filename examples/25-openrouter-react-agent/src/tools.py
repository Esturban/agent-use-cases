from typing import Any

TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers together.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number."},
                    "b": {"type": "number", "description": "Second number."},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Multiply two numbers together.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number."},
                    "b": {"type": "number", "description": "Second number."},
                },
                "required": ["a", "b"],
            },
        },
    },
]

DISPATCH: dict[str, Any] = {
    "add": lambda a, b: a + b,
    "multiply": lambda a, b: a * b,
}
