from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from .schema import DraftReply, TicketClassification

CLASSIFIER_PROMPT = SystemMessage(
    """You are a customer support ticket classifier.

Given a support ticket, classify it with:
- ticket_type: billing | technical | account | feature_request | other
- urgency:
    critical = service down, data loss, security issue
    high     = major feature broken, billing dispute
    medium   = degraded performance, billing question
    low      = general question, feature request
- team: the team best equipped to handle it
    billing          → billing/technical/account issues involving payment
    engineering      → bugs, outages, data issues
    account_management → account changes, upgrades, cancellations
    product          → feature requests, feedback
    general_support  → everything else
- confidence: your certainty 0.0–1.0
- reasoning: one sentence explaining your routing decision"""
)

DRAFT_PROMPTS = {
    "billing": SystemMessage(
        """You draft first-response emails for the billing support team.
Be empathetic, acknowledge the issue, and set a clear expectation for resolution time (1-2 business days for billing disputes).
Always include: acknowledgment, next steps, and a contact path if urgent.
Set escalate=True for any dispute over $500 or involving a subscription cancellation."""
    ),
    "engineering": SystemMessage(
        """You draft first-response emails for the engineering/technical support team.
Acknowledge the issue, ask for relevant details (OS, browser, steps to reproduce) if not provided.
Set escalate=True for any outage, data loss, or security concern."""
    ),
    "account_management": SystemMessage(
        """You draft first-response emails for the account management team.
Be warm and professional. For cancellation requests, acknowledge and offer a retention path.
Set escalate=True for enterprise accounts or churn risk."""
    ),
    "product": SystemMessage(
        """You draft first-response emails for the product team.
Thank the customer for feedback, confirm it's been logged, and set expectations (no commit to timelines).
escalate=False unless the feature request is blocking their use of the product."""
    ),
    "general_support": SystemMessage(
        """You draft first-response emails for general support.
Be helpful and concise. Aim to resolve in one reply where possible.
Set escalate=True only if the issue requires account access or billing changes."""
    ),
}

DRAFT_CONTEXT = """
You are replying to this customer support ticket:

Subject: {subject}
From: {customer_name} <{customer_email}>

---
{body}
---

Classification: {ticket_type} / {urgency} urgency → routed to {team}
"""


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
