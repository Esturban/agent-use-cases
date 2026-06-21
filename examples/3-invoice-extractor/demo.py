import os
import sys

import gradio as gr
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(raise_error_if_not_found=False))


sys.path.insert(0, os.path.dirname(__file__))
from src.schema import Invoice

SYSTEM_PROMPT = (
    "You are an invoice parsing assistant. Extract structured data from invoice text. "
    "Return exact values from the document. Date must be ISO format YYYY-MM-DD. "
    "Amounts in decimal (no currency symbols in numbers)."
)

MODELS = [
    "openai/gpt-5.4-nano",
    "minimax/minimax-m3",
    "openai/gpt-4.1-nano",
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

SAMPLE_AGENCY = """NovaMark Agency — Digital Marketing Services
Invoice No: NM-2024-0338
Issue Date: 15 August 2024

Social Media Management (3 platforms)    1 month    £1,200.00
Paid Ads Management Fee                  1 month    £800.00
Creative Production (8 assets)           8 units    £150.00/unit = £1,200.00
Performance Report & Strategy Call       1 session  £350.00

Subtotal: £3,550.00
VAT (20%): £710.00
Total Due: £4,260.00
Payment Terms: 30 days"""


def extract_invoice(invoice_text: str, model: str):
    if not invoice_text.strip():
        return "", "", "", [], 0.0, 0.0, 0.0

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENAI_API_KEY"],
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
    gr.Markdown(
        "## 📄 Invoice Extractor\n"
        "Paste any invoice or receipt — the model pulls out vendor, date, every line item, "
        "and totals into structured fields in under 3 seconds.\n\n"
        "**Built for:** finance teams and accounts payable — replacing manual data entry "
        "from PDFs, emails, and scanned receipts into any ERP or spreadsheet."
    )

    with gr.Accordion("What gets extracted", open=True):
        gr.Markdown(
            "| Field | Detail |\n"
            "|-------|--------|\n"
            "| **Vendor** | Supplier / business name |\n"
            "| **Invoice number** | Reference ID exactly as written |\n"
            "| **Date** | Normalized to ISO format (YYYY-MM-DD) |\n"
            "| **Line items** | Description · quantity · unit price · line total |\n"
            "| **Subtotal / Tax / Total** | Amounts as plain decimals, no currency symbols |\n\n"
            "**Samples included:** SaaS subscription, consulting day-rate, cafe receipt, "
            "and a UK agency invoice (tests currency symbol handling and VAT).\n\n"
            "_The model returns exact values from the document — it never interpolates or infers missing fields._"
        )

    with gr.Row():
        invoice_input = gr.Textbox(
            label="Invoice text",
            lines=14,
            placeholder="Paste your invoice or receipt text here…",
        )

    with gr.Row():
        model_dropdown = gr.Dropdown(
            choices=MODELS,
            value=MODELS[0],
            label="Model",
        )
        extract_btn = gr.Button("Extract Invoice", variant="primary")

    gr.Examples(
        examples=[[SAMPLE_SAAS], [SAMPLE_CONSULTING], [SAMPLE_CAFE], [SAMPLE_AGENCY]],
        inputs=[invoice_input],
        label="Sample invoices — click to load",
    )

    gr.Markdown("#### Extracted fields")

    with gr.Row():
        vendor_out = gr.Textbox(label="Vendor", interactive=False)
        invoice_number_out = gr.Textbox(label="Invoice number", interactive=False)
        date_out = gr.Textbox(label="Date (ISO)", interactive=False)

    line_items_out = gr.Dataframe(
        headers=["Description", "Qty", "Unit Price", "Total"],
        label="Line items",
        interactive=False,
    )

    with gr.Row():
        subtotal_out = gr.Number(label="Subtotal")
        tax_out = gr.Number(label="Tax")
        total_out = gr.Number(label="Total amount")

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
