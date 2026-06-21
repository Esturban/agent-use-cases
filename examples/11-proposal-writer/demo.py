"""Gradio demo — RFP Proposal Writer via OpenRouter structured output."""

import os
import sys

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))
from src.schema import Proposal, ProposalOutline  # noqa: E402

SUPERVISOR_SYSTEM = (
    "You are a proposal director reviewing an RFP before your team drafts a response.\n\n"
    "Produce a structured decomposition of the RFP:\n"
    "1. Extract every requirement, marking which are mandatory pass/fail criteria\n"
    "2. Identify 2-4 win themes — strategic angles that should run through the whole proposal\n"
    "3. Identify how the client will evaluate and score proposals\n"
    "4. List the sections the proposal should contain, in order\n\n"
    "Be precise. Requirements you miss now become compliance failures later."
)

WRITER_SYSTEM = (
    "You are a senior proposal writer crafting a winning RFP response.\n\n"
    "You will receive the original RFP text and a structured outline (win themes, requirements, "
    "evaluation criteria, sections to write).\n\n"
    "Your draft must:\n"
    "- Lead every section with the client's problem, not your firm's capabilities\n"
    "- Weave the win themes consistently through all sections\n"
    "- Be specific about methodology — no generic consulting language\n"
    "- Address all mandatory requirements explicitly in the compliance_statement\n"
    "- Keep the executive_summary under 200 words and punchy\n\n"
    "Write to win, not to comply."
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

SAMPLE_RFP = """REQUEST FOR PROPOSAL — DIGITAL TRANSFORMATION ADVISORY

Issuing organisation: MidlandsGrid PLC (energy distribution, 2,400 employees)
Submission deadline: 30 July 2025
Project value: GBP 1.2m — 18-month engagement

BACKGROUND
MidlandsGrid is replacing its 15-year-old SAP ECC platform with SAP S/4HANA. The legacy system
cannot support real-time grid operations data or the renewable energy forecasting modules required
under the UK Energy Act 2023. The project must be complete before the statutory reporting
deadline of 1 April 2027.

SCOPE OF WORK
1. Programme management and governance framework
2. Business process re-engineering for Finance, Operations, and Asset Management
3. Data migration strategy (estimated 12TB, 8 source systems)
4. Change management and training (2,400 end users)
5. Integration design for 14 third-party systems

MANDATORY REQUIREMENTS (pass/fail)
M1. ISO 27001 certified or equivalent evidence of information security management
M2. Minimum 3 completed SAP S/4HANA implementations in regulated utilities
M3. UK-based delivery team for all client-facing activities
M4. Named Project Director with 10+ years SAP transformation experience

EVALUATION CRITERIA (weighted)
Technical approach: 35%
Relevant experience: 30%
Commercial: 25%
Social value: 10%

SUBMISSION FORMAT
Executive summary (max 2 pages), technical approach, team CVs, case studies, commercial schedule
"""

SAMPLE_RFP_2 = """REQUEST FOR PROPOSAL — COMMERCIAL DUE DILIGENCE ADVISORY

Issuing organisation: Apex Growth Partners (mid-market PE fund)
Target: SaaS business in HR tech, GBP 45m EV
Deadline: 18 July 2025

BACKGROUND
Apex is evaluating a Series C investment in a UK-based HR onboarding automation platform.
They require a commercial due diligence advisor to validate the investment thesis and identify risks
before exclusivity is signed. The assignment must be completed within 3 weeks.

SCOPE
1. Market sizing and growth validation (TAM, SAM, growth drivers)
2. Competitive landscape — current and emerging threats
3. Customer reference interviews (minimum 8 customers)
4. Revenue quality and churn analysis
5. Management team assessment
6. Red flag identification and risk register

MANDATORY REQUIREMENTS
M1. Previous CDD experience in B2B SaaS or HR tech
M2. Ability to start within 5 working days of award
M3. Named senior partner as day-to-day lead

EVALUATION CRITERIA
Quality of approach: 40% | Track record: 35% | Commercial: 25%
"""


def _format_outline(outline: ProposalOutline) -> str:
    reqs = "\n".join(
        f"{'**[MANDATORY]** ' if r.mandatory else ''}{r.section}: {r.requirement}"
        for r in outline.requirements
    )
    themes = "\n".join(f"• {t}" for t in outline.win_themes)
    criteria = "\n".join(f"• {c}" for c in outline.evaluation_criteria)
    sections = " → ".join(outline.sections_to_write)
    return (
        f"**Win themes:**\n{themes}\n\n"
        f"**Evaluation criteria:**\n{criteria}\n\n"
        f"**Requirements extracted ({len(outline.requirements)}):**\n{reqs}\n\n"
        f"**Sections to write:** {sections}"
    )


def write_proposal(rfp_text: str, model: str):
    if not rfp_text.strip():
        return "", "", "", "", "", "", "", ""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise gr.Error("OPENAI_API_KEY is not set — set OPENAI_API_KEY in your shell environment.")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    outline_completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SUPERVISOR_SYSTEM},
            {"role": "user", "content": rfp_text},
        ],
        response_format=ProposalOutline,
    )
    outline: ProposalOutline = outline_completion.choices[0].message.parsed

    writer_prompt = (
        f"RFP:\n{rfp_text}\n\n"
        f"Outline:\nWin themes: {', '.join(outline.win_themes)}\n"
        f"Evaluation criteria: {', '.join(outline.evaluation_criteria)}\n"
        f"Sections: {', '.join(outline.sections_to_write)}\n"
        "Mandatory requirements: "
        + "; ".join(r.requirement for r in outline.requirements if r.mandatory)
    )

    proposal_completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": WRITER_SYSTEM},
            {"role": "user", "content": writer_prompt},
        ],
        response_format=Proposal,
    )
    p: Proposal = proposal_completion.choices[0].message.parsed

    differentiators = "\n".join(f"• {d}" for d in p.key_differentiators)
    themes = " · ".join(p.win_themes)

    return (
        _format_outline(outline),
        themes,
        p.executive_summary,
        p.our_approach,
        p.team_and_credentials,
        p.commercial,
        differentiators,
        p.compliance_statement,
    )


with gr.Blocks(title="RFP Proposal Writer") as demo:
    gr.Markdown(
        "## 📝 RFP Proposal Writer\n"
        "Paste an RFP → the model produces a complete proposal in two steps: "
        "first it extracts requirements and win themes, then it drafts every section.\n\n"
        "**Built for:** bid teams, management consultants, and professional services firms "
        "who need a first-draft proposal in minutes, not days."
    )

    with gr.Accordion("2-step pipeline — how it works", open=True):
        gr.Markdown(
            "**Step 1 — Analyse (Supervisor):** reads the RFP and extracts every requirement "
            "(flagging mandatory pass/fail criteria), identifies 2-4 win themes, and determines "
            "how the client will score submissions.\n\n"
            "**Step 2 — Write (Writer):** uses the structured outline to draft all proposal sections — "
            "leading each with the client's problem, weaving win themes consistently, and producing "
            "a compliance statement that addresses every mandatory requirement explicitly.\n\n"
            "| Section produced | What it contains |\n"
            "|-----------------|------------------|\n"
            "| **Executive summary** | The win argument in under 200 words |\n"
            "| **Our approach** | Methodology and delivery phasing |\n"
            "| **Team & credentials** | Key personnel, relevant experience |\n"
            "| **Commercial** | Pricing structure and value drivers |\n"
            "| **Key differentiators** | 3-5 bullets for the cover slide |\n"
            "| **Compliance statement** | Explicit confirmation of every mandatory requirement |\n\n"
            "_Sample 1: MidlandsGrid PLC — SAP S/4HANA digital transformation, GBP 1.2m._\n"
            "_Sample 2: Apex Growth Partners — commercial due diligence for a SaaS PE deal._"
        )

    with gr.Row():
        with gr.Column(scale=2):
            rfp_input = gr.Textbox(
                label="RFP text",
                lines=24,
                placeholder="Paste the full RFP here…",
                value=SAMPLE_RFP,
            )
            model_dd = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Write Proposal", variant="primary")
            gr.Examples(
                examples=[[SAMPLE_RFP], [SAMPLE_RFP_2]],
                inputs=[rfp_input],
                label="Sample RFPs — click to load",
            )

        with gr.Column(scale=3):
            gr.Markdown("#### Step 1 — RFP Analysis")
            outline_out = gr.Markdown()
            gr.Markdown("#### Step 2 — Proposal Draft")
            themes_out = gr.Textbox(label="Win themes", interactive=False)
            exec_summary_out = gr.Textbox(label="Executive summary", lines=5, interactive=False)
            approach_out = gr.Textbox(label="Our approach", lines=5, interactive=False)
            team_out = gr.Textbox(label="Team & credentials", lines=4, interactive=False)
            commercial_out = gr.Textbox(label="Commercial", lines=4, interactive=False)
            differentiators_out = gr.Textbox(
                label="Key differentiators", lines=4, interactive=False
            )
            compliance_out = gr.Textbox(label="Compliance statement", lines=3, interactive=False)

    run_btn.click(
        fn=write_proposal,
        inputs=[rfp_input, model_dd],
        outputs=[
            outline_out,
            themes_out,
            exec_summary_out,
            approach_out,
            team_out,
            commercial_out,
            differentiators_out,
            compliance_out,
        ],
    )

if __name__ == "__main__":
    demo.launch()
