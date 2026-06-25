"""Gradio demo for the AR Collection Agent (via OpenRouter).

Accepts a JSON list of customer dicts, runs the aging-bucket state machine,
and displays the resulting collection plan in a structured UI.
"""

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

# ---------------------------------------------------------------------------
# Tier system prompts (inline for OpenRouter direct calls)
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Deterministic helpers
# ---------------------------------------------------------------------------


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
        return True, "Credit hold: " + "; ".join(reasons) + "."
    return False, None


# ---------------------------------------------------------------------------
# Main handler
# ---------------------------------------------------------------------------


def generate_plan(customer_json: str, as_of_date: str, model: str):
    try:
        raw = json.loads(customer_json)
        if not isinstance(raw, list):
            raise ValueError("Input must be a JSON array of customer objects.")
    except (json.JSONDecodeError, ValueError) as exc:
        return [], 0, 0, f"JSON parse error: {exc}"

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )

    actions = []

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
        except (KeyError, TypeError, ValueError) as exc:
            actions.append(
                [customer_id if "customer_id" in cust else "?", "?", "parse_error", 0, "no", f"Error: {exc}"]
            )
            continue

        bucket = _get_bucket(days_overdue)
        tier = BUCKET_MAPPING[bucket]
        score = _priority_score(days_overdue, outstanding_amount)
        hold, _ = _credit_hold(days_overdue, total_exposure, credit_limit)

        if tier == "no_action":
            letter_preview = "No action required."
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
                    model=model.split("/", 1)[-1] if "/" in model else model,
                    messages=[
                        {"role": "system", "content": TIER_SYSTEM_PROMPTS[tier]},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=0.3,
                )
                letter_preview = resp.choices[0].message.content or "No response."
            except Exception as exc:
                letter_preview = f"API error: {exc}"

        actions.append(
            [customer_name, bucket, tier, f"{currency} {outstanding_amount:,.2f}", score, "YES" if hold else "no", letter_preview[:300]]
        )

    # Sort by priority score descending (column index 4)
    actions.sort(key=lambda r: r[4], reverse=True)

    credit_hold_count = sum(1 for r in actions if r[5] == "YES")
    legal_referral_count = sum(1 for r in actions if r[2] == "legal_referral")

    summary = (
        f"Plan as of {as_of_date}. "
        f"{len(actions)} accounts processed. "
        f"Credit holds: {credit_hold_count}. "
        f"Legal referrals: {legal_referral_count}."
    )

    # Return rows without the letter column for the dataframe, summary for textbox
    df_rows = [[r[0], r[1], r[2], r[3], r[4], r[5]] for r in actions]

    return df_rows, credit_hold_count, legal_referral_count, summary


# ---------------------------------------------------------------------------
# Example input — all 6 customers as pre-filled JSON
# ---------------------------------------------------------------------------

EXAMPLE_CUSTOMERS_JSON = json.dumps(
    [
        {
            "customer_id": "CUST-001",
            "customer_name": "Apex Corp",
            "invoice_number": "INV-2025-0441",
            "invoice_date": "2025-06-10",
            "due_date": "2025-06-24",
            "outstanding_amount": 8750.00,
            "currency": "USD",
            "days_overdue": 0,
            "prior_contact_count": 0,
            "credit_limit": 50000.00,
            "total_exposure": 8750.00,
        },
        {
            "customer_id": "CUST-002",
            "customer_name": "BrightPath Ltd",
            "invoice_number": "INV-2025-0388",
            "invoice_date": "2025-05-17",
            "due_date": "2025-06-06",
            "outstanding_amount": 12400.00,
            "currency": "USD",
            "days_overdue": 18,
            "prior_contact_count": 0,
            "credit_limit": 50000.00,
            "total_exposure": 12400.00,
        },
        {
            "customer_id": "CUST-003",
            "customer_name": "Coastal Trading",
            "invoice_number": "INV-2025-0312",
            "invoice_date": "2025-04-20",
            "due_date": "2025-05-10",
            "outstanding_amount": 31500.00,
            "currency": "USD",
            "days_overdue": 45,
            "prior_contact_count": 1,
            "credit_limit": 50000.00,
            "total_exposure": 31500.00,
        },
        {
            "customer_id": "CUST-004",
            "customer_name": "Delta Enterprises",
            "invoice_number": "INV-2025-0244",
            "invoice_date": "2025-03-15",
            "due_date": "2025-04-14",
            "outstanding_amount": 22000.00,
            "currency": "USD",
            "days_overdue": 72,
            "prior_contact_count": 2,
            "credit_limit": 50000.00,
            "total_exposure": 22000.00,
        },
        {
            "customer_id": "CUST-005",
            "customer_name": "Echo Systems",
            "invoice_number": "INV-2025-0180",
            "invoice_date": "2025-02-10",
            "due_date": "2025-03-12",
            "outstanding_amount": 85000.00,
            "currency": "USD",
            "days_overdue": 97,
            "prior_contact_count": 3,
            "credit_limit": 100000.00,
            "total_exposure": 120000.00,
        },
        {
            "customer_id": "CUST-006",
            "customer_name": "Frontier Corp",
            "invoice_number": "INV-2025-0201",
            "invoice_date": "2025-04-25",
            "due_date": "2025-05-20",
            "outstanding_amount": 4200.00,
            "currency": "USD",
            "days_overdue": 35,
            "prior_contact_count": 0,
            "credit_limit": 50000.00,
            "total_exposure": 4200.00,
        },
    ],
    indent=2,
)

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

with gr.Blocks(title="AR Collection Agent") as demo:
    gr.Markdown(
        "# AR Collection Agent\n"
        "Paste a JSON array of customer records. The agent classifies each into an aging bucket "
        "(deterministic), then generates a tone-calibrated collection letter via the selected model."
    )

    with gr.Row():
        with gr.Column(scale=2):
            customer_input = gr.Textbox(
                label="Customer Data (JSON array)",
                lines=20,
                placeholder=(
                    "[\n"
                    "  {\n"
                    "    \"customer_id\": \"CUST-001\",\n"
                    "    \"customer_name\": \"Example Co\",\n"
                    "    \"invoice_number\": \"INV-2025-0001\",\n"
                    "    \"invoice_date\": \"2025-05-01\",\n"
                    "    \"due_date\": \"2025-05-31\",\n"
                    "    \"outstanding_amount\": 15000.00,\n"
                    "    \"currency\": \"USD\",\n"
                    "    \"days_overdue\": 24,\n"
                    "    \"prior_contact_count\": 0,\n"
                    "    \"credit_limit\": 50000.00,\n"
                    "    \"total_exposure\": 15000.00\n"
                    "  }\n"
                    "]"
                ),
            )
        with gr.Column(scale=1):
            as_of_date_input = gr.Textbox(
                label="As of Date (YYYY-MM-DD)",
                value="2025-06-24",
            )
            model_dropdown = gr.Dropdown(
                choices=MODELS,
                value=MODELS[0],
                label="Model",
            )
            run_btn = gr.Button("Generate Collection Plan", variant="primary")

    gr.Markdown("## Collection Plan")

    actions_table = gr.Dataframe(
        headers=["Customer", "Bucket", "Tier", "Amount", "Priority", "Credit Hold"],
        label="Actions (sorted by priority)",
        interactive=False,
    )

    with gr.Row():
        credit_hold_out = gr.Number(label="Credit Hold Count", precision=0)
        legal_referral_out = gr.Number(label="Legal Referral Count", precision=0)

    summary_out = gr.Textbox(label="Collection Summary", lines=3, interactive=False)

    gr.Examples(
        examples=[[EXAMPLE_CUSTOMERS_JSON, "2025-06-24", MODELS[0]]],
        inputs=[customer_input, as_of_date_input, model_dropdown],
        label="Example: 6 customers across all aging buckets",
    )

    run_btn.click(
        fn=generate_plan,
        inputs=[customer_input, as_of_date_input, model_dropdown],
        outputs=[actions_table, credit_hold_out, legal_referral_out, summary_out],
    )

if __name__ == "__main__":
    demo.launch()
