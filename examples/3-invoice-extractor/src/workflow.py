from langchain_openai import ChatOpenAI

from .schema import Invoice


def create_workflow():
    """Return a runnable that extracts a structured Invoice from raw text.

    with_structured_output forces the model to populate every Invoice field.
    If the response fails Pydantic validation (e.g. total_amount <= 0),
    the LangChain layer retries automatically.
    """
    llm = ChatOpenAI(model="gpt-4o-mini")
    return llm.with_structured_output(Invoice)
