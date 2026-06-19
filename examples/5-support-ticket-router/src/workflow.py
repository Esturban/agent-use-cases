from langchain_openai import ChatOpenAI

from .prompts import CLASSIFIER_PROMPT, DRAFT_CONTEXT, DRAFT_PROMPTS
from .schema import DraftReply, TicketClassification


def create_classifier():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return CLASSIFIER_PROMPT | llm.with_structured_output(TicketClassification)


def create_drafter(team: str):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    system = DRAFT_PROMPTS.get(team, DRAFT_PROMPTS["general_support"])
    return system | llm.with_structured_output(DraftReply)


def run(ticket: dict) -> dict:
    """
    ticket: {subject, body, customer_name, customer_email}
    returns: {classification, draft}
    """
    classifier = create_classifier()
    classification: TicketClassification = classifier.invoke(
        f"Subject: {ticket['subject']}\n\n{ticket['body']}"
    )

    context = DRAFT_CONTEXT.format(
        subject=ticket["subject"],
        customer_name=ticket["customer_name"],
        customer_email=ticket["customer_email"],
        body=ticket["body"],
        ticket_type=classification.ticket_type,
        urgency=classification.urgency,
        team=classification.team,
    )

    drafter = create_drafter(classification.team)
    draft: DraftReply = drafter.invoke(context)

    return {
        "classification": classification.model_dump(),
        "draft": draft.model_dump(),
    }
