from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from .schema import ContractReview

REVIEWER_SYSTEM = SystemMessage(
    """You are a senior commercial lawyer reviewing a contract on behalf of a client.

Your analysis must cover three areas:

1. RISK FINDINGS — every clause that creates risk for the client
   - You MUST include a clause_reference (section/clause number) for every finding
   - If you cannot point to a specific clause, do not include that finding
   - Quote or closely paraphrase the language that creates the risk
   - recommended_redline must be concrete proposed language, not vague advice like "negotiate this"

2. MISSING PROTECTIONS — standard clauses absent from this contract
   - Only flag protections that are genuinely standard for this contract type
   - Provide draft suggested_clause language the client can propose

3. NEGOTIATION POINTS — prioritised list of what to push for
   - must_have: deal-breakers; walk away if not addressed
   - should_have: important but not fatal
   - nice_to_have: improvements worth raising if the counterparty is cooperative

Be thorough but precise. A finding without a clause reference is worthless."""
)


def run(contract_text: str) -> ContractReview:
    """
    Review a contract and return a structured ContractReview.

    Args:
        contract_text: Full text of the contract to review.

    Returns:
        ContractReview with risk findings (each citing a clause), missing
        protections, and prioritised negotiation points.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    reviewer = REVIEWER_SYSTEM | llm.with_structured_output(ContractReview)
    return reviewer.invoke(f"CONTRACT TO REVIEW:\n\n{contract_text}")
