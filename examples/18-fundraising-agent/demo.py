"""Gradio demo — Fundraising Strategy Generator via OpenRouter structured output."""

import os
import sys

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))
from src.schema import FundraisingPackage  # noqa: E402

SYSTEM_PROMPT = (
    "You are a fundraising advisor generating investor-specific materials for three audiences simultaneously.\n\n"
    "For each persona (VC, PE, family office), produce:\n"
    "- investor_thesis: what THIS investor type cares about, in their language\n"
    "- headline_metrics: 3-5 metrics most relevant to this persona\n"
    "- narrative_angle: the story framing that lands best with this audience\n"
    "- key_asks: what you are asking for, framed for this persona\n"
    "- objection_responses: pre-emptive answers to the top 2 likely objections\n"
    "- suggested_materials: which documents to send first and in what order\n\n"
    "VC language: ARR, NRR, burn multiple, CAC payback, category creation.\n"
    "PE language: EBITDA, margin expansion, operational efficiency, exit multiple, downside protection.\n"
    "Family office language: capital preservation, dividend potential, resilience, governance, stable compounding.\n\n"
    "Also identify 3-5 universal_value_props that resonate across all personas."
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

SAMPLE_COMPANY = """COMPANY: Coreflow Analytics
ROUND: Series B — raising GBP 22m
USE OF FUNDS: 60% product & engineering, 25% GTM expansion (US), 15% working capital

BUSINESS:
B2B SaaS — operational analytics for mid-market logistics companies (50-500 vehicles).
Platform ingests GPS, fuel, maintenance, and driver behaviour data to surface cost anomalies in real time.
Reduces fleet operating costs by average 18% within 6 months of deployment.

TRACTION:
ARR: GBP 4.8m (+112% YoY) | NRR: 134% | Gross margin: 78%
Customers: 87 | ACV: GBP 55k | CAC payback: 14 months
3 enterprise pilots underway (250+ vehicle fleets)
UK market: profitable. US pilot: 2 customers, GBP 180k ARR.

TEAM:
CEO — ex-McKinsey, 8 years logistics ops consulting
CTO — ex-Palantir, built data pipelines processing 10B+ events/day
CFO — ex-KPMG, previously CFO of a logistics SaaS through to exit

FINANCIALS:
Burn: GBP 320k/month | Runway: 19 months at current burn
Capex-light: all cloud, no proprietary hardware

COMPETITIVE POSITION:
Main competitors: Samsara (US-focused, large enterprise), Quartix (UK, basic telematics only).
Neither covers operational analytics at depth for mid-market. No direct UK competitor at this ACV.
"""

SAMPLE_COMPANY_2 = """COMPANY: NestNorth Capital Ltd
ROUND: Growth Equity — raising GBP 15m
USE OF FUNDS: 40% property acquisitions, 35% platform build, 25% team

BUSINESS:
PropTech platform for build-to-rent (BTR) property management in the UK North (Manchester, Leeds, Sheffield).
Combines proprietary tenant-matching technology with in-house property management.
Currently manages 1,200 units across 8 developments. Target: 5,000 units by 2027.

FINANCIALS:
Revenue: GBP 3.8m (management fees + platform licensing)
EBITDA: GBP 0.9m (24% margin) | 3-year CAGR: 47%
Contracted forward revenue: GBP 2.1m (signed LOIs for 3 new developments)
NAV of managed portfolio: GBP 85m

TEAM:
CEO — ex-CBRE, 15 years BTR asset management
CTO — ex-Rightmove, built tenant search infrastructure
CFO — ex-PwC Real Estate

DIFFERENTIATION:
Proprietary tenant-scoring model reduces void periods to 4 days (industry average: 28 days).
Landlord NPS: 78. All developments within 400m of transport links.
"""


def _format_materials(m) -> str:
    lines = [
        f"**Investor thesis:** {m.investor_thesis}\n",
        "**Headline metrics:** " + " · ".join(m.headline_metrics),
        f"\n**Narrative angle:** {m.narrative_angle}\n",
        "**Key asks:**\n" + "\n".join(f"• {a}" for a in m.key_asks),
        "\n**Objection responses:**\n" + "\n".join(f"• {r}" for r in m.objection_responses),
        "\n**Send first:** " + " → ".join(m.suggested_materials),
    ]
    return "\n".join(lines)


def generate_fundraising(profile: str, model: str):
    if not profile.strip():
        return "", "", "", "", ""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise gr.Error("OPENROUTER_API_KEY is not set — add it to your .env file.")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": profile},
        ],
        response_format=FundraisingPackage,
    )
    r: FundraisingPackage = completion.choices[0].message.parsed
    universal = "\n".join(f"• {v}" for v in r.universal_value_props)
    return (
        universal,
        _format_materials(r.vc_materials),
        _format_materials(r.pe_materials),
        _format_materials(r.family_office_materials),
        f"Company: {r.company or 'N/A'} | Round: {r.round_type}",
    )


with gr.Blocks(title="Fundraising Strategy") as demo:
    gr.Markdown(
        "## 📈 Fundraising Strategy Generator\n"
        "Paste a company profile → the model generates audience-specific fundraising materials "
        "for VC, PE, and family office investors simultaneously — each in the right language, "
        "with pre-built objection responses.\n\n"
        "**Built for:** founders, CFOs, and advisors preparing for a fundraise who need to tailor "
        "the same story three different ways without starting from scratch each time."
    )

    with gr.Accordion("Why three personas matter", open=True):
        gr.Markdown(
            "VCs, PE firms, and family offices evaluate the same company on completely different axes:\n\n"
            "| Persona | What they care about | Their language |\n"
            "|---------|---------------------|----------------|\n"
            "| **Venture Capital** | Growth velocity, TAM, NRR, category leadership | ARR, burn multiple, CAC payback |\n"
            "| **Private Equity** | EBITDA, margin expansion, operational efficiency | Exit multiple, EBITDA bridge, downside protection |\n"
            "| **Family Office** | Capital preservation, governance, stable compounding | Dividend yield, NAV, resilience |\n\n"
            "Pitching with a generic deck to all three is the fastest way to get a no from all three.\n\n"
            "_Sample 1: Coreflow Analytics — B2B SaaS, Series B, GBP 22m raise._\n"
            "_Sample 2: NestNorth Capital — PropTech, Growth Equity, GBP 15m raise._"
        )

    with gr.Row():
        with gr.Column(scale=2):
            profile_input = gr.Textbox(
                label="Company profile",
                lines=22,
                placeholder="Paste your company profile — business, traction, team, financials, competitive position…",
                value=SAMPLE_COMPANY,
            )
            model_dd = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Generate Fundraising Strategy", variant="primary")
            gr.Examples(
                examples=[[SAMPLE_COMPANY], [SAMPLE_COMPANY_2]],
                inputs=[profile_input],
                label="Sample profiles — click to load",
            )

        with gr.Column(scale=3):
            round_out = gr.Textbox(label="Round", interactive=False)
            universal_out = gr.Textbox(
                label="Universal value props (resonate across all personas)",
                lines=4,
                interactive=False,
            )
            with gr.Tab("Venture Capital"):
                vc_out = gr.Markdown()
            with gr.Tab("Private Equity"):
                pe_out = gr.Markdown()
            with gr.Tab("Family Office"):
                fo_out = gr.Markdown()

    run_btn.click(
        fn=generate_fundraising,
        inputs=[profile_input, model_dd],
        outputs=[universal_out, vc_out, pe_out, fo_out, round_out],
    )

if __name__ == "__main__":
    demo.launch()
