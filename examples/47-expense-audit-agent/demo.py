"""Gradio demo — Expense Audit Agent via OpenRouter."""

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
# 47 · Expense Audit Agent
Audit employee expense reports against a **configurable T&E policy** and route to the correct approval tier.

> **Harness concept — policy rule engine:** Policy limits live in a `POLICY` dict in `tools.py`, not hardcoded in the prompt.
> Updating meal limits means editing the dict — zero prompt changes required.
> The LLM evaluates lines against the injected policy context. Approval routing is fully deterministic.
"""

TIER_COLORS = {
    "auto_approve": "badge-green",
    "line_manager": "badge-blue",
    "finance_director": "badge-orange",
    "rejected": "badge-red",
}

SEV_EMOJI = {"info": "🔵 info", "warn": "🟡 warn", "block": "🔴 block"}

_POLICY_SUMMARY = (
    f"Meal limits — tier-1 cities {POLICY['meal_limits']['tier_1']['cities']}: "
    f"${POLICY['meal_limits']['tier_1']['daily_limit']}/day | "
    f"tier-2 cities {POLICY['meal_limits']['tier_2']['cities']}: "
    f"${POLICY['meal_limits']['tier_2']['daily_limit']}/day | "
    f"default: ${POLICY['meal_limits']['default']['daily_limit']}/day. "
    f"Accommodation — tier-1: ${POLICY['accommodation_limits']['tier_1']['nightly']}/night | "
    f"tier-2: ${POLICY['accommodation_limits']['tier_2']['nightly']}/night | "
    f"default: ${POLICY['accommodation_limits']['default']['nightly']}/night. "
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
    "Approval routing: no violations → auto_approve; info/warn only → line_manager; "
    "any block + total < 5000 → finance_director; "
    "block + total >= 5000 OR missing receipt above threshold → rejected.\n\n"
    "Return a complete AuditResult."
)

EXAMPLE_CLEAN = """\
Report: EXP-2025-001 | Employee: Alice Chen | Total claimed: $830
L01: transport, $380, NYC, economy flight NYC return, receipt=yes, pre_approved=yes, economy
L02: accommodation, $320, NYC, hotel 1 night, receipt=yes
L03: meals, $95, NYC, team working lunch, receipt=yes
L04: transport, $35, NYC, taxi to client office, receipt=yes"""

EXAMPLE_VIOLATIONS = """\
Report: EXP-2025-002 | Employee: Bob Kumar | Total claimed: $4,670
L01: transport, $3200, NYC, business class flight, receipt=yes, pre_approved=no, business
L02: accommodation, $420, NYC, hotel above limit, receipt=yes
L03: meals, $150, NYC, client dinner over limit, receipt=yes
L04: entertainment, $280, NYC, client event, receipt=yes
L05: equipment, $620, NYC, laptop purchase, receipt=yes"""


def audit(report_description: str, model: str):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )

    try:
        resp = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": report_description},
            ],
            response_format=AuditResult,
        )
    except Exception as exc:
        return [], 0, 0, '<span class="badge badge-red">ERROR</span>', f"API error: {exc}"

    result = resp.choices[0].message.parsed
    if result is None:
        return [], 0, 0, '<span class="badge badge-red">ERROR</span>', "No structured response."

    violation_rows = [
        [v.line_id, v.rule_id, SEV_EMOJI.get(v.severity, v.severity), v.violation_detail]
        for v in result.violations
    ]

    tier_cls = TIER_COLORS.get(result.approval_tier, "badge-gray")
    tier_html = f'<span class="badge {tier_cls}">{result.approval_tier.replace("_", " ").title()}</span>'

    return (
        violation_rows,
        result.compliant_lines,
        result.violation_lines,
        tier_html,
        result.audit_summary,
    )


with gr.Blocks(title="Expense Audit Agent", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(HEADER)

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### Expense Report")
            report_input = gr.Textbox(
                label="Report Description",
                lines=10,
                placeholder=(
                    "Report: EXP-YYYY-NNN | Employee: Name | Total claimed: $X\n"
                    "L01: category, amount, city, description, receipt=yes/no, pre_approved=yes/no"
                ),
                value=EXAMPLE_CLEAN,
            )
            model_dropdown = gr.Dropdown(label="Model", choices=MODELS, value=MODELS[0])
            run_btn = gr.Button("Audit Report", variant="primary", size="lg")

        with gr.Column(scale=3):
            gr.Markdown("### Audit Result")
            violations_df = gr.Dataframe(
                headers=["Line", "Rule", "Severity", "Violation Detail"],
                label="Policy Violations",
                interactive=False,
                wrap=True,
            )
            with gr.Row():
                compliant_out = gr.Number(label="Compliant Lines", precision=0, interactive=False)
                violation_count_out = gr.Number(label="Violation Lines", precision=0, interactive=False)
            approval_tier_out = gr.HTML(label="Approval Tier")
            summary_out = gr.Textbox(label="Audit Summary", lines=4, interactive=False)

    run_btn.click(
        fn=audit,
        inputs=[report_input, model_dropdown],
        outputs=[violations_df, compliant_out, violation_count_out, approval_tier_out, summary_out],
    )

    gr.Markdown("---\n### Try an example")
    gr.Examples(
        examples=[
            [EXAMPLE_CLEAN, MODELS[0]],
            [EXAMPLE_VIOLATIONS, MODELS[0]],
        ],
        inputs=[report_input, model_dropdown],
        label="Clean report (auto-approve) · Violations report (finance director)",
    )

if __name__ == "__main__":
    demo.launch()
