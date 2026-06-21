"""Gradio demo — Board Pack Reviewer via OpenRouter structured output."""

import os
import sys

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))
from src.schema import DirectorBriefing  # noqa: E402

SYSTEM_PROMPT = (
    "You are an experienced non-executive director reviewing a board pack before a meeting. "
    "Produce a structured briefing that helps fellow directors cut through management language "
    "and focus on what actually matters.\n\n"
    "Rules:\n"
    "- Frame every risk as a board concern, not a management update\n"
    "- Name information gaps explicitly — 'the pack does not disclose X' is more useful than silence\n"
    "- Questions for management must be probing: challenge assumptions, not process\n"
    "- overall_pack_quality reflects governance fitness, not length or formatting\n"
    "- If something looks sanitised or is missing context, say so\n\n"
    "You serve shareholders and stakeholders, not management."
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

SAMPLE_PACK = """MERIDIAN CAPITAL GROUP PLC
BOARD OF DIRECTORS — MEETING 18 JUNE 2025
STRICTLY CONFIDENTIAL

1. FINANCIAL PERFORMANCE — Q1 2025
Revenue: GBP 28.4m (budget: GBP 31.2m, -9%)
EBITDA: GBP 3.1m (budget: GBP 4.8m, -35%)
Cash: GBP 6.2m (Dec 2024: GBP 9.4m) — burn rate accelerating
Three clients (representing 22% of revenue) have invoked contract review clauses.

2. STRATEGIC UPDATE — PROJECT ATLAS
The previously approved acquisition of DataBridge Ltd (EV: GBP 45m) is proceeding.
Completion expected Q3 2025. Integration planning has not commenced pending completion.
DataBridge FY2024 results: revenue GBP 8.1m (+42% YoY), EBITDA GBP (0.6m) — pre-profitability.

3. RISK REGISTER (management update)
Top risks: market conditions, talent retention, regulatory change. No new risks added.
All risks rated 'managed'. No escalations since last meeting.

4. PEOPLE
CFO resignation accepted effective 31 July 2025. Interim CFO search underway.
Three senior client managers departed in April. Exit interview data not yet available.

5. RESOLUTIONS REQUIRED
5.1 Approve revised Q2 budget (revised down 18% from approved plan)
5.2 Approve DataBridge acquisition — proceed to legal completion
5.3 Approve CFO interim appointment (candidate details in appendix — NOT included in this pack)
"""

QUALITY_LABEL = {
    "strong": "✅ Strong",
    "adequate": "🟡 Adequate",
    "weak": "🔴 Weak",
}

SEVERITY_ICON = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
}


def _format_risks(risks: list) -> str:
    if not risks:
        return "_No material risks identified._"
    lines = []
    for r in sorted(risks, key=lambda x: x.rank):
        icon = SEVERITY_ICON.get(r.severity, "")
        lines.append(
            f"**{r.rank}. {icon} {r.title}** ({r.area} · {r.severity})\n\n"
            f"{r.detail}\n\n"
            f"*Source: {r.source_section}*\n\n"
            f"**NED question:** _{r.suggested_question}_"
        )
    return "\n\n---\n\n".join(lines)


def _format_gaps(gaps: list) -> str:
    if not gaps:
        return "_No material information gaps identified._"
    return "\n\n".join(
        f"**{g.section}:** {g.missing}\n_{g.why_it_matters}_" for g in gaps
    )


def _format_decisions(decisions: list) -> str:
    if not decisions:
        return "_No formal resolutions in this pack._"
    return "\n\n".join(
        f"**{d.item}**\n{d.context}\n"
        + (f"*Management recommendation: {d.recommendation}*\n" if d.recommendation else "")
        + f"**Key consideration:** {d.key_consideration}"
        for d in decisions
    )


def review_board_pack(pack_text: str, model: str):
    if not pack_text.strip():
        return "", "", "", "", "", ""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise gr.Error("OPENROUTER_API_KEY is not set — add it to your .env file.")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Board pack to review:\n\n" + pack_text},
        ],
        response_format=DirectorBriefing,
    )
    r: DirectorBriefing = completion.choices[0].message.parsed
    questions = "\n".join(f"• {q}" for q in r.questions_for_management)
    return (
        QUALITY_LABEL.get(r.overall_pack_quality, r.overall_pack_quality),
        r.executive_assessment,
        _format_risks(r.top_risks),
        _format_gaps(r.information_gaps),
        _format_decisions(r.decisions_required),
        questions,
    )


with gr.Blocks(title="Board Pack Reviewer") as demo:
    gr.Markdown(
        "## 📋 Board Pack Reviewer\n"
        "Paste a board pack → the model produces a NED briefing: top risks ranked by severity, "
        "information gaps, decisions required, and probing questions for management.\n\n"
        "**Built for:** non-executive directors, chairs, and governance advisors who need to cut "
        "through management language before walking into the boardroom."
    )

    with gr.Accordion("What this produces", open=True):
        gr.Markdown(
            "The model acts as an experienced NED and returns four structured outputs:\n\n"
            "| Output | What it tells you |\n"
            "|--------|-------------------|\n"
            "| **Top risks** | Up to 5 risks ranked by severity — framed as board concerns, "
            "not management euphemisms. Each includes a suggested NED question. |\n"
            "| **Information gaps** | Material information absent from the pack that the board "
            "needs before deciding. |\n"
            "| **Decisions required** | Items requiring board approval with key considerations "
            "and management's recommendation. |\n"
            "| **Questions for management** | Probing questions — challenging assumptions, not process. |\n\n"
            "_Sample: Meridian Capital Group — revenue miss, accelerating cash burn, CFO departure, "
            "a GBP 45m acquisition pending, and a risk register showing zero escalations. "
            "Something doesn't add up._"
        )

    with gr.Row():
        with gr.Column(scale=2):
            pack_input = gr.Textbox(
                label="Board pack text",
                lines=22,
                placeholder="Paste the board pack content here…",
                value=SAMPLE_PACK,
            )
            model_dd = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Review Board Pack", variant="primary")

        with gr.Column(scale=3):
            quality_out = gr.Textbox(label="Pack quality", interactive=False)
            assessment_out = gr.Textbox(label="5-minute NED briefing", lines=4, interactive=False)
            gr.Markdown("#### Top Risks")
            risks_out = gr.Markdown()
            gr.Markdown("#### Information Gaps")
            gaps_out = gr.Markdown()
            gr.Markdown("#### Decisions Required")
            decisions_out = gr.Markdown()
            questions_out = gr.Textbox(
                label="Questions for management", lines=6, interactive=False
            )

    run_btn.click(
        fn=review_board_pack,
        inputs=[pack_input, model_dd],
        outputs=[quality_out, assessment_out, risks_out, gaps_out, decisions_out, questions_out],
    )

if __name__ == "__main__":
    demo.launch()
