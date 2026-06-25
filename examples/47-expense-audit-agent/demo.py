"""Gradio demo for the Expense Audit Agent (via OpenRouter)."""

import os

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from src.schema import AuditResult
from src.tools import POLICY

load_dotenv()

MODELS = [
    "openai/gpt-5.4-nano",
    "openai/gpt-4.1-nano",
    "anthropic/claude-haiku-4-5",
]

# ---------------------------------------------------------------------------
# System prompt with POLICY injected at module load time
# ---------------------------------------------------------------------------

_POLICY_SUMMARY = (
    f"Meal limits: tier-1 cities {POLICY['meal_limits']['tier_1']['cities']} "
    f"${POLICY['meal_limits']['tier_1']['daily_limit']}/day, "
    f"tier-2 cities {POLICY['meal_limits']['tier_2']['cities']} "
    f"${POLICY['meal_limits']['tier_2']['daily_limit']}/day, "
    f"default ${POLICY['meal_limits']['default']['daily_limit']}/day. "
    f"Accommodation limits: tier-1 ${POLICY['accommodation_limits']['tier_1']['nightly']}/night, "
    f"tier-2 ${POLICY['accommodation_limits']['tier_2']['nightly']}/night, "
    f"default ${POLICY['accommodation_limits']['default']['nightly']}/night. "
    f"Receipt required above ${POLICY['receipt_threshold']}. "
    f"Entertainment limit: ${POLICY['entertainment_limit']} per event. "
    f"Equipment limit: ${POLICY['equipment_limit']} per item. "
    f"Business/first-class travel requires pre-approval."
)

SYSTEM_PROMPT = (
    "You are a corporate T&E expense auditor. "
    "Evaluate each expense line against the policy limits below and generate a "
    "PolicyViolation for every breach.\n\n"
    f"POLICY:\n{_POLICY_SUMMARY}\n\n"
    "Severity: info=minor note, warn=approver review required, block=cannot approve as-is.\n"
    "Rule IDs: MEAL-001 HOTEL-002 TRAVEL-003 RECEIPT-001 ENT-001 EQUIP-001.\n\n"
    "Approval routing: no violations->auto_approve; info/warn only->line_manager; "
    "any block + total<5000->finance_director; "
    "block + total>=5000 OR missing receipt above threshold->rejected.\n\n"
    "Return a complete AuditResult."
)

# ---------------------------------------------------------------------------
# Example inputs
# ---------------------------------------------------------------------------

EXAMPLE_CLEAN = (
    "Report: EXP-2025-001 | Employee: Alice Chen\n"
    "L01: transport, $380, NYC, economy flight NYC return, receipt=yes, pre_approved=yes, economy\n"
    "L02: accommodation, $320, NYC, hotel stay 1 night, receipt=yes\n"
    "L03: meals, $95, NYC, team working lunch, receipt=yes\n"
    "L04: transport, $35, NYC, taxi to client office, receipt=yes"
)

EXAMPLE_VIOLATIONS = (
    "Report: EXP-2025-002 | Employee: Bob Kumar\n"
    "L01: transport, $3200, NYC, business class flight, receipt=yes, pre_approved=no, business\n"
    "L02: accommodation, $420, NYC, hotel above limit, receipt=yes\n"
    "L03: meals, $150, NYC, client dinner over limit, receipt=yes\n"
    "L04: entertainment, $280, NYC, client event, receipt=yes\n"
    "L05: equipment, $620, NYC, laptop, receipt=yes"
)

# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------


def audit(report_description: str, model: str):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )

    model_id = model.split("/", 1)[-1] if "/" in model else model

    try:
        resp = client.beta.chat.completions.parse(
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": report_description},
            ],
            response_format=AuditResult,
        )
    except Exception as exc:
        return [], 0, 0, "error", f"API error: {exc}"

    result = resp.choices[0].message.parsed
    if result is None:
        return [], 0, 0, "error", "No structured response returned."

    violation_rows = [
        [v.line_id, v.rule_id, v.severity, v.violation_detail]
        for v in result.violations
    ]

    return (
        violation_rows,
        result.compliant_lines,
        result.violation_lines,
        result.approval_tier,
        result.audit_summary,
    )


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

with gr.Blocks(title="Expense Audit Agent") as demo:
    gr.Markdown("# Expense Audit Agent")
    gr.Markdown(
        "Describe an employee expense report in plain text. "
        "The agent evaluates each line against the configured T&E policy and "
        "routes the report to the correct approval tier."
    )

    with gr.Row():
        with gr.Column(scale=2):
            report_input = gr.Textbox(
                label="Expense Report Description",
                lines=10,
                placeholder="Report ID, employee name, and one expense line per line...",
                value=EXAMPLE_CLEAN,
            )
            model_dropdown = gr.Dropdown(
                label="Model",
                choices=MODELS,
                value=MODELS[0],
            )
            run_btn = gr.Button("Audit Report", variant="primary")

        with gr.Column(scale=3):
            violations_df = gr.Dataframe(
                headers=["Line", "Rule", "Severity", "Detail"],
                label="Policy Violations",
            )
            with gr.Row():
                compliant_out = gr.Number(label="Compliant Lines")
                violation_count_out = gr.Number(label="Violation Lines")
            approval_tier_out = gr.Textbox(label="Approval Tier")
            summary_out = gr.Textbox(label="Audit Summary", lines=4)

    run_btn.click(
        fn=audit,
        inputs=[report_input, model_dropdown],
        outputs=[
            violations_df,
            compliant_out,
            violation_count_out,
            approval_tier_out,
            summary_out,
        ],
    )

    gr.Examples(
        examples=[
            [EXAMPLE_CLEAN, MODELS[0]],
            [EXAMPLE_VIOLATIONS, MODELS[0]],
        ],
        inputs=[report_input, model_dropdown],
        label="Load Example",
    )

if __name__ == "__main__":
    demo.launch()
