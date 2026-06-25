from langchain_openai import ChatOpenAI

from .schema import EmailTriage


def create_workflow():
    """Return a runnable that classifies an email into an EmailTriage result."""
    llm = ChatOpenAI(model="gpt-4.1-nano")
    return llm.with_structured_output(EmailTriage)
