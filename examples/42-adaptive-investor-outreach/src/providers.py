"""
Multi-model claim validation via OpenRouter.

Mirrors the fan-out pattern from example 27 (multi-provider-fan-out):
each model independently assesses whether a financial claim is defensible
given the stated projection assumptions.
"""
import os

from openai import OpenAI

from .prompts import VALIDATE_SYSTEM
from .schema import ClaimValidation

VALIDATION_MODELS = [
    "openai/gpt-4o-mini",
    "mistralai/mistral-7b-instruct",
    "meta-llama/llama-3.1-8b-instruct",
]


def _get_client() -> OpenAI:
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )


def validate_claim_with_model(
    claim: str,
    assumptions: list[str],
    model: str,
) -> ClaimValidation:
    """Ask a single model to validate one financial claim.

    Args:
        claim: The financial claim to assess (e.g. 'ARR grows from $2M to $8M').
        assumptions: The key modelling assumptions from the FinancialProjection.
        model: OpenRouter model string (e.g. 'openai/gpt-4o-mini').

    Returns:
        A ClaimValidation with verdict, confidence, and note from that model.
    """
    client = _get_client()
    assumptions_text = "\n".join(f"- {a}" for a in assumptions)
    user_message = (
        f"Claim to validate:\n{claim}\n\n"
        f"Modelling assumptions:\n{assumptions_text}"
    )
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": VALIDATE_SYSTEM},
            {"role": "user", "content": user_message},
        ],
        response_format=ClaimValidation,
    )
    result: ClaimValidation = completion.choices[0].message.parsed
    result.claim = claim
    result.model_used = model
    return result
