import os

from openai import OpenAI

from .schema import EmailTriage


def create_client() -> OpenAI:
    """Return an OpenAI-compatible client pointed at OpenRouter."""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )


def classify(email_text: str, model: str = "openai/gpt-4o-mini") -> EmailTriage:
    """
    Classify an email using OpenRouter structured output.

    The model string is the only thing that changes between providers —
    swap it (e.g. "anthropic/claude-3-haiku", "mistralai/mistral-7b-instruct")
    and the rest of the code is identical.

    Args:
        email_text: Raw email content to classify.
        model: OpenRouter model identifier string.

    Returns:
        EmailTriage with urgency, category, summary, and recommended_action.
    """
    client = create_client()
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an email triage assistant. "
                    "Classify the email and recommend an action."
                ),
            },
            {"role": "user", "content": email_text},
        ],
        response_format=EmailTriage,
    )
    return completion.choices[0].message.parsed
