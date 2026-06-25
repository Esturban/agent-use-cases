"""Gradio demo — Bank Reconciliation Agent via OpenRouter."""

import csv
import io
import json
import os

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import List

from src.calculator import find_matches
from src.prompts import RECON_SYSTEM
from src.schema import BankReconciliationSummary, MatchedPair, UnmatchedItem

load_dotenv()

MODELS = [
    "openai/gpt-5.4-nano",
    "openai/gpt-4.1-nano",
    "anthropic/claude-haiku-4-5",
]

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
# 46 · Bank Reconciliation Agent
Match bank statement transactions against GL cash account entries and classify exceptions.

> **Harness concept — bounded matching loop:** A deterministic Python pre-matcher handles exact matches
> (same amount + date) and probable matches (same amount, within 2 days). The LLM classifies **only the
> unmatched exceptions** — so model call volume scales with exception count, not total transaction volume.
> Framework: raw OpenAI SDK (no LangGraph).
"""

EXC_EMOJI = {
    "timing_difference": "⏱ timing_difference",
    "bank_charge": "🏦 bank_charge",
    "duplicate": "♊ duplicate",
    "missing_booking": "❓ missing_booking",
    "fraud_indicator": "🚨 fraud_indicator",
}

EXAMPLE_BANK = """date,description,debit,credit
2025-06-02,Customer payment Invoice 1041,0.00,5200.00
2025-06-04,Supplier payment PO-8821,3100.00,0.00
2025-06-07,Customer payment Invoice 1042,0.00,8750.00
2025-06-10,Payroll run June W1,12400.00,0.00
2025-06-12,Customer payment Invoice 1043,0.00,4620.00
2025-06-14,Rent payment June,3500.00,0.00
2025-06-18,Customer payment Invoice 1044,0.00,6930.00
2025-06-21,Utilities payment,820.00,0.00
2025-06-25,Customer payment Invoice 1045,0.00,2980.00
2025-06-30,Deposit in transit Invoice 1046,0.00,1250.00
2025-06-30,Monthly account service fee,18.50,0.00
2025-06-28,Supplier payment PO-8830,7680.00,0.00"""

EXAMPLE_GL = """date,reference,amount,description
2025-06-02,JE-2001,5200.00,AR receipt Invoice 1041
2025-06-04,JE-2002,-3100.00,AP payment PO-8821
2025-06-07,JE-2003,8750.00,AR receipt Invoice 1042
2025-06-10,JE-2004,-12400.00,Payroll June W1
2025-06-12,JE-2005,4620.00,AR receipt Invoice 1043
2025-06-14,JE-2006,-3500.00,Rent June
2025-06-18,JE-2007,6930.00,AR receipt Invoice 1044
2025-06-21,JE-2008,-820.00,Utilities June
2025-06-25,JE-2009,2980.00,AR receipt Invoice 1045
2025-06-27,JE-2010,-7680.00,AP payment PO-8830
2025-06-30,JE-2011,-482.00,Accrual reversal prepaid insurance"""


def _parse_bank_csv(raw: str) -> list:
    reader = csv.DictReader(io.StringIO(raw.strip()))
    rows = []
    for i, row in enumerate(reader):
        rows.append({
            "txn_id": f"B{i + 1:02d}",
            "date": row["date"].strip(),
            "description": row["description"].strip(),
            "debit": float(row.get("debit", 0) or 0),
            "credit": float(row.get("credit", 0) or 0),
        })
    return rows


def _parse_gl_csv(raw: str) -> list:
    reader = csv.DictReader(io.StringIO(raw.strip()))
    rows = []
    for i, row in enumerate(reader):
        rows.append({
            "entry_id": f"GL{i + 1:02d}",
            "date": row["date"].strip(),
            "reference": row.get("reference", f"JE-{i + 1}").strip(),
            "amount": float(row["amount"]),
            "description": row["description"].strip(),
        })
    return rows


def _classify_unmatched(client, model, period, bank_balance, gl_balance, unmatched_bank, unmatched_gl):
    class _UnmatchedClassification(BaseModel):
        items: List[UnmatchedItem]

    if not unmatched_bank and not unmatched_gl:
        return []

    payload = {
        "unmatched_bank_transactions": unmatched_bank,
        "unmatched_gl_entries": unmatched_gl,
    }
    user_msg = (
        f"Period: {period}\nBank: {bank_balance}\nGL: {gl_balance}\n\n"
        f"{json.dumps(payload, indent=2)}"
    )
    resp = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": RECON_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        response_format=_UnmatchedClassification,
    )
    parsed = resp.choices[0].message.parsed
    return parsed.items if parsed else []


def reconcile(bank_csv, gl_csv, period, bank_balance, gl_balance, model):
    try:
        bank_txns = _parse_bank_csv(bank_csv)
        gl_entries = _parse_gl_csv(gl_csv)
    except Exception as exc:
        return 0, [], '<span class="badge badge-red">ERROR</span>', f"CSV parse error: {exc}"

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )

    matched_raw, unmatched_bank, unmatched_gl = find_matches(bank_txns, gl_entries)
    matched_pairs = [MatchedPair(**m) for m in matched_raw]
    unmatched_items = _classify_unmatched(
        client, model, period, bank_balance, gl_balance, unmatched_bank, unmatched_gl
    )

    reconciling_value = sum(
        item.amount if item.source == "bank" else -item.amount
        for item in unmatched_items
        if item.exception_type == "timing_difference"
    )
    gap = abs(bank_balance - gl_balance - reconciling_value)
    is_reconciled = gap <= 0.01

    note = (
        f"Reconciliation complete for {period}. "
        f"{len(matched_pairs)} matched, {len(unmatched_items)} exceptions."
        if is_reconciled
        else f"Unexplained difference of {gap:,.2f} remains for {period}."
    )

    summary = BankReconciliationSummary(
        period=period,
        bank_closing_balance=bank_balance,
        gl_cash_balance=gl_balance,
        matched_pairs=matched_pairs,
        unmatched_items=unmatched_items,
        reconciling_items_value=reconciling_value,
        is_reconciled=is_reconciled,
        reconciliation_note=note,
    )

    unmatched_rows = [
        [
            item.item_id,
            "Bank" if item.source == "bank" else "GL",
            f"{item.amount:,.2f}",
            EXC_EMOJI.get(item.exception_type, item.exception_type),
            item.recommended_action,
        ]
        for item in summary.unmatched_items
    ]

    recon_badge = (
        '<span class="badge badge-green">✓ RECONCILED</span>'
        if summary.is_reconciled
        else '<span class="badge badge-red">✗ UNRECONCILED</span>'
    )

    return len(summary.matched_pairs), unmatched_rows, recon_badge, summary.reconciliation_note


with gr.Blocks(title="Bank Reconciliation Agent", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(HEADER)

    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown("### Bank Statement")
            bank_csv = gr.Textbox(
                label="CSV (date, description, debit, credit)",
                lines=13,
                value=EXAMPLE_BANK,
            )
            gr.Markdown("### GL Cash Account")
            gl_csv = gr.Textbox(
                label="CSV (date, reference, amount, description)",
                lines=11,
                value=EXAMPLE_GL,
            )
        with gr.Column(scale=1):
            gr.Markdown("### Settings")
            period = gr.Textbox(label="Period", value="June 2025")
            bank_balance = gr.Number(label="Bank Closing Balance", value=42350.00, precision=2)
            gl_balance = gr.Number(label="GL Cash Balance", value=41100.00, precision=2)
            model = gr.Dropdown(label="Model", choices=MODELS, value=MODELS[0])
            run_btn = gr.Button("Reconcile", variant="primary", size="lg")

    gr.Markdown("---\n### Results")
    with gr.Row():
        matched_count = gr.Number(label="Matched Pairs", precision=0, interactive=False)
        recon_badge_out = gr.HTML(label="Status")

    unmatched_df = gr.Dataframe(
        headers=["ID", "Source", "Amount", "Exception Type", "Recommended Action"],
        label="Unmatched / Exception Items",
        interactive=False,
        wrap=True,
    )
    note_out = gr.Textbox(label="Reconciliation Note", lines=2, interactive=False)

    run_btn.click(
        fn=reconcile,
        inputs=[bank_csv, gl_csv, period, bank_balance, gl_balance, model],
        outputs=[matched_count, unmatched_df, recon_badge_out, note_out],
    )

    gr.Markdown("---\n### Try an example")
    gr.Examples(
        examples=[[EXAMPLE_BANK, EXAMPLE_GL, "June 2025", 42350.00, 41100.00, MODELS[0]]],
        inputs=[bank_csv, gl_csv, period, bank_balance, gl_balance, model],
        label="Scenario 1 — standard month-end close",
    )

if __name__ == "__main__":
    demo.launch()
