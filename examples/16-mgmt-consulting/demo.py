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
    "You are a management consultant conducting a cost optimization review. "
    "Analyse the operational profile and identify inefficiencies. For each one:\n"
    "1. Classify EFFORT: low / medium / high\n"
    "2. Classify IMPACT (savings potential): low / medium / high\n"
    "3. Assign quadrant — effort=low+impact=high → quick_win; effort=high+impact=high → major_project; "
    "effort=low+impact=low → fill_in; effort=high+impact=low → thankless_task. "
    "Treat medium effort as low, medium impact as high.\n"
    "4. Estimate annual saving in GBP where data supports it.\n"
    "5. List 3-5 concrete implementation steps.\n"
    "Sort quick_wins first. Provide a 3-4 sentence executive_summary and prioritization_note."
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

SAMPLE_BRIEF = """OPERATIONAL REVIEW — HARTWELL PARTNERS LLP
Professional services firm (management consulting boutique)
Revenue: GBP 6.4m | Headcount: 28 (12 fee-earners, 8 senior associates, 8 support)

CURRENT STATE OBSERVATIONS:
1. BILLING: Timesheets submitted weekly via email to finance. Manual entry to Xero takes finance team ~2 days/month. Write-off rate: 18% (industry benchmark: 8-12%). Invoicing delayed average 23 days post-project completion.

2. KNOWLEDGE MANAGEMENT: Project deliverables stored in individual consultant Dropbox folders. No central repository. Estimated 30% of new proposal time spent recreating slides that exist somewhere in the firm.

3. UTILISATION: Average utilisation 61% (target: 75%). No real-time visibility. Partner allocates projects via WhatsApp and memory. Three consultants billed zero hours in March.

4. PROCUREMENT: Each partner negotiates own software subscriptions. Audit found 14 SaaS tools, 6 with <2 active users. Annual SaaS spend: GBP 94k.

5. RECRUITMENT: Average time-to-hire: 87 days. Three roles open >6 months. No ATS in use — CVs tracked in shared Excel file.

6. CLIENT REPORTING: Monthly client reports produced manually in PowerPoint. Each takes 3-4 hours. 24 active clients = 72-96 hours/month in report production.
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
        "## 💰 Cost Optimization Assessment\n"
        "Paste an operational profile → the model identifies inefficiencies, "
        "classifies each by effort vs. impact, and delivers a prioritized action plan with GBP savings estimates.\n\n"
        "**Built for:** CEOs, COOs, and strategy teams who need a structured first-cut optimization "
        "roadmap before committing to a full consulting engagement."
    )

    with gr.Accordion("2×2 Effort–Impact framework", open=True):
        gr.Markdown(
            "Every finding is classified on two axes and placed in a quadrant:\n\n"
            "| | **High Impact** | **Low Impact** |\n"
            "|---|---|---|\n"
            "| **Low Effort** | 🟢 **Quick Win** — do first | 🔵 Fill-in — do when free |\n"
            "| **High Effort** | 🟡 **Major Project** — plan carefully | 🔴 Thankless Task — avoid |\n\n"
            "The model estimates annual GBP savings where the brief provides enough data. "
            "Quick Wins surface first — highest ROI with lowest friction.\n\n"
            "_Sample: Hartwell Partners LLP — 28-person consulting boutique. "
            "Issues span billing, utilisation, knowledge management, SaaS sprawl, and client reporting._"
        )

    with gr.Row():
        with gr.Column(scale=2):
            brief_input = gr.Textbox(
                label="Operational profile",
                lines=20,
                placeholder="Paste your operational review notes — headcount, processes, costs, inefficiencies…",
                value=SAMPLE_BRIEF,
            )
            model_dd = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Run Assessment", variant="primary")

        with gr.Column(scale=3):
            saving_out = gr.Textbox(label="Total addressable saving", interactive=False)
            summary_out = gr.Textbox(label="Executive summary", lines=4, interactive=False)
            gr.Markdown("#### 🟢 Quick Wins (low effort, high impact)")
            quick_out = gr.Markdown()
            gr.Markdown("#### 🟡 Major Projects (high effort, high impact)")
            major_out = gr.Markdown()
            gr.Markdown("#### 🔵 Fill-ins (low effort, low impact)")
            fill_out = gr.Markdown()
            priority_out = gr.Textbox(label="Where to start", lines=2, interactive=False)

    run_btn.click(
        fn=run_assessment,
        inputs=[brief_input, model_dd],
        outputs=[saving_out, summary_out, quick_out, major_out, fill_out, priority_out],
    )

if __name__ == "__main__":
    demo.launch()
