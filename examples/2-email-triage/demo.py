"""Gradio demo — Email Triage via OpenRouter structured output."""

import os

import gradio as gr
from openai import OpenAI

from src.schema import EmailTriage

SAMPLES = [
    """\
Subject: URGENT - Invoice #4821 overdue 30 days, account suspended
From: accounts@acme-corp.com

Hi team, our account has been suspended due to unpaid invoice #4821 ($4,200).
Payment was due May 1st -- now 30 days overdue.
We need this resolved immediately or we lose access to production systems.
Please escalate ASAP.""",
    """\
Subject: ALERT: Production database unreachable - all services down
From: monitoring@internal.co

Our monitoring system detected that db-prod-01 is not responding.
All customer-facing services are returning 503 errors.
Engineering has been paged. Estimated impact: 2,000 active sessions.""",
    """\
Subject: Idea - dark mode for the dashboard
From: alex.chen@customer.com

Hey, love the product! One thing that would really help is a dark mode option
for the main dashboard. A lot of us use it late at night and the bright white
is pretty hard on the eyes. No rush, just a thought.""",
    """\
Subject: EXCLUSIVE OFFER - 80% off enterprise plan, TODAY ONLY!!!
From: deals@saas-blaster.io

Don't miss out on our BIGGEST SALE EVER. Upgrade now and save thousands.
Limited spots available. Click here to claim your discount before midnight.
Unsubscribe | Terms | Privacy""",
]

URGENCY_EMOJI = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}
CATEGORY_EMOJI = {
    "billing": "💳 billing",
    "technical": "⚙️ technical",
    "general": "💬 general",
    "spam": "🗑️ spam",
}

MODELS = [
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]


def classify(email_text: str, model: str) -> tuple[str, str, str, str]:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return "—", "—", "Set OPENROUTER_API_KEY and restart", "—"

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an email triage assistant. Classify the email and recommend an action.",
            },
            {"role": "user", "content": email_text},
        ],
        response_format=EmailTriage,
    )
    result: EmailTriage = completion.choices[0].message.parsed
    return (
        URGENCY_EMOJI.get(result.urgency, result.urgency),
        CATEGORY_EMOJI.get(result.category, result.category),
        result.summary,
        result.recommended_action,
    )


with gr.Blocks(title="Email Triage") as demo:
    gr.Markdown(
        "## Email Triage\n"
        "Paste an email and let the agent classify urgency, category, and recommended action."
    )
    with gr.Row():
        with gr.Column(scale=2):
            email_input = gr.Textbox(
                label="Email content",
                lines=10,
                placeholder="Paste email here…",
                value=SAMPLES[0],
            )
            gr.Examples(examples=[[s] for s in SAMPLES], inputs=email_input, label="Samples")
        with gr.Column(scale=1):
            model_select = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model (via OpenRouter)")
            classify_btn = gr.Button("Triage", variant="primary")
            urgency_out = gr.Textbox(label="Urgency", interactive=False)
            category_out = gr.Textbox(label="Category", interactive=False)
            summary_out = gr.Textbox(label="Summary", interactive=False)
            action_out = gr.Textbox(label="Recommended action", interactive=False)

    classify_btn.click(
        fn=classify,
        inputs=[email_input, model_select],
        outputs=[urgency_out, category_out, summary_out, action_out],
    )

if __name__ == "__main__":
    demo.launch()
