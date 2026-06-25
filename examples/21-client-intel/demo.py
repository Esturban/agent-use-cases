"""Gradio demo — Client Intelligence Brief via OpenRouter structured output."""

import os

import gradio as gr
from openai import OpenAI

from src.schema import ClientIntelBrief

# Mock intelligence stores (same data as tools.py)
_NEWS = {
    "acme corp": (
        "Acme Corp raised a $120M Series C led by Tiger Global in Q1 2024. "
        "The company also announced a strategic partnership with Microsoft Azure."
    ),
    "beta industries": (
        "Beta Industries announced a $300M debt facility in Q4 2023. "
        "Revenue grew 28% YoY per their investor day presentation."
    ),
}
_FILINGS = {
    "acme corp": "Acme Corp is under FTC scrutiny for potential antitrust issues related to its 2023 acquisition of Streamline Inc.",
    "beta industries": "Beta Industries disclosed material climate-related reporting obligations under new SEC rules effective 2025.",
}
_LEADERSHIP = {
    "acme corp": "CFO Sarah Lin departed in March 2024. New CFO David Park hired from Goldman Sachs, effective May 2024.",
    "beta industries": "CTO Michael Chen promoted to Chief AI Officer, a newly created role, in January 2024.",
}
_MARKET = {
    "acme corp": "Acme Corp publicly stated intent to expand into the APAC market by end of 2024 and is hiring aggressively in Singapore.",
    "beta industries": "Beta Industries filed three patents in Q1 2024 related to autonomous logistics, signalling an AI-first product pivot.",
}

ANALYST_SYSTEM = (
    "You are a senior commercial intelligence analyst. "
    "Given raw intelligence signals about a company, synthesise them into a structured "
    "ClientIntelBrief with funding events, leadership changes, regulatory exposures, "
    "strategic signals, and prioritised relationship actions for the account team."
)

MODELS = [
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]

KNOWN_COMPANIES = ["Acme Corp", "Beta Industries"]


def _gather_intel(company: str) -> str:
    key = company.lower()
    news = _NEWS.get(key, f"No significant recent news found for {company}.")
    filings = _FILINGS.get(key, f"No material regulatory filings found for {company}.")
    leadership = _LEADERSHIP.get(key, f"No recent leadership changes found for {company}.")
    market = _MARKET.get(key, f"No significant market signals found for {company}.")
    return (
        f"Company: {company}\n\n"
        f"[News & Funding]\n{news}\n\n"
        f"[Regulatory Filings]\n{filings}\n\n"
        f"[Leadership Changes]\n{leadership}\n\n"
        f"[Market & Strategic Signals]\n{market}"
    )


def _fmt_list(items, fmt_fn) -> str:
    return "\n".join(fmt_fn(x) for x in items) if items else "None"


def build_brief(company: str, model: str) -> tuple[str, str, str, str, str]:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return "Set OPENROUTER_API_KEY env var", "", "", "", ""
    if not company.strip():
        return "Enter a company name.", "", "", "", ""

    intel = _gather_intel(company.strip())
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": ANALYST_SYSTEM},
            {"role": "user", "content": intel},
        ],
        response_format=ClientIntelBrief,
    )
    brief: ClientIntelBrief = completion.choices[0].message.parsed

    funding = _fmt_list(
        brief.funding_events,
        lambda f: f"• {f.date} — {f.round_type} ${f.amount_usd_m:.0f}M ({f.lead_investor})",
    )
    leadership = _fmt_list(
        brief.leadership_changes,
        lambda lc: f"• {lc.date} — {lc.role} {lc.change_type}: {lc.name}",
    )
    sev_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}
    regulatory = _fmt_list(
        brief.regulatory_exposures,
        lambda r: f"• {sev_icon.get(r.severity, '')} [{r.severity.upper()}] {r.topic}: {r.summary}",
    )
    signals = _fmt_list(
        brief.strategic_signals,
        lambda s: f"• {s.signal}\n  → {s.implication}",
    )
    actions = _fmt_list(brief.relationship_actions, lambda a: f"• {a}")
    return funding, leadership, regulatory, signals, actions


with gr.Blocks(title="Client Intel Brief") as demo:
    gr.Markdown(
        "## Client Intelligence Brief\n"
        "Enter a company name. The agent gathers signals across news, filings, "
        "leadership changes, and market moves — then synthesises prioritised account actions.\n\n"
        f"*Demo data available for: {', '.join(KNOWN_COMPANIES)}*"
    )
    with gr.Row():
        company_input = gr.Textbox(label="Company name", value="Acme Corp", scale=3)
        model_select = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model (via OpenRouter)", scale=1)
    gr.Examples(examples=[[c] for c in KNOWN_COMPANIES], inputs=company_input, label="Examples")
    run_btn = gr.Button("Build Brief", variant="primary")

    funding_out = gr.Textbox(label="Funding & capital events", lines=3, interactive=False)
    leadership_out = gr.Textbox(label="Leadership changes", lines=3, interactive=False)
    regulatory_out = gr.Textbox(label="Regulatory exposures", lines=3, interactive=False)
    signals_out = gr.Textbox(label="Strategic signals", lines=4, interactive=False)
    actions_out = gr.Textbox(label="Relationship actions (prioritised)", lines=4, interactive=False)

    run_btn.click(
        fn=build_brief,
        inputs=[company_input, model_select],
        outputs=[funding_out, leadership_out, regulatory_out, signals_out, actions_out],
    )

if __name__ == "__main__":
    demo.launch()
