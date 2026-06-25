"""Gradio demo — AR Collection Agent via OpenRouter."""

import json
import os

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

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
.badge-blue   { background: #dbeafe; color: #1e40af; }
.badge-gray   { background: #f3f4f6; color: #374151; }
footer { display: none !important; }
"""

HEADER = """\
# 48 · AR Collection Agent
Classify AR customers by aging bucket and generate **tone-calibrated collection letters** for each tier.

> **Harness concept — aging-bucket state machine:** Bucket assignment is fully deterministic (`BUCKET_MAPPING` dict).
> The LLM generates a different persona per tier using four distinct system prompts — same task, four radically different tones.
> Credit hold logic is also deterministic (>90 days overdue or >80% of credit limit exposed).
"""

TIER_SYSTEM_PROMPTS: dict = {
    "friendly_reminder": (
        "You are a polite and professional accounts receivable specialist. "
        "Write a warm, friendly payment reminder letter of approximately 150 words. "
        "Tone: Assume the overdue payment is simply an oversight. "
        "Required: acknowledge good standing, state invoice and amount, "
        "request payment, list payment methods. "
        "Output only the letter body."
    ),
    "formal_notice": (
        "You are a firm but professional accounts receivable manager. "
        "Write a formal payment notice letter of approximately 200 words. "
        "Required: invoice number and amount, 7-day payment deadline, "
        "consequences (interest charges, credit hold), payment instructions. "
        "Output only the letter body."
    ),
    "final_demand": (
        "You are a senior accounts receivable director. "
        "Write a serious, unambiguous final demand letter of approximately 250 words. "
        "Required: account history summary, 5-business-day deadline, "
        "explicit legal warning (referral to counsel + potential litigation), "
        "final payment instructions. "
        "Output only the letter body."
    ),
    "legal_referral": (
        "You are an accounts receivable manager preparing an internal legal referral memo. "
        "Write a concise internal memo of approximately 200 words. "
        "Format: TO: Legal Department / FROM: Accounts Receivable / "
        "RE: Customer [Name] — Overdue Account Referral. "
        "Required: customer ID, total exposure, days overdue, "
        "collection attempt summary, recommended action. "
        "Output only the memo body."
    ),
}

BUCKET_MAPPING: dict = {
    "current": "no_action",
    "1_30": "friendly_reminder",
    "31_60": "formal_notice",
    "61_90": "final_demand",
    "90_plus": "legal_referral",
}

TIER_COLORS = {
    "no_action": "badge-green",
    "friendly_reminder": "badge-blue",
    "formal_notice": "badge-orange",
    "final_demand": "badge-red",
    "legal_referral": "badge-red",
}

BUCKET_LABELS = {
    "current": "Current",
    "1_30": "1–30 days",
    "31_60": "31–60 days",
    "61_90": "61–90 days",
    "90_plus": "90+ days",
}


def _get_bucket(days_overdue: int) -> str:
    if days_overdue <= 0:
        return "current"
    if days_overdue <= 30:
        return "1_30"
    if days_overdue <= 60:
        return "31_60"
    if days_overdue <= 90:
        return "61_90"
    return "90_plus"


def _priority_score(days_overdue: int, outstanding_amount: float) -> int:
    raw = days_overdue / 10 + outstanding_amount / 5000
    return min(10, max(1, int(raw)))


def _credit_hold(days_overdue: int, total_exposure: float, credit_limit: float):
    reasons = []
    if days_overdue > 90:
        reasons.append(f"{days_overdue} days overdue")
    ratio = total_exposure / credit_limit if credit_limit > 0 else 0.0
    if ratio > 0.8:
        reasons.append(f"exposure {ratio * 100:.1f}% of credit limit")
    if reasons:
        return True, "; ".join(reasons)
    return False, None


def generate_plan(customer_json: str, as_of_date: str, model: str):
    try:
        raw = json.loads(customer_json)
        if not isinstance(raw, list):
            raise ValueError("Input must be a JSON array.")
    except (json.JSONDecodeError, ValueError) as exc:
        return [], 0, 0, "", f"JSON error: {exc}"

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )

    table_rows = []
    letter_parts = []

    for cust in raw:
        try:
            customer_id = cust.get("customer_id", "?")
            customer_name = cust.get("customer_name", "Unknown")
            invoice_number = cust.get("invoice_number", "")
            due_date = cust.get("due_date", "")
            outstanding_amount = float(cust.get("outstanding_amount", 0))
            currency = cust.get("currency", "USD")
            days_overdue = int(cust.get("days_overdue", 0))
            prior_contact_count = int(cust.get("prior_contact_count", 0))
            credit_limit = float(cust.get("credit_limit", 0))
            total_exposure = float(cust.get("total_exposure", outstanding_amount))
        except (KeyError, TypeError, ValueError):
            table_rows.append(["?", "?", "parse_error", "?", 0, "NO"])
            continue

        bucket = _get_bucket(days_overdue)
        tier = BUCKET_MAPPING[bucket]
        score = _priority_score(days_overdue, outstanding_amount)
        hold, hold_reason = _credit_hold(days_overdue, total_exposure, credit_limit)

        if tier == "no_action":
            letter = "No action required — account current."
        else:
            user_content = (
                f"Customer: {customer_name} (ID: {customer_id})\n"
                f"Invoice: {invoice_number}\n"
                f"Due date: {due_date}\n"
                f"Outstanding: {currency} {outstanding_amount:,.2f}\n"
                f"Days overdue: {days_overdue}\n"
                f"Prior contacts: {prior_contact_count}\n"
                f"Total exposure: {currency} {total_exposure:,.2f}\n"
                f"Credit limit: {currency} {credit_limit:,.2f}"
            )
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": TIER_SYSTEM_PROMPTS[tier]},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=0.3,
                )
                letter = resp.choices[0].message.content or "No response."
            except Exception as exc:
                letter = f"API error: {exc}"

        table_rows.append([
            customer_name,
            BUCKET_LABELS.get(bucket, bucket),
            tier.replace("_", " ").title(),
            f"{currency} {outstanding_amount:,.2f}",
            score,
            "YES 🔒" if hold else "No",
        ])

        header = f"{'═' * 60}\n{customer_name} | {BUCKET_LABELS.get(bucket, bucket)} | {tier.replace('_', ' ').title()}"
        if hold and hold_reason:
            header += f"\n⚠ Credit hold: {hold_reason}"
        letter_parts.append(f"{header}\n{'─' * 60}\n{letter}\n")

    # Sort by priority score descending (col index 4)
    table_rows.sort(key=lambda r: r[4], reverse=True)

    credit_hold_count = sum(1 for r in table_rows if "YES" in str(r[5]))
    legal_referral_count = sum(1 for r in table_rows if "Legal Referral" in str(r[2]))

    summary = (
        f"Plan as of {as_of_date} · {len(table_rows)} accounts · "
        f"{credit_hold_count} credit hold(s) · {legal_referral_count} legal referral(s)"
    )

    letters_text = "\n".join(letter_parts) if letter_parts else "No letters generated."

    return table_rows, credit_hold_count, legal_referral_count, letters_text, summary


EXAMPLE_CUSTOMERS_JSON = json.dumps([
    {"customer_id": "CUST-001", "customer_name": "Apex Corp", "invoice_number": "INV-2025-0441",
     "invoice_date": "2025-06-10", "due_date": "2025-06-24", "outstanding_amount": 8750.00,
     "currency": "USD", "days_overdue": 0, "prior_contact_count": 0, "credit_limit": 50000.00, "total_exposure": 8750.00},
    {"customer_id": "CUST-002", "customer_name": "BrightPath Ltd", "invoice_number": "INV-2025-0388",
     "invoice_date": "2025-05-17", "due_date": "2025-06-06", "outstanding_amount": 12400.00,
     "currency": "USD", "days_overdue": 18, "prior_contact_count": 0, "credit_limit": 50000.00, "total_exposure": 12400.00},
    {"customer_id": "CUST-003", "customer_name": "Coastal Trading", "invoice_number": "INV-2025-0312",
     "invoice_date": "2025-04-20", "due_date": "2025-05-10", "outstanding_amount": 31500.00,
     "currency": "USD", "days_overdue": 45, "prior_contact_count": 1, "credit_limit": 50000.00, "total_exposure": 31500.00},
    {"customer_id": "CUST-004", "customer_name": "Delta Enterprises", "invoice_number": "INV-2025-0244",
     "invoice_date": "2025-03-15", "due_date": "2025-04-14", "outstanding_amount": 22000.00,
     "currency": "USD", "days_overdue": 72, "prior_contact_count": 2, "credit_limit": 50000.00, "total_exposure": 22000.00},
    {"customer_id": "CUST-005", "customer_name": "Echo Systems", "invoice_number": "INV-2025-0180",
     "invoice_date": "2025-02-10", "due_date": "2025-03-12", "outstanding_amount": 85000.00,
     "currency": "USD", "days_overdue": 97, "prior_contact_count": 3, "credit_limit": 100000.00, "total_exposure": 120000.00},
    {"customer_id": "CUST-006", "customer_name": "Frontier Corp", "invoice_number": "INV-2025-0201",
     "invoice_date": "2025-04-25", "due_date": "2025-05-20", "outstanding_amount": 4200.00,
     "currency": "USD", "days_overdue": 35, "prior_contact_count": 0, "credit_limit": 50000.00, "total_exposure": 4200.00},
], indent=2)

with gr.Blocks(title="AR Collection Agent", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(HEADER)

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### Customer Data")
            customer_input = gr.Textbox(
                label="JSON array of customer records",
                lines=22,
                value=EXAMPLE_CUSTOMERS_JSON,
            )
        with gr.Column(scale=1):
            gr.Markdown("### Settings")
            as_of_date_input = gr.Textbox(label="As of Date", value="2025-06-24")
            model_dropdown = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Generate Collection Plan", variant="primary", size="lg")

    gr.Markdown("---\n### Collection Plan")
    actions_table = gr.Dataframe(
        headers=["Customer", "Aging Bucket", "Tier", "Amount", "Priority", "Credit Hold"],
        label="Actions (sorted by priority score)",
        interactive=False,
        wrap=True,
    )

    with gr.Row():
        credit_hold_out = gr.Number(label="Credit Hold Count", precision=0, interactive=False)
        legal_referral_out = gr.Number(label="Legal Referral Count", precision=0, interactive=False)

    summary_out = gr.Textbox(label="Summary", interactive=False)

    gr.Markdown("### Generated Letters")
    letters_out = gr.Textbox(
        label="Collection Letters & Memos",
        lines=20,
        interactive=False,
        placeholder="Letters will appear here after running the plan...",
    )

    gr.Examples(
        examples=[[EXAMPLE_CUSTOMERS_JSON, "2025-06-24", MODELS[0]]],
        inputs=[customer_input, as_of_date_input, model_dropdown],
        label="6 customers across all aging buckets",
    )

    run_btn.click(
        fn=generate_plan,
        inputs=[customer_input, as_of_date_input, model_dropdown],
        outputs=[actions_table, credit_hold_out, legal_referral_out, letters_out, summary_out],
    )

if __name__ == "__main__":
    demo.launch()
