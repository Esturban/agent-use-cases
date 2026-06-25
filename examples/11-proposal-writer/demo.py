"""Gradio demo — RFP Proposal Writer via OpenRouter structured output."""

import os
import sys

import gradio as gr
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(raise_error_if_not_found=False))

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
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]

SAMPLE_RFP = """REQUEST FOR PROPOSAL — ENTERPRISE DIGITAL TRANSFORMATION ADVISORY

Issuing organisation: Saudi Electricity Company (SEC)
Reference: SEC-ICT-2025-0047
Submission deadline: 15 September 2025
Project value: SAR 18,000,000 — 24-month engagement
Language: Responses must be submitted in both Arabic and English

BACKGROUND
SEC operates the national power grid serving 10.5 million customers across the Kingdom of Saudi Arabia.
The company is executing its Digital Transformation Roadmap 2030, aligned with the National
Transformation Programme and Vision 2030 objectives. The current Oracle EBS financial management
system (deployed 2009) cannot support real-time operational analytics, predictive maintenance modules,
or ZATCA Phase 2 e-invoicing compliance required by Q4 2026.

SEC seeks an advisory partner to lead the transition to SAP S/4HANA Public Cloud and implement a
unified data platform integrating generation, transmission, and distribution operations.

SCOPE OF WORK
1. Programme governance and PMO establishment
2. Business process re-engineering for Finance, Procurement, and Asset Management (11,000 assets)
3. Data migration strategy (estimated 18TB across 6 legacy systems, including Arabic-language data)
4. Change management and capability building (14,000 end users across 12 regions)
5. ZATCA Phase 2 e-invoicing integration and SDAIA data governance compliance
6. Integration architecture for 22 third-party operational systems

MANDATORY REQUIREMENTS (pass/fail — automatic disqualification if not met)
M1. Valid NCA (National Cybersecurity Authority) Compliance Certificate or equivalent evidence
M2. SDAIA-approved data residency — all data must remain within the Kingdom of Saudi Arabia
M3. Minimum 3 completed SAP S/4HANA implementations in regulated energy or utilities in GCC or MENA
M4. Named Saudi-registered legal entity as prime contractor
M5. Nitaqat Platinum or Platinum+ rating (minimum 35% Saudi national employees on engagement)
M6. Named Programme Director with 12+ years ERP transformation experience

EVALUATION CRITERIA (weighted scoring)
Technical approach and methodology: 40%
Relevant GCC/MENA experience and reference projects: 30%
Commercial and value for money: 20%
Local content and Saudization plan: 10%

SUBMISSION FORMAT
Arabic executive summary (max 3 pages) + English technical response, team CVs, 3 GCC/MENA reference
case studies, commercial schedule in SAR, Saudization plan with Nitaqat evidence, IKTVA commitment letter
"""

SAMPLE_RFP_2 = """REQUEST FOR PROPOSAL — STRATEGIC ADVISORY: TOURISM INVESTMENT ATTRACTION

Issuing organisation: Royal Commission for AlUla (RCU)
Reference: RCU-STRAT-2025-0012
Submission deadline: 30 August 2025
Project value: SAR 6,500,000 — 12-month engagement

BACKGROUND
AlUla is being developed as Saudi Arabia's premier cultural and heritage tourism destination under
Vision 2030. RCU has committed to welcoming 250,000 visitors by 2026 and 2,000,000 by 2035.
To reach these targets, RCU requires a strategic advisory partner to design and execute an
international investment attraction programme targeting hospitality, entertainment, and eco-tourism
operators across Europe, Asia, and North America.

SCOPE OF WORK
1. International investor targeting — identify and qualify 50+ target operators and investors
2. Investment proposition design — develop RCU's value proposition for each investor segment
3. Roadshow execution — organise 3 international roadshows (London, Singapore, New York)
4. Anchor tenant negotiation support — advisory on term sheets for 5 priority development sites
5. Pipeline reporting — monthly investor pipeline dashboard for RCU senior leadership
6. All deliverables to be produced in Arabic and English

MANDATORY REQUIREMENTS
M1. Previous tourism investment attraction or destination advisory experience in GCC, MENA,
    or a comparable emerging market context
M2. Demonstrated relationships with international hotel operators in the 5-star and luxury segment
M3. Arabic-capable senior advisor named and committed to the engagement team
M4. Ability to mobilise fully within 10 working days of contract award

EVALUATION CRITERIA
Strategic approach and creativity: 35%
Relevant experience and investor network: 40%
Commercial and value for money: 25%
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
            "_Sample 1: Saudi Electricity Company (SEC) — SAP S/4HANA digital transformation, SAR 18m. "
            "Covers NCA compliance, SDAIA data residency, ZATCA e-invoicing, and Nitaqat requirements._\n\n"
            "_Sample 2: Royal Commission for AlUla (RCU) — Vision 2030 tourism investment attraction "
            "advisory, SAR 6.5m. International roadshows, anchor tenant negotiation, Arabic/English deliverables._"
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
