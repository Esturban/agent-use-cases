"""Gradio demo: classify a support ticket and draft a first-response reply."""

import os
import sys

import gradio as gr

sys.path.insert(0, os.path.dirname(__file__))
from src.schema import DraftReply, TicketClassification  # noqa: E402

MODELS = [
    "openai/gpt-5.4-nano",
    "minimax/minimax-m3",
    "openai/gpt-4.1-nano",
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]

CLASSIFIER_SYSTEM = (
    "You are a customer support ticket classifier. Given a support ticket, classify:\n"
    "- ticket_type: billing | technical | account | feature_request | other\n"
    "- urgency: critical (service down/data loss/security) | high (major feature broken/billing dispute)"
    " | medium (degraded perf/billing question) | low (general question/feature request)\n"
    "- team: billing | engineering | account_management | product | general_support\n"
    "- confidence: 0.0-1.0\n"
    "- reasoning: one sentence explaining the routing decision"
)

DRAFTER_SYSTEMS = {
    "billing": (
        "Draft a first-response email for the billing support team. "
        "Empathetic, acknowledge issue, set 1-2 business day resolution expectation. "
        "Set escalate=True for disputes over $500 or subscription cancellations."
    ),
    "engineering": (
        "Draft a first-response email for the engineering/technical support team. "
        "Acknowledge issue, ask for relevant details if not provided. "
        "Set escalate=True for outages, data loss, or security."
    ),
    "account_management": (
        "Draft a first-response email for the account management team. "
        "Warm and professional. For cancellations, offer retention path. "
        "Set escalate=True for enterprise accounts."
    ),
    "product": (
        "Draft a first-response email for the product team. "
        "Thank customer, confirm feedback logged, no timeline commitments. "
        "escalate=False unless blocking."
    ),
    "general_support": (
        "Draft a first-response email for general support. "
        "Helpful and concise, aim to resolve in one reply. "
        "escalate=True only if account access or billing changes needed."
    ),
}

URGENCY_EMOJI = {
    "critical": "🔴 critical",
    "high": "🟠 high",
    "medium": "🟡 medium",
    "low": "🟢 low",
}

SAMPLES = [
    [
        "Charged twice this month - invoice #4821",
        "Sarah Chen",
        "schen@example.com",
        "I noticed my credit card was charged $99 twice on June 1st. Invoice #4821 shows a duplicate charge. Please refund ASAP.",
    ],
    [
        "Dashboard not loading - production down",
        "Marcus Torres",
        "m.torres@bigcorp.com",
        "Our entire team cannot access the dashboard since 9 AM EST. Getting 502 errors. We're on the Enterprise plan and this is costing us revenue.",
    ],
    [
        "API rate limits killing our integration",
        "Dev Team",
        "dev@acme-corp.com",
        "We're hitting 429s on the /events endpoint every few minutes even though we're well within the published limits. Started after yesterday's deploy.",
    ],
    [
        "How do I add team members?",
        "Priya Patel",
        "priya@startup.io",
        "I'm trying to invite my colleagues to our workspace but can't find the option in Settings.",
    ],
    [
        "Want to cancel — switching to competitor",
        "James Park",
        "jpark@bloomretail.com",
        "We've decided to go with a different vendor. Please cancel our annual subscription and process a prorated refund for the remaining months.",
    ],
]


def route_and_draft(subject: str, customer_name: str, customer_email: str, body: str, model: str):
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        err = "OPENROUTER_API_KEY is not set."
        return err, "", "", "", "", "", "", ""

    try:
        from openai import OpenAI

        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

        clf: TicketClassification = (
            client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {"role": "system", "content": CLASSIFIER_SYSTEM},
                    {
                        "role": "user",
                        "content": (
                            f"Subject: {subject}\nFrom: {customer_name} <{customer_email}>\n---\n{body}"
                        ),
                    },
                ],
                response_format=TicketClassification,
            )
            .choices[0]
            .message.parsed
        )

        draft_user_msg = (
            f"You are replying to this support ticket:\n"
            f"Subject: {subject}\n"
            f"From: {customer_name} <{customer_email}>\n"
            f"---\n{body}\n---\n"
            f"Classification: {clf.ticket_type} / {clf.urgency} urgency → routed to {clf.team}"
        )

        draft: DraftReply = (
            client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {"role": "system", "content": DRAFTER_SYSTEMS[clf.team]},
                    {"role": "user", "content": draft_user_msg},
                ],
                response_format=DraftReply,
            )
            .choices[0]
            .message.parsed
        )

    except Exception as exc:  # noqa: BLE001
        err = f"Error: {exc}"
        return err, "", "", "", "", "", "", ""

    urgency_display = URGENCY_EMOJI.get(clf.urgency, clf.urgency)
    confidence_display = f"{clf.confidence * 100:.0f}%"
    escalate_display = "⚠️ Yes — notify team lead" if draft.escalate else "No"

    return (
        urgency_display,
        clf.team.replace("_", " "),
        confidence_display,
        clf.reasoning,
        draft.subject,
        draft.body,
        draft.internal_note,
        escalate_display,
    )


with gr.Blocks(title="Support Ticket Router") as demo:
    gr.Markdown(
        "## 🎫 Support Ticket Router\n"
        "Paste a customer ticket → the model classifies it, routes it to the right team, "
        "and generates a ready-to-send first-response draft with an internal note.\n\n"
        "**Built for:** support ops teams replacing manual triage queues — "
        "two structured API calls replace a human deciding who to forward the email to."
    )

    with gr.Accordion("Routing logic & teams", open=True):
        gr.Markdown(
            "**Step 1 — Classify:** one API call identifies ticket type, urgency, and target team.\n"
            "**Step 2 — Draft:** a second API call, prompted specifically for that team, "
            "writes the first-response email and internal note.\n\n"
            "| Team | Handles | Escalates when |\n"
            "|------|---------|----------------|\n"
            "| **Billing** | Charges, invoices, refunds | Dispute >$500 or cancellation |\n"
            "| **Engineering** | Bugs, outages, API issues | Outage, data loss, or security |\n"
            "| **Account Management** | Retention, upgrades, enterprise | Enterprise account |\n"
            "| **Product** | Feature requests, feedback | Blocking issue |\n"
            "| **General Support** | How-to, onboarding | Access or billing change needed |\n\n"
            "**Urgency:** 🔴 critical · 🟠 high · 🟡 medium · 🟢 low"
        )

    with gr.Row():
        with gr.Column():
            subject_in = gr.Textbox(label="Subject")
            name_in = gr.Textbox(label="Customer name")
            email_in = gr.Textbox(label="Customer email")
            body_in = gr.Textbox(label="Ticket body", lines=6,
                                 placeholder="Paste the customer's message here…")
            model_in = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Route & Draft", variant="primary")
            gr.Examples(
                examples=SAMPLES,
                inputs=[subject_in, name_in, email_in, body_in],
                label="Sample tickets — click to load",
            )

        with gr.Column():
            gr.Markdown("#### Classification")
            urgency_out = gr.Textbox(label="Urgency", interactive=False)
            team_out = gr.Textbox(label="Routed to", interactive=False)
            confidence_out = gr.Textbox(label="Confidence", interactive=False)
            reasoning_out = gr.Textbox(label="Routing reason", interactive=False)
            gr.Markdown("#### Draft reply")
            draft_subject_out = gr.Textbox(label="Subject", interactive=False)
            draft_body_out = gr.Textbox(label="Body", lines=8, interactive=False)
            internal_note_out = gr.Textbox(label="Internal note", interactive=False)
            escalate_out = gr.Textbox(label="Escalate?", interactive=False)

    run_btn.click(
        fn=route_and_draft,
        inputs=[subject_in, name_in, email_in, body_in, model_in],
        outputs=[
            urgency_out,
            team_out,
            confidence_out,
            reasoning_out,
            draft_subject_out,
            draft_body_out,
            internal_note_out,
            escalate_out,
        ],
    )

if __name__ == "__main__":
    demo.launch()
