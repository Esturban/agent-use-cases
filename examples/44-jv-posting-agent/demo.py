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


def run_demo(event_description, document_type, amount, cost_centre, period, model):
    """Call OpenRouter, validate balance, return structured result."""
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
            line.side,
            line.account_code,
            line.account_name,
            line.amount,
            line.cost_centre or "",
        ]
        for line in result.lines
    ]
    return lines_data, str(balanced), status, total_dr, total_cr


with gr.Blocks(title="JV Posting Agent") as demo:
    gr.Markdown(
        "# 44 · JV Posting Agent\n"
        "Convert a business event into a balanced double-entry journal posting."
    )
    with gr.Row():
        with gr.Column():
            event_input = gr.Textbox(label="Event Description", lines=3)
            doc_type = gr.Dropdown(
                choices=["SA", "KR", "DR", "ZP", "AB", "AA", "RE"],
                label="Document Type",
                value="AA",
            )
            amount_input = gr.Number(label="Amount", value=10000.0)
            cc_input = gr.Textbox(label="Cost Centre (optional)", value="")
            period_input = gr.Textbox(label="Period (YYYY-MM)", value="2025-06")
            model_input = gr.Dropdown(choices=MODELS, label="Model", value=MODELS[0])
            submit_btn = gr.Button("Generate Posting", variant="primary")
        with gr.Column():
            lines_out = gr.Dataframe(
                headers=["Side", "Account Code", "Account Name", "Amount", "Cost Centre"],
                label="Journal Lines",
            )
            balanced_out = gr.Textbox(label="Balanced")
            status_out = gr.Textbox(label="Posting Status")
            dr_out = gr.Number(label="Total Debits")
            cr_out = gr.Number(label="Total Credits")

    submit_btn.click(
        fn=run_demo,
        inputs=[event_input, doc_type, amount_input, cc_input, period_input, model_input],
        outputs=[lines_out, balanced_out, status_out, dr_out, cr_out],
    )

    gr.Examples(
        examples=[
            [
                "Received IT equipment invoice from Dell, capitalise as fixed asset",
                "AA",
                12500.0,
                "CC5001",
                "2025-06",
                MODELS[0],
            ],
            [
                "Accrue June salary expense for finance department, not yet paid",
                "RE",
                45000.0,
                "CC2001",
                "2025-06",
                MODELS[0],
            ],
            [
                "Customer payment received for outstanding invoice INV-2025-0441",
                "ZP",
                8750.0,
                "",
                "2025-06",
                MODELS[0],
            ],
        ],
        inputs=[event_input, doc_type, amount_input, cc_input, period_input, model_input],
    )

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set — copy .env.example to .env")
    demo.launch()
