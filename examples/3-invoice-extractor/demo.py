import os
import sys

import gradio as gr
from openai import OpenAI

sys.path.insert(0, os.path.dirname(__file__))
from src.schema import Invoice

SYSTEM_PROMPT = (
    "You are an invoice parsing assistant. Extract structured data from invoice text. "
    "Return exact values from the document. Date must be ISO format YYYY-MM-DD. "
    "Amounts in decimal (no currency symbols in numbers)."
)

MODELS = [
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]

SAMPLE_SAAS = """CloudPeak Software
Invoice #: INV-2024-0892
Date: May 15, 2024

Annual SaaS License - 5 seats    Qty: 1    $2,400.00
Premium Support                   Qty: 1    $600.00
Onboarding Services               Qty: 3    $150.00 each = $450.00

Subtotal: $3,450.00
Tax (15%): $517.50
Total: $3,967.50"""

SAMPLE_CONSULTING = """Apex Cloud Consulting
Invoice #: APC-2024-112
Date: June 15, 2024

Architecture Review    1 day    $3,500.00
Implementation         3 days   $2,200.00/day = $6,600.00
Documentation          0.5 day  $1,800.00/day = $900.00

Subtotal: $11,000.00
GST (10%): $1,100.00
Total: $12,100.00"""

SAMPLE_CAFE = """Maple Street Cafe
Receipt #: RCP-0442
Date: July 3, 2024

Coffee        x2    $4.50 each = $9.00
Sandwich      x1    $12.50
Cake          x1    $6.00

Subtotal: $27.50
Tax (8%): $2.20
Total: $29.70"""


def extract_invoice(invoice_text: str, model: str):
    if not invoice_text.strip():
        return "", "", "", [], 0.0, 0.0, 0.0

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": invoice_text},
        ],
        response_format=Invoice,
    )

    result: Invoice = completion.choices[0].message.parsed

    line_items_data = [
        [item.description, item.quantity, f"${item.unit_price:.2f}", f"${item.total:.2f}"]
        for item in result.line_items
    ]

    return (
        result.vendor,
        result.invoice_number,
        result.date,
        line_items_data,
        result.subtotal,
        result.tax,
        result.total_amount,
    )


with gr.Blocks(title="Invoice Extractor") as demo:
    gr.Markdown("## Invoice Extractor\nPaste raw invoice or receipt text to extract structured fields.")

    with gr.Row():
        invoice_input = gr.Textbox(
            label="Invoice Text",
            lines=12,
            placeholder="Paste your invoice or receipt text here...",
        )

    with gr.Row():
        model_dropdown = gr.Dropdown(
            choices=MODELS,
            value=MODELS[0],
            label="Model",
        )
        extract_btn = gr.Button("Extract Invoice", variant="primary")

    gr.Examples(
        examples=[[SAMPLE_SAAS], [SAMPLE_CONSULTING], [SAMPLE_CAFE]],
        inputs=[invoice_input],
        label="Sample Invoices",
    )

    gr.Markdown("### Extracted Fields")

    with gr.Row():
        vendor_out = gr.Textbox(label="Vendor")
        invoice_number_out = gr.Textbox(label="Invoice Number")
        date_out = gr.Textbox(label="Date")

    line_items_out = gr.Dataframe(
        headers=["Description", "Qty", "Unit Price", "Total"],
        label="Line Items",
        interactive=False,
    )

    with gr.Row():
        subtotal_out = gr.Number(label="Subtotal")
        tax_out = gr.Number(label="Tax")
        total_out = gr.Number(label="Total Amount")

    extract_btn.click(
        fn=extract_invoice,
        inputs=[invoice_input, model_dropdown],
        outputs=[
            vendor_out,
            invoice_number_out,
            date_out,
            line_items_out,
            subtotal_out,
            tax_out,
            total_out,
        ],
    )

if __name__ == "__main__":
    demo.launch()
