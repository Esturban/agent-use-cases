"""
PydanticAI invoice extractor.

PydanticAI is a schema-first agent framework: you declare the output type as a
Pydantic model and the framework handles the prompt construction, API call,
validation, and retry loop. Compare with example 3 (invoice-extractor) which
uses LangChain's with_structured_output() — same result, different entry point.

Key difference from LangChain:
  - LangChain: model.with_structured_output(Schema)  → runnable chain
  - PydanticAI: Agent(model, result_type=Schema)       → typed Agent object
"""
import os

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from .schema import Invoice


def create_agent(model_name: str = "gpt-4o-mini") -> Agent:
    """Build a PydanticAI Agent whose return type is Invoice."""
    model = OpenAIModel(model_name, api_key=os.environ["OPENAI_API_KEY"])
    return Agent(
        model,
        result_type=Invoice,
        system_prompt=(
            "You are an invoice parsing assistant. "
            "Extract all fields exactly as stated in the document. "
            "If a field is missing, use an empty string for text fields and 0.0 for numeric fields."
        ),
    )


def extract(invoice_text: str, model_name: str = "gpt-4o-mini") -> Invoice:
    """
    Extract structured invoice data from raw invoice text.

    Args:
        invoice_text: Raw text content of the invoice.
        model_name: OpenAI model identifier.

    Returns:
        Invoice with vendor, dates, totals, and line items.
    """
    agent = create_agent(model_name)
    result = agent.run_sync(f"Extract the invoice fields from the following:\n\n{invoice_text}")
    return result.data
