"""Gradio demo — AP Invoice Processor via OpenRouter."""

import json
import os

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from src.prompts import EXTRACTOR_PROMPT, MATCHER_PROMPT
from src.schema import ExtractedInvoice, MatchResult
from src.tools import lookup_gr, lookup_po

load_dotenv()

MODELS = [
    "openai/gpt-5.4-nano",
    "openai/gpt-4.1-nano",
    "anthropic/claude-haiku-4-5",
    "mistralai/mistral-7b-instruct",
]

EXTRACTOR_SYSTEM = EXTRACTOR_PROMPT.content
MATCHER_SYSTEM = MATCHER_PROMPT.content

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
.badge-blue   { background: #dbeafe; color: #1e40af; }
.badge-gray   { background: #f3f4f6; color: #374151; }
footer { display: none !important; }
"""

HEADER = """\
# 45 · AP Invoice Processor
Run a **3-way match** (invoice → PO → goods receipt) and route the invoice to the correct approval tier.

> **Harness concept — staged pipeline:** Stage 1 extracts structured invoice data (LLM).
> Stage 2 fetches PO and GR records (deterministic lookup — no LLM).
> Stage 3 classifies discrepancies (LLM). Approval routing is fully deterministic.
"""

TIER_COLORS = {
    "auto_approve": "badge-green",
    "line_manager": "badge-blue",
    "finance_controller": "badge-orange",
    "vp_finance": "badge-red",
}

STATUS_COLORS = {
    "clean": "badge-green",
    "discrepancy": "badge-orange",
    "blocked": "badge-red",
}

SEV_EMOJI = {"info": "🔵 info", "warn": "🟡 warn", "block": "🔴 block"}


def _badge(text: str, color_cls: str) -> str:
    label = text.replace("_", " ").title()
    return f'<span class="badge {color_cls}">{label}</span>'


def run_demo(invoice_text: str, model: str):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )

    # Stage 1 — LLM extraction
    extract_resp = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": EXTRACTOR_SYSTEM},
            {"role": "user", "content": invoice_text},
        ],
        response_format=ExtractedInvoice,
    )
    invoice: ExtractedInvoice = extract_resp.choices[0].message.parsed

    # Stage 2 — deterministic PO / GR lookup
    po_data = lookup_po(invoice.po_reference)
    gr_data = lookup_gr(invoice.po_reference)

    # Stage 3 — LLM match classification
    context = (
        f"Invoice:\n{json.dumps(invoice.model_dump(), indent=2)}\n\n"
        f"Purchase Order:\n{json.dumps(po_data, indent=2) if po_data else 'NOT FOUND'}\n\n"
        f"Goods Receipt:\n{json.dumps(gr_data, indent=2) if gr_data else 'NOT FOUND'}"
    )
    match_resp = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": MATCHER_SYSTEM},
            {"role": "user", "content": context},
        ],
        response_format=MatchResult,
    )
    mr: MatchResult = match_resp.choices[0].message.parsed

    disc_rows = [
        [
            d.discrepancy_type.replace("_", " "),
            d.field,
            d.invoice_value,
            d.expected_value,
            f"{d.variance_pct:.1f}%" if d.variance_pct is not None else "—",
            SEV_EMOJI.get(d.severity, d.severity),
        ]
        for d in mr.discrepancies
    ]

    tier_cls = TIER_COLORS.get(mr.approval_tier, "badge-gray")
    status_cls = STATUS_COLORS.get(mr.match_status, "badge-gray")

    return (
        f"{invoice.vendor_id}",
        f"{invoice.invoice_number}",
        f"{invoice.currency} {invoice.total_amount:,.2f}",
        disc_rows,
        _badge(mr.match_status, status_cls),
        _badge(mr.approval_tier, tier_cls),
        mr.approval_rationale,
    )


EXAMPLE_1 = (
    "ACME Tech Supplies\n"
    "Vendor ID: ACME-001\n"
    "Invoice Number: INV-ACME-2025-0892\n"
    "Invoice Date: 2025-06-15\n"
    "PO Reference: PO-2025-001\n\n"
    "Line Items:\n"
    "  1. Cloud Server Model X500 — Qty: 4 — Unit Price: $2,100.00 — Total: $8,400.00\n\n"
    "Invoice Total: $8,400.00 USD"
)

EXAMPLE_2 = (
    "Beta Office Solutions\n"
    "Vendor ID: BETA-002\n"
    "Invoice Number: INV-BETA-2025-0441\n"
    "Invoice Date: 2025-06-18\n"
    "PO Reference: PO-2025-002\n\n"
    "Line Items:\n"
    "  1. Ergonomic Office Chair — Qty: 100 — Unit Price: $150.00 — Total: $15,000.00\n\n"
    "Invoice Total: $15,000.00 USD"
)

EXAMPLE_3 = (
    "Gamma Advisory Group\n"
    "Vendor ID: GAMMA-003\n"
    "Invoice Number: INV-GAMMA-2025-0318\n"
    "Invoice Date: 2025-06-20\n"
    "PO Reference: PO-2025-003\n\n"
    "Line Items:\n"
    "  1. Management Consulting Services — Qty: 75 hours — Unit Price: $421.25 — Total: $31,593.75\n\n"
    "Invoice Total: $31,593.75 USD"
)

with gr.Blocks(title="AP Invoice Processor", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(HEADER)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Invoice")
            invoice_input = gr.Textbox(
                label="Invoice Text",
                lines=14,
                placeholder="Paste vendor invoice text — vendor name, vendor ID, invoice number, date, PO reference, line items, total.",
            )
            model_input = gr.Dropdown(choices=MODELS, label="Model", value=MODELS[0])
            submit_btn = gr.Button("Run 3-Way Match", variant="primary", size="lg")

        with gr.Column(scale=1):
            gr.Markdown("### Extraction")
            with gr.Row():
                vendor_out = gr.Textbox(label="Vendor ID", interactive=False)
                invoice_num_out = gr.Textbox(label="Invoice Number", interactive=False)
                total_out = gr.Textbox(label="Total Amount", interactive=False)
            gr.Markdown("### Match Result")
            disc_out = gr.Dataframe(
                headers=["Discrepancy", "Field", "Invoice", "Expected", "Variance", "Severity"],
                label="Discrepancies",
                interactive=False,
                wrap=True,
            )
            with gr.Row():
                status_out = gr.HTML(label="Match Status")
                tier_out = gr.HTML(label="Approval Tier")
            rationale_out = gr.Textbox(label="Rationale", lines=3, interactive=False)

    submit_btn.click(
        fn=run_demo,
        inputs=[invoice_input, model_input],
        outputs=[vendor_out, invoice_num_out, total_out, disc_out, status_out, tier_out, rationale_out],
    )

    gr.Markdown("---\n### Try an example")
    gr.Examples(
        examples=[
            [EXAMPLE_1, MODELS[0]],
            [EXAMPLE_2, MODELS[0]],
            [EXAMPLE_3, MODELS[0]],
        ],
        inputs=[invoice_input, model_input],
        label="Clean match · Quantity short · Price variance",
    )

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set — copy .env.example to .env")
    demo.launch()
