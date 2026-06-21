import os

import gradio as gr
from openai import OpenAI

from src.schema import ContractReview

SYSTEM_PROMPT = (
    "You are a senior commercial lawyer reviewing a contract on behalf of a client. "
    "Identify all risk findings (with exact clause_reference for every finding), "
    "missing standard protections, and negotiation points prioritised as "
    "must_have/should_have/nice_to_have. Be thorough but precise. "
    "A finding without a clause reference is worthless."
)

SAMPLE_SERVICES = """PROFESSIONAL SERVICES AGREEMENT

Section 1. Services
Service Provider shall perform consulting services as directed by Client. Client may modify the scope at any time without notice.

Section 2. Payment
Client shall pay within 90 days of invoice. Late payments shall not accrue interest. Client may withhold payment for any reason.

Section 3. Intellectual Property
All work product created by Service Provider shall be sole property of Client. This assignment includes all pre-existing tools and methodologies.

Section 4. Confidentiality
Service Provider agrees to keep all Client information confidential for 1 year following termination.

Section 5. Liability
Client shall not be liable for any damages. Service Provider's liability to Client shall be unlimited.

Section 6. Termination
Client may terminate immediately without cause. Service Provider may not terminate without 180 days written notice.

Section 7. Governing Law
Governed by the laws of the State of Delaware."""

SAMPLE_NDA = """MUTUAL NON-DISCLOSURE AGREEMENT

This Agreement is entered into between the parties identified below.

1. Definition of Confidential Information
"Confidential Information" means any non-public information disclosed by either party.

2. Obligations
Each party agrees to hold the other's Confidential Information in strict confidence and not to disclose it to any third party.

3. Term
This Agreement shall remain in effect for two (2) years from the date of signing.

4. Governing Law
This Agreement shall be governed by the laws of California."""


RISK_EMOJI = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}

MODELS = [
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]


def review_contract(contract_text: str, model: str):
    if not contract_text.strip():
        return "No contract text provided.", "", "", "", ""

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": contract_text},
        ],
        response_format=ContractReview,
    )

    result: ContractReview = completion.choices[0].message.parsed

    overall_risk = RISK_EMOJI.get(result.overall_risk, result.overall_risk)

    risk_lines = []
    for f in result.risk_findings:
        severity_label = f.severity.upper()
        category_label = f.category.replace("_", " ").title()
        risk_lines.append(
            f"**[{severity_label}] {category_label} — {f.clause_reference}**\n"
            f"- **Issue:** {f.issue}\n"
            f"- **Implication:** {f.implication}\n"
            f"- **Redline:** {f.recommended_redline}"
        )
    risk_md = "\n\n".join(risk_lines) if risk_lines else "_None identified._"

    protection_lines = []
    for p in result.missing_protections:
        protection_lines.append(
            f"**{p.protection}**\n"
            f"- **Why needed:** {p.why_needed}\n"
            f"- **Suggested clause:** {p.suggested_clause}"
        )
    protection_md = "\n\n".join(protection_lines) if protection_lines else "_None identified._"

    groups = {"must_have": [], "should_have": [], "nice_to_have": []}
    for n in result.negotiation_points:
        groups[n.priority].append(n)

    neg_lines = []
    for priority, label in [
        ("must_have", "Must Have"),
        ("should_have", "Should Have"),
        ("nice_to_have", "Nice to Have"),
    ]:
        points = groups[priority]
        if points:
            neg_lines.append(f"### {label}")
            for p in points:
                neg_lines.append(
                    f"**{p.topic}**\n"
                    f"- **Current:** {p.current_position}\n"
                    f"- **Target:** {p.target_position}"
                )
    neg_md = "\n\n".join(neg_lines) if neg_lines else "_None identified._"

    return overall_risk, result.executive_summary, risk_md, protection_md, neg_md


with gr.Blocks(title="Contract Reviewer") as demo:
    gr.Markdown(
        "# Contract Reviewer\n"
        "Paste contract text to receive risk findings, missing protections, and negotiation points."
    )

    with gr.Row():
        with gr.Column(scale=2):
            contract_input = gr.Textbox(
                label="Contract Text",
                lines=14,
                placeholder="Paste contract text here...",
            )
            model_dropdown = gr.Dropdown(
                choices=MODELS,
                value=MODELS[0],
                label="Model",
            )
            review_btn = gr.Button("Review Contract", variant="primary")

            gr.Examples(
                examples=[[SAMPLE_SERVICES], [SAMPLE_NDA]],
                inputs=[contract_input],
                label="Sample Contracts",
            )

        with gr.Column(scale=3):
            overall_risk_out = gr.Textbox(label="Overall Risk", interactive=False)
            executive_summary_out = gr.Textbox(
                label="Executive Summary", lines=3, interactive=False
            )
            risk_findings_out = gr.Markdown(label="Risk Findings")
            missing_protections_out = gr.Markdown(label="Missing Protections")
            negotiation_points_out = gr.Markdown(label="Negotiation Points")

    review_btn.click(
        fn=review_contract,
        inputs=[contract_input, model_dropdown],
        outputs=[
            overall_risk_out,
            executive_summary_out,
            risk_findings_out,
            missing_protections_out,
            negotiation_points_out,
        ],
    )

if __name__ == "__main__":
    demo.launch()
