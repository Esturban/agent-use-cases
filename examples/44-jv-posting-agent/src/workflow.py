"""JV posting workflow."""

from langchain_openai import ChatOpenAI

from .calculator import check_balance
from .prompts import POSTING_PROMPT
from .schema import PostingRequest, PostingResult


def create_posting_agent():
    """Return a runnable chain that produces a structured PostingResult."""
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    return POSTING_PROMPT | llm.with_structured_output(PostingResult)


def run(request: PostingRequest) -> PostingResult:
    """Execute the posting agent and enforce debit=credit balance deterministically."""
    agent = create_posting_agent()
    result: PostingResult = agent.invoke(
        f"Event: {request.event_description}\n"
        f"Document type: {request.document_type}\n"
        f"Amount: ${request.amount:,.2f}\n"
        f"Period: {request.period}\n"
        f"Cost centre: {request.cost_centre or 'N/A'}"
    )
    debits = [line.amount for line in result.lines if line.side == "debit"]
    credits = [line.amount for line in result.lines if line.side == "credit"]
    balanced = check_balance(debits, credits)
    return PostingResult(
        lines=result.lines,
        is_balanced=balanced,
        total_debits=round(sum(debits), 2),
        total_credits=round(sum(credits), 2),
        posting_status="approved" if balanced else "rejected",
        rejection_reason=(
            None
            if balanced
            else f"Imbalance: debits ${sum(debits):,.2f} vs credits ${sum(credits):,.2f}"
        ),
    )
