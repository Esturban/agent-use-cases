import os

import gradio as gr
from openai import OpenAI

from src.schema import LeadScore

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
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]

TIER_EMOJI = {"hot": "🔥 hot", "warm": "🟡 warm", "cold": "❄️ cold"}

HOT = "Company: Meridian Payments | Industry: FinTech | Size: 120 employees | Contact: Sarah Chen, VP of Operations | Notes: Team reconciling invoices manually across 3 spreadsheets, ~15 hours/week. Pay ~$8k/month in SaaS tools, looking to consolidate before Q3. Budget $2k–4k/month."
WARM = "Company: BloomRetail | Industry: E-commerce | Size: 35 employees | Contact: James Park, Head of Marketing | Notes: Struggling with inventory data across Shopify and their WMS. No dedicated ops person. Budget unclear but interested in a demo."
COLD = "Company: Riverside Law Group | Industry: Legal | Size: 12 attorneys | Contact: Office Manager | Notes: Looking for a better way to track billable hours. Currently using spreadsheets. Very small team, no budget discussed."


def qualify(lead_text: str, model: str):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise gr.Error("OPENROUTER_API_KEY is not set.")

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
    gr.Markdown("## Lead Qualifier\nPaste a lead description and score it against your ICP.")

    with gr.Row():
        with gr.Column():
            lead_input = gr.Textbox(label="Lead description", lines=10)
            model_dd = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Qualify Lead", variant="primary")
            gr.Examples(
                examples=[[HOT], [WARM], [COLD]],
                inputs=[lead_input],
                label="Sample leads",
            )

        with gr.Column():
            score_out = gr.Number(label="ICP Score (1–10)")
            tier_out = gr.Textbox(label="Tier")
            met_out = gr.Textbox(label="Criteria met")
            missed_out = gr.Textbox(label="Criteria missed")
            action_out = gr.Textbox(label="Recommended action")
            reasoning_out = gr.Textbox(label="Reasoning", lines=3)

    run_btn.click(
        qualify,
        inputs=[lead_input, model_dd],
        outputs=[score_out, tier_out, met_out, missed_out, action_out, reasoning_out],
    )

if __name__ == "__main__":
    demo.launch()
