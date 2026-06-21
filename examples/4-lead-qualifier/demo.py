import os
import sys

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))
from src.schema import LeadScore  # noqa: E402

SYSTEM = """You are a sales qualification assistant. Score inbound leads against this ICP rubric.

IDEAL CUSTOMER PROFILE (ICP):
  Industry:      SaaS, FinTech, or E-commerce
  Company size:  50-500 employees
  Pain point:    manual workflows, data silos, or compliance burden
  Buyer role:    VP Operations, CFO, or CTO
  Budget signal: existing software spend > $5k/month

SCORING:
  8-10 -> hot   (3+ criteria met, strong pain + budget signal)
  5-7  -> warm  (2 criteria met, or strong pain but budget unclear)
  1-4  -> cold  (fewer than 2 criteria met)

Populate criteria_met and criteria_missed by naming the exact ICP criteria above.
reasoning must explain the score in 1-2 sentences citing the criteria.
Never invent data not present in the lead description."""

MODELS = [
    "openai/gpt-5.4-nano",
    "minimax/minimax-m3",
    "openai/gpt-4.1-nano",
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]

TIER_EMOJI = {"hot": "🔥 hot", "warm": "🟡 warm", "cold": "❄️ cold"}

HOT = "Company: Meridian Payments | Industry: FinTech | Size: 120 employees | Contact: Sarah Chen, VP of Operations | Notes: Team reconciling invoices manually across 3 spreadsheets, ~15 hours/week. Pay ~$8k/month in SaaS tools, looking to consolidate before Q3. Budget $2k–4k/month."
WARM = "Company: BloomRetail | Industry: E-commerce | Size: 35 employees | Contact: James Park, Head of Marketing | Notes: Struggling with inventory data across Shopify and their WMS. No dedicated ops person. Budget unclear but interested in a demo."
COLD = "Company: Riverside Law Group | Industry: Legal | Size: 12 attorneys | Contact: Office Manager | Notes: Looking for a better way to track billable hours. Currently using spreadsheets. Very small team, no budget discussed."
REAL = "Company: Coreflow | Industry: SaaS (HR tech) | Size: 210 employees | Contact: Marcus Reid, COO | Notes: 4-person ops team spending 20hrs/week manually moving data between Workday, Salesforce, and their billing system. Current SaaS spend ~$14k/month. Actively evaluating automation vendors before their Series C closes in 90 days."


def qualify(lead_text: str, model: str):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise gr.Error("OPENAI_API_KEY is not set.")

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": lead_text},
        ],
        response_format=LeadScore,
    )
    result: LeadScore = completion.choices[0].message.parsed
    return (
        result.score,
        TIER_EMOJI.get(result.tier, result.tier),
        "\n".join(result.criteria_met),
        "\n".join(result.criteria_missed),
        result.recommended_action,
        result.reasoning,
    )


with gr.Blocks(title="Lead Qualifier") as demo:
    gr.Markdown(
        "## 🎯 Lead Qualifier\n"
        "Paste inbound lead notes → the model scores them against a hardcoded ICP and returns a "
        "tier, criteria breakdown, and recommended next action.\n\n"
        "**Built for:** sales teams, BDRs, and RevOps — anyone who needs a first-pass triage "
        "before burning a rep's time on a cold prospect."
    )

    with gr.Accordion("ICP & Scoring Rubric", open=True):
        gr.Markdown(
            "The model scores every lead against **five criteria**. "
            "Criteria met vs. missed are returned explicitly so you can audit the reasoning.\n\n"
            "| Criterion | Target |\n"
            "|-----------|--------|\n"
            "| **Industry** | SaaS · FinTech · E-commerce |\n"
            "| **Company size** | 50–500 employees |\n"
            "| **Pain point** | Manual workflows · Data silos · Compliance burden |\n"
            "| **Buyer role** | VP Operations · CFO · CTO |\n"
            "| **Budget signal** | >$5k/month existing SaaS spend |\n\n"
            "**Score → Tier:** `8–10` = 🔥 Hot (3+ criteria + budget) · "
            "`5–7` = 🟡 Warm (2 criteria or budget unclear) · "
            "`1–4` = ❄️ Cold (fewer than 2 criteria)\n\n"
            "_The model never invents signals — if a criterion isn't mentioned in the notes, it counts as missed._"
        )

    with gr.Row():
        with gr.Column():
            lead_input = gr.Textbox(
                label="Lead description",
                lines=10,
                placeholder="Paste CRM notes, a form submission, or any lead context here…",
            )
            model_dd = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Qualify Lead", variant="primary")
            gr.Examples(
                examples=[[HOT], [WARM], [COLD], [REAL]],
                inputs=[lead_input],
                label="Sample leads — click to load",
            )

        with gr.Column():
            gr.Markdown("#### Qualification result")
            score_out = gr.Number(label="ICP Score (1–10)")
            tier_out = gr.Textbox(label="Tier", interactive=False)
            met_out = gr.Textbox(label="Criteria met", lines=3, interactive=False)
            missed_out = gr.Textbox(label="Criteria missed", lines=3, interactive=False)
            action_out = gr.Textbox(label="Recommended action", interactive=False)
            reasoning_out = gr.Textbox(label="Why this score", lines=3, interactive=False)

    run_btn.click(
        qualify,
        inputs=[lead_input, model_dd],
        outputs=[score_out, tier_out, met_out, missed_out, action_out, reasoning_out],
    )

if __name__ == "__main__":
    demo.launch()
