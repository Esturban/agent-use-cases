"""Gradio demo — Market Entry Strategy via OpenRouter structured output."""

import os
import sys

import gradio as gr
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(raise_error_if_not_found=False))

sys.path.insert(0, os.path.dirname(__file__))
from src.schema import MarketAnalysis  # noqa: E402

SYSTEM_PROMPT = (
    "You are a strategy consultant producing a market entry analysis. "
    "Given a client brief, analyse the target market and return a structured MarketAnalysis.\n\n"
    "For each competitor, estimate market share, list 2-3 key strengths and 2-3 weaknesses.\n"
    "For opportunities and risks, score each 1-10 (10 = highest attractiveness/severity).\n"
    "Provide a clear entry_recommendation: enter / monitor / avoid, with a 2-3 sentence rationale.\n"
    "Be specific and commercially grounded — no generic consulting language."
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

SAMPLE_BRIEF = """MARKET ENTRY ANALYSIS REQUEST

Client: NovaMed Diagnostics (Netherlands-based, EUR 85m revenue)
Target market: UK private healthcare diagnostics
Proposed product: rapid molecular diagnostic panels for GP practices and occupational health clinics

CONTEXT:
NovaMed has 40% market share in Benelux for PCR-based diagnostics sold to hospital labs.
They want to expand into the UK, targeting private GP practices and occupational health clinics.
The UK private diagnostics market was disrupted post-COVID — several incumbents exited.
NHS outsourcing of diagnostics to private providers increased 28% in 2024.

Analyse:
- Total addressable market size and growth rate
- Key competitors and their positioning
- Regulatory environment (UKCA marking, CQC registration requirements)
- Market entry recommendation with rationale
"""

SAMPLE_BRIEF_2 = """MARKET ENTRY ANALYSIS REQUEST

Client: FleetSync (UK-based SaaS, GBP 4.8m ARR)
Target market: US mid-market logistics fleet management software (50-500 vehicles)
Current position: UK market leader for fleets under 200 vehicles; no US presence

CONTEXT:
FleetSync raised Series B (GBP 22m) and is evaluating a US market entry.
Primary use case: real-time driver behaviour analytics, fuel optimization, maintenance scheduling.
US competitors: Samsara (enterprise focus), Geotab (hardware-dependent), Verizon Connect (legacy).
No clear leader in the 50-200 vehicle segment in the US. FleetSync's ACV is USD 45k.

Analyse the US mid-market fleet management opportunity.
"""

VERDICT_LABEL = {
    "enter": "✅ Enter",
    "monitor": "🟡 Monitor",
    "avoid": "🔴 Avoid",
}


def _format_competitors(competitors: list) -> str:
    if not competitors:
        return "_No competitors identified._"
    lines = []
    for c in competitors:
        lines.append(
            f"**{c.name}** (~{c.estimated_market_share_pct:.0f}% market share)\n\n"
            "Strengths: " + " · ".join(c.strengths) + "\n\n"
            "Weaknesses: " + " · ".join(c.weaknesses)
        )
    return "\n\n---\n\n".join(lines)


def _format_opp_risks(items: list) -> str:
    if not items:
        return "_None identified._"
    opps = [i for i in items if i.category == "opportunity"]
    risks = [i for i in items if i.category == "risk"]
    lines = []
    if opps:
        lines.append("**Opportunities**")
        for o in sorted(opps, key=lambda x: -x.score):
            lines.append(f"• (score {o.score}/10) {o.description}")
    if risks:
        lines.append("\n**Risks**")
        for r in sorted(risks, key=lambda x: -x.score):
            lines.append(f"• (score {r.score}/10) {r.description}")
    return "\n".join(lines)


def analyse_market(brief: str, model: str):
    if not brief.strip():
        return "", "", "", "", ""
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
        response_format=MarketAnalysis,
    )
    r: MarketAnalysis = completion.choices[0].message.parsed
    market_summary = (
        f"Market: {r.market}\n"
        f"TAM: USD {r.market_size_usd_bn:.1f}bn | Growth rate: {r.growth_rate_pct:.1f}% p.a."
    )
    return (
        VERDICT_LABEL.get(r.entry_recommendation, r.entry_recommendation),
        r.rationale,
        market_summary,
        _format_competitors(r.competitors),
        _format_opp_risks(r.opportunities_and_risks),
    )


with gr.Blocks(title="Market Entry Strategy") as demo:
    gr.Markdown(
        "## 🌍 Market Entry Strategy\n"
        "Paste a client brief → the model produces a market entry analysis: TAM, competitor profiles, "
        "opportunities and risks scored 1-10, and a clear enter/monitor/avoid verdict.\n\n"
        "**Built for:** strategy teams, CEOs, and investors evaluating new geographies or segments "
        "before committing capital to a market entry."
    )

    with gr.Accordion("What this produces", open=True):
        gr.Markdown(
            "| Output | Detail |\n"
            "|--------|--------|\n"
            "| **Verdict** | Enter · Monitor · Avoid — with a 2-3 sentence rationale |\n"
            "| **Market sizing** | TAM in USD billions and annual growth rate |\n"
            "| **Competitor profiles** | Top 3-5 players: estimated share, strengths, weaknesses |\n"
            "| **Opportunities & risks** | Scored 1-10, sorted by score |\n\n"
            "_Sample 1: NovaMed Diagnostics evaluating UK private healthcare diagnostics._\n\n"
            "_Sample 2: FleetSync (UK SaaS) evaluating US mid-market fleet management._"
        )

    with gr.Row():
        with gr.Column(scale=2):
            brief_input = gr.Textbox(
                label="Client brief",
                lines=18,
                placeholder="Describe the client, target market, product, and what you need analysed…",
                value=SAMPLE_BRIEF,
            )
            model_dd = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Analyse Market", variant="primary")
            gr.Examples(
                examples=[[SAMPLE_BRIEF], [SAMPLE_BRIEF_2]],
                inputs=[brief_input],
                label="Sample briefs — click to load",
            )

        with gr.Column(scale=3):
            verdict_out = gr.Textbox(label="Entry recommendation", interactive=False)
            rationale_out = gr.Textbox(label="Rationale", lines=3, interactive=False)
            market_out = gr.Textbox(label="Market sizing", lines=2, interactive=False)
            gr.Markdown("#### Competitor Landscape")
            competitors_out = gr.Markdown()
            gr.Markdown("#### Opportunities & Risks")
            opp_risk_out = gr.Markdown()

    run_btn.click(
        fn=analyse_market,
        inputs=[brief_input, model_dd],
        outputs=[verdict_out, rationale_out, market_out, competitors_out, opp_risk_out],
    )

if __name__ == "__main__":
    demo.launch()
