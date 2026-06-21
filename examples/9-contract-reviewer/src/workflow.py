from langchain_openai import ChatOpenAI

from .prompts import REVIEWER_SYSTEM
from .schema import ContractReview


def run(contract_text: str) -> ContractReview:
    """
    Review a contract and return a structured ContractReview.

    Args:
        contract_text: Full text of the contract to review.

    Returns:
        ContractReview with risk findings (each citing a clause), missing
        protections, and prioritised negotiation points.
    """
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    reviewer = REVIEWER_SYSTEM | llm.with_structured_output(ContractReview)
    return reviewer.invoke(f"CONTRACT TO REVIEW:\n\n{contract_text}")
