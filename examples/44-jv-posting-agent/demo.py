"""Gradio demo — JV Posting Agent via OpenRouter."""

import os

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from src.calculator import check_balance
from src.prompts import POSTING_PROMPT
from src.schema import PostingResult

load_dotenv()

MODELS = [
    "openai/gpt-5.4-nano",
    "openai/gpt-4.1-nano",
    "anthropic/claude-haiku-4-5",
    "mistralai/mistral-7b-instruct",
]

SYSTEM_CONTENT = POSTING_PROMPT.content

CSS = """
.badge {
    display: inline-block;
    padding: 5px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85em;
    letter-spacing: 0.03em;
}
.badge-green  { background: #d1fae5; color: #065f46; }
.badge-red    { background: #fee2e2; color: #991b1b; }
.badge-orange { background: #fef3c7; color: #92400e; }
.badge-gray   { background: #f3f4f6; color: #374151; }
footer { display: none !important; }
"""

HEADER = """\
# 44 · JV Posting Agent
Convert any business event description into a **balanced, GL-coded double-entry journal posting**.

> **Harness concept — double-entry validation gate:** The LLM assigns accounts from a 20-account chart of accounts.
> A deterministic `check_balance()` gate then enforces **debit = credit** — LLM arithmetic is never trusted for financial correctness.
> Any imbalanced posting is returned as `rejected` regardless of model confidence.
"""


def _badge(text: str) -> str:
    text_lower = text.lower()
    if text_lower in ("approved", "true"):
        cls = "badge-green"
    elif text_lower in ("rejected", "false"):
        cls = "badge-red"
    else:
        cls = "badge-orange"
    return f'<span class="badge {cls}">{text.upper()}</span>'


def run_demo(event_description, document_type, amount, cost_centre, period, model):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )
    user_msg = (
        f"Event: {event_description}\n"
        f"Document type: {document_type}\n"
        f"Amount: ${float(amount):,.2f}\n"
        f"Period: {period}\n"
        f"Cost centre: {cost_centre or 'N/A'}"
    )
    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_CONTENT},
            {"role": "user", "content": user_msg},
        ],
        response_format=PostingResult,
    )
    result: PostingResult = response.choices[0].message.parsed
    debits = [line.amount for line in result.lines if line.side == "debit"]
    credits = [line.amount for line in result.lines if line.side == "credit"]
    balanced = check_balance(debits, credits)
    total_dr = round(sum(debits), 2)
    total_cr = round(sum(credits), 2)
    status = "approved" if balanced else "rejected"

    lines_data = [
        [
            "DR" if line.side == "debit" else "CR",
            line.account_code,
            line.account_name,
            f"{line.amount:,.2f}",
            line.cost_centre or "",
        ]
        for line in result.lines
    ]
    return (
        lines_data,
        _badge(str(balanced)),
        _badge(status),
        f"{total_dr:,.2f}",
        f"{total_cr:,.2f}",
    )


with gr.Blocks(title="JV Posting Agent", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(HEADER)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")
            event_input = gr.Textbox(
                label="Business Event",
                lines=3,
                placeholder="e.g. Received IT equipment invoice from Dell, capitalise as fixed asset",
            )
            with gr.Row():
                doc_type = gr.Dropdown(
                    choices=["SA", "KR", "DR", "ZP", "AB", "AA", "RE"],
                    label="Document Type",
                    value="AA",
                    info="AA=Asset · AB=Depreciation · RE=Accrual · ZP=Payment · KR=Vendor inv · DR=Customer inv",
                )
                amount_input = gr.Number(label="Amount (USD)", value=12500.0, precision=2)
            with gr.Row():
                cc_input = gr.Textbox(label="Cost Centre", placeholder="CC5001 (optional)")
                period_input = gr.Textbox(label="Period", value="2025-06", placeholder="YYYY-MM")
            model_input = gr.Dropdown(choices=MODELS, label="Model", value=MODELS[0])
            submit_btn = gr.Button("Generate Journal Posting", variant="primary", size="lg")

        with gr.Column(scale=1):
            gr.Markdown("### Journal Lines")
            lines_out = gr.Dataframe(
                headers=["Side", "Account", "Account Name", "Amount", "Cost Centre"],
                label="Double-Entry Lines",
                interactive=False,
                wrap=True,
            )
            with gr.Row():
                balanced_out = gr.HTML(label="Balanced")
                status_out = gr.HTML(label="Status")
            with gr.Row():
                dr_out = gr.Textbox(label="Total Debits", interactive=False)
                cr_out = gr.Textbox(label="Total Credits", interactive=False)

    submit_btn.click(
        fn=run_demo,
        inputs=[event_input, doc_type, amount_input, cc_input, period_input, model_input],
        outputs=[lines_out, balanced_out, status_out, dr_out, cr_out],
    )

    gr.Markdown("---\n### Try an example")
    gr.Examples(
        examples=[
            ["Received IT equipment invoice from Dell, capitalise as fixed asset", "AA", 12500.0, "CC5001", "2025-06", MODELS[0]],
            ["Accrue June salary expense for finance department, not yet paid", "RE", 45000.0, "CC2001", "2025-06", MODELS[0]],
            ["Customer payment received for outstanding invoice INV-2025-0441", "ZP", 8750.0, "", "2025-06", MODELS[0]],
        ],
        inputs=[event_input, doc_type, amount_input, cc_input, period_input, model_input],
        label="Pre-filled scenarios",
    )

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set — copy .env.example to .env")
    demo.launch()
