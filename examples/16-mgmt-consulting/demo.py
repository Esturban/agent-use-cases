"""Gradio demo — Cost Optimization Assessment via OpenRouter structured output."""

import os
import sys

import gradio as gr
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(raise_error_if_not_found=False))

sys.path.insert(0, os.path.dirname(__file__))
from src.schema import CostOptimizationReport  # noqa: E402

SYSTEM_PROMPT = (
    "You are a senior management consultant conducting an operational cost optimization review "
    "for a client in Saudi Arabia. Analyse the operational profile and identify inefficiencies. "
    "For each one:\n"
    "1. Classify EFFORT: low / medium / high\n"
    "2. Classify IMPACT (savings potential): low / medium / high\n"
    "3. Assign quadrant — effort=low+impact=high → quick_win; effort=high+impact=high → major_project; "
    "effort=low+impact=low → fill_in; effort=high+impact=low → thankless_task. "
    "Treat medium effort as low, medium impact as high.\n"
    "4. Estimate annual saving in SAR where the brief provides enough data to support a credible estimate.\n"
    "5. List 3-5 concrete, actionable implementation steps.\n"
    "Sort quick_wins first. Write a 3-4 sentence executive_summary for a C-suite audience "
    "and a prioritization_note that recommends exactly where to start and why."
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

SAMPLE_BRIEF = """OPERATIONAL REVIEW — MAJD DEVELOPMENT COMPANY
Saudi real estate developer — residential and mixed-use projects, Riyadh & Eastern Province
Revenue: SAR 285m | Headcount: 215 (45 project managers, 80 technical, 60 commercial, 30 support)
Vision 2030 context: company holds 3 active government-linked housing contracts

CURRENT STATE OBSERVATIONS:

1. PROJECT COST CONTROL
Milestone claims submitted manually by PMs to finance via email. Reconciliation across 12 active
projects takes the finance team 8 days/month. Cost overrun rate: 22% of project value
(industry benchmark: 8-12%). Client invoicing delayed average 31 days post-milestone sign-off.
No real-time cost dashboard; CFO relies on monthly Excel summaries from each PM.

2. SUBCONTRACTOR MANAGEMENT
47 active subcontractors across 12 projects. No centralised contract repository — each PM
maintains own WhatsApp groups and personal Excel trackers. Duplicate subcontractors found
engaged by different PMs at different rates for the same scope. Estimated 15% of subcontractor
spend (SAR 6.8m/year) going to duplicates or unapproved vendors.

3. SAUDIZATION (NITAQAT) COMPLIANCE REPORTING
Current Saudi national ratio: 31% against a Platinum target of 35%. Monthly HRDF reporting done
manually by HR team — takes 3 working days per submission. Two Nitaqat penalties in 2024
totalling SAR 180,000 due to late or incorrect submissions. No early-warning system when ratio
drops below threshold.

4. PROCUREMENT
No enforced approved vendor list. Department heads procure independently without central
oversight. Internal audit found SAR 2.3m in single-source procurement in Q1 2025 alone.
No framework agreements with key material suppliers despite SAR 45m annual material spend.
No volume rebates negotiated.

5. PROJECT STATUS REPORTING
Weekly project reports produced manually in PowerPoint by each of the 45 PMs: approximately
90 hours/week in report production. Board receives 45 inconsistent formats with no aggregated
view. Senior leadership cannot identify which projects are at risk without reading every report.

6. FLEET & EQUIPMENT UTILISATION
68 company vehicles and 23 pieces of heavy equipment tracked via paper logs. Average vehicle
utilisation: 52% against a 75% target. No GPS tracking in place. Monthly fuel spend: SAR 185,000
with no usage-based reconciliation. Equipment downtime not measured.
"""

SAMPLE_BRIEF_2 = """OPERATIONAL REVIEW — WAJD ADVISORY GROUP
Saudi management consultancy — Vision 2030 strategy and transformation advisory, Riyadh
Revenue: SAR 42m | Headcount: 67 (22 consultants, 18 senior associates, 10 analysts, 17 support)

CURRENT STATE OBSERVATIONS:

1. BILLABLE HOURS & INVOICING
Timesheets submitted informally via WhatsApp to finance. Manual entry takes 4 working days/month.
Write-off rate: 21% (benchmark for boutique advisory: 8-12%). Average invoice delay: 27 days
post-project completion. No automated time-capture system in use.

2. KNOWLEDGE MANAGEMENT
All client deliverables stored in individual consultant OneDrive folders. No firm-wide knowledge
repository. Arabic/English bilingual documents not tagged or searchable. Estimated 35% of new
proposal time spent recreating content that exists somewhere in the firm.

3. BILLABLE UTILISATION
58% billable utilisation against a 72% target. Principals allocate projects informally via
WhatsApp and personal memory. 4 consultants billed zero hours in Q1 2025. No real-time
utilisation dashboard.

4. ARABIC TRANSLATION COSTS
SAR 280,000/year spent on external translation of client deliverables into Arabic. Internal
bilingual capacity exists but is not systematically deployed. Translation turnaround adds
3-5 days to every deliverable.

5. SAUDIZATION (NITAQAT)
38% Saudi national staff (currently Platinum). 3 Saudi nationals hired in Q4 2024 resigned
within 6 months. No structured graduate or training pathway to build a sustainable Saudi pipeline.
Retention cost of replacement: estimated SAR 45,000 per hire.

6. TRAVEL & ACCOMMODATION
Riyadh-to-Jeddah flights booked at short notice. Average ticket: SAR 1,850 (advance booking:
SAR 420). No consolidated hotel rates or preferred supplier agreements. Annual travel budget
overrun: SAR 340,000 against plan.
"""


def _format_recs(recs: list) -> str:
    if not recs:
        return "_None identified._"
    lines = []
    for r in recs:
        saving = f" · Est. saving: **{r.estimated_annual_saving}**" if r.estimated_annual_saving else ""
        lines.append(
            f"**{r.title}** ({r.category} · effort={r.effort} · impact={r.impact}){saving}\n\n"
            f"{r.rationale}\n\n"
            "Steps: " + " → ".join(r.implementation_steps)
        )
    return "\n\n---\n\n".join(lines)


def run_assessment(brief: str, model: str):
    if not brief.strip():
        return "", "", "", "", "", ""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise gr.Error("OPENAI_API_KEY is not set — set OPENAI_API_KEY in your shell environment.")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": brief},
        ],
        response_format=CostOptimizationReport,
    )
    r: CostOptimizationReport = completion.choices[0].message.parsed
    saving = r.total_addressable_saving or "Not quantified"
    return (
        saving,
        r.executive_summary,
        _format_recs(r.quick_wins),
        _format_recs(r.major_projects),
        _format_recs(r.fill_ins),
        r.prioritization_note,
    )


with gr.Blocks(title="Cost Optimization Assessment") as demo:
    gr.Markdown(
        "## Cost Optimization Assessment\n"
        "Describe your company's operational challenges in plain language — "
        "headcount, processes, costs, and where time is being wasted. "
        "The AI acts as a senior management consultant, identifies the inefficiencies, "
        "and delivers a prioritized action plan with SAR savings estimates.\n\n"
        "**Who this is for:** CEOs, COOs, and strategy teams who want a structured view of "
        "where money is being lost before committing to a full consulting engagement. "
        "Useful for Vision 2030 transformation programs, privatization readiness, and pre-investment operational reviews."
    )

    with gr.Accordion("How the AI prioritizes recommendations", open=True):
        gr.Markdown(
            "Not every operational fix is worth the same effort. The AI classifies every finding "
            "on two dimensions — how hard it is to implement, and how much value it unlocks — "
            "then places it in one of four categories:\n\n"
            "| | **High Savings Potential** | **Low Savings Potential** |\n"
            "|---|---|---|\n"
            "| **Easy to implement** | 🟢 **Quick Win** — do this first | 🔵 **Fill-in** — do when capacity allows |\n"
            "| **Hard to implement** | 🟡 **Major Project** — plan and resource properly | 🔴 **Thankless Task** — avoid or deprioritise |\n\n"
            "Quick Wins come first — they deliver real savings without needing a transformation programme. "
            "Major Projects need a business case and dedicated resource. "
            "The AI estimates annual savings in SAR wherever the brief contains enough data.\n\n"
            "_Sample 1: Majd Development Company — Saudi real estate developer, SAR 285m revenue. "
            "Issues: subcontractor spend, Nitaqat compliance, project cost overruns, fleet utilisation._\n\n"
            "_Sample 2: Wajd Advisory Group — Riyadh-based management consultancy, SAR 42m revenue. "
            "Issues: billable hour leakage, Arabic translation costs, Saudization retention, travel spend._"
        )

    with gr.Row():
        with gr.Column(scale=2):
            brief_input = gr.Textbox(
                label="Operational profile",
                lines=22,
                placeholder=(
                    "Describe your company — sector, headcount, revenue — then list the operational "
                    "issues you are facing. Be specific: name the process, how long it takes, "
                    "what it costs, and what the gap is versus where you want to be. "
                    "The more detail you give, the more accurate the savings estimates will be."
                ),
                value=SAMPLE_BRIEF,
            )
            model_dd = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Run Assessment", variant="primary")
            gr.Examples(
                examples=[[SAMPLE_BRIEF], [SAMPLE_BRIEF_2]],
                inputs=[brief_input],
                label="Sample profiles — click to load",
            )

        with gr.Column(scale=3):
            saving_out = gr.Textbox(
                label="Total addressable saving (SAR, annual)",
                interactive=False,
            )
            summary_out = gr.Textbox(
                label="Executive summary",
                lines=4,
                interactive=False,
            )
            gr.Markdown("#### 🟢 Quick Wins — high savings, low effort. Do these first.")
            quick_out = gr.Markdown()
            gr.Markdown("#### 🟡 Major Projects — high savings, requires a project plan.")
            major_out = gr.Markdown()
            gr.Markdown("#### 🔵 Fill-ins — low-effort housekeeping. Do when capacity allows.")
            fill_out = gr.Markdown()
            priority_out = gr.Textbox(
                label="Where to start — the AI's recommended first move",
                lines=3,
                interactive=False,
            )

    run_btn.click(
        fn=run_assessment,
        inputs=[brief_input, model_dd],
        outputs=[saving_out, summary_out, quick_out, major_out, fill_out, priority_out],
    )

if __name__ == "__main__":
    demo.launch()
