"""
Hugging Face Spaces entry point — three agent demos in one tabbed interface.
Set OPENROUTER_API_KEY as a Space secret before launching.
"""

import os
from typing import List, Literal, Optional

import gradio as gr
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator

# ── Schemas (inlined — no sub-package imports needed for HF Spaces) ──────────

class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float

class Invoice(BaseModel):
    vendor: str
    invoice_number: str
    date: str
    subtotal: float
    tax: float
    total_amount: float
    line_items: List[LineItem]

    @field_validator("total_amount")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("total_amount must be positive")
        return v

class ResumeScore(BaseModel):
    candidate_name: str
    overall_score: int = Field(ge=1, le=10)
    tier: Literal["strong_yes", "yes", "maybe", "no"]
    years_experience: int = Field(ge=0)
    skills_matched: List[str]
    skills_missing: List[str]
    standout: str
    concern: str
    recommended_action: Literal["schedule_interview", "hold_for_review", "pass"]

class RiskFinding(BaseModel):
    severity: Literal["critical", "high", "medium", "low"]
    category: Literal["liability", "payment", "ip", "termination", "confidentiality", "governance", "compliance", "other"]
    clause_reference: str
    issue: str
    implication: str
    recommended_redline: str

class MissingProtection(BaseModel):
    protection: str
    why_needed: str
    suggested_clause: str

class NegotiationPoint(BaseModel):
    priority: Literal["must_have", "should_have", "nice_to_have"]
    topic: str
    current_position: str
    target_position: str

class ContractReview(BaseModel):
    contract_type: str
    counterparty: Optional[str] = None
    governing_law: Optional[str] = None
    overall_risk: Literal["high", "medium", "low"]
    executive_summary: str
    risk_findings: List[RiskFinding]
    missing_protections: List[MissingProtection]
    negotiation_points: List[NegotiationPoint]

# ── Shared ───────────────────────────────────────────────────────────────────

MODELS = [
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]

def _client() -> OpenAI:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise ValueError("OPENROUTER_API_KEY is not set.")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)

# ── Tab 1: Invoice Extractor ─────────────────────────────────────────────────

INVOICE_SYSTEM = (
    "You are an invoice parsing assistant. Extract structured data from invoice text. "
    "Return exact values from the document. Date must be ISO format YYYY-MM-DD. "
    "Amounts in decimal — no currency symbols in the numeric fields."
)

INVOICE_SAMPLES = [
    """CloudPeak Software Ltd
Invoice #: INV-2024-0892  |  Date: May 15, 2024

Annual SaaS License - 5 seats    Qty: 1    $2,400.00
Premium Support Package           Qty: 1    $600.00
Onboarding Services               Qty: 3    $150.00 each = $450.00

Subtotal: $3,450.00
Tax (15%): $517.50
Total Due: $3,967.50""",

    """Apex Cloud Consulting
Invoice No: APC-2024-112  |  Date: June 15, 2024

Architecture Review    1 day    @ $3,500/day     $3,500.00
Implementation         3 days   @ $2,200/day     $6,600.00
Documentation          0.5 day  @ $1,800/day       $900.00

Subtotal: $11,000.00
GST (10%): $1,100.00
Total: $12,100.00""",

    """Maple Street Cafe
Receipt #: RCP-0442  |  Date: July 3, 2024

Coffee       x2    $4.50 each = $9.00
Sandwich     x1    $12.50
Cake         x1    $6.00

Subtotal: $27.50
Tax (8%): $2.20
Total: $29.70""",
]

def extract_invoice(text: str, model: str):
    if not text.strip():
        return "", "", "", [], 0.0, 0.0, 0.0
    try:
        result: Invoice = _client().beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": INVOICE_SYSTEM},
                {"role": "user", "content": text},
            ],
            response_format=Invoice,
        ).choices[0].message.parsed
    except Exception as e:
        return str(e), "", "", [], 0.0, 0.0, 0.0
    rows = [
        [i.description, i.quantity, f"${i.unit_price:.2f}", f"${i.total:.2f}"]
        for i in result.line_items
    ]
    return result.vendor, result.invoice_number, result.date, rows, result.subtotal, result.tax, result.total_amount

# ── Tab 2: Resume Screener ───────────────────────────────────────────────────

RESUME_SYSTEM = """You are a senior technical recruiter screening candidates for a backend engineering role.

Job Specification:
Role: Senior Python Backend Engineer — FinTech startup (Series B, 80 employees)
Required: Python 5+ years, REST API design (FastAPI or Django REST), PostgreSQL, Cloud (AWS or GCP), Git/CI/CD
Nice to have: Financial domain, Pydantic, Docker/Kubernetes, Team leadership
Red flags: <3 years experience, no production deployment, only frontend or data science

Score 1–10. tier: strong_yes=8-10, yes=6-7, maybe=4-5, no=1-3. Be honest. Do not inflate scores."""

RESUME_SAMPLES = [
    """Alex Kim — Senior Software Engineer
7 years Python. Built FastAPI microservices handling $2M/day at two fintech startups.
Led a team of 3. PostgreSQL, AWS (ECS, RDS), Docker, Kubernetes, GitHub Actions CI/CD.
Skills: Python, FastAPI, PostgreSQL, AWS, Docker, Pydantic, Redis, Git.""",

    """Jordan Lee — Data Scientist
4 years. Python, pandas, scikit-learn, XGBoost. ML pipelines for e-commerce.
Basic Flask for internal tools — never production. No cloud deployment.
Skills: Python, pandas, scikit-learn, SQL (basic), Flask.""",

    """Sam Nguyen — Junior Backend Developer
2 years. Django REST Framework, PostgreSQL, basic GCP App Engine.
Still learning Docker and CI/CD. No production deployment at scale.
Skills: Python, Django, PostgreSQL, GCP (basic), Git.""",
]

TIER_LABEL = {
    "strong_yes": "✅ strong_yes",
    "yes": "🟢 yes",
    "maybe": "🟡 maybe",
    "no": "🔴 no",
}

def screen_resume(text: str, model: str):
    if not text.strip():
        return None, "", "", "", "", "", ""
    try:
        result: ResumeScore = _client().beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": RESUME_SYSTEM},
                {"role": "user", "content": text},
            ],
            response_format=ResumeScore,
        ).choices[0].message.parsed
    except Exception as e:
        return None, str(e), "", "", "", "", ""
    return (
        result.overall_score,
        TIER_LABEL.get(result.tier, result.tier),
        ", ".join(result.skills_matched),
        ", ".join(result.skills_missing),
        result.standout,
        result.concern,
        result.recommended_action,
    )

# ── Tab 3: Contract Reviewer ─────────────────────────────────────────────────

CONTRACT_SYSTEM = (
    "You are a senior commercial lawyer reviewing a contract on behalf of a client. "
    "Identify all risk findings (with exact clause_reference for every finding — never omit it), "
    "missing standard protections, and negotiation points as must_have/should_have/nice_to_have. "
    "Be thorough but precise. A finding without a clause reference is worthless."
)

CONTRACT_SAMPLES = [
    """PROFESSIONAL SERVICES AGREEMENT

Section 1. Services
Service Provider shall perform consulting services as directed by Client.
Client may modify the scope at any time without notice.

Section 2. Payment
Client shall pay within 90 days of invoice. Late payments shall not accrue interest.
Client may withhold payment for any reason it deems appropriate.

Section 3. Intellectual Property
All work product created by Service Provider shall be sole property of Client.
This assignment includes all pre-existing tools and methodologies used in delivery.

Section 4. Confidentiality
Service Provider agrees to keep all Client information confidential for 1 year following termination.

Section 5. Liability
Client shall not be liable for any damages whatsoever.
Service Provider's liability to Client shall be unlimited.

Section 6. Termination
Client may terminate immediately without cause.
Service Provider may not terminate without 180 days written notice.

Section 7. Governing Law
Governed by the laws of the State of Delaware.""",

    """MUTUAL NON-DISCLOSURE AGREEMENT

1. Definition of Confidential Information
"Confidential Information" means any non-public information disclosed by either party.

2. Obligations
Each party shall hold the other's Confidential Information in strict confidence
and shall not disclose it to any third party.

3. Term
This Agreement shall remain in effect for two (2) years from the date of signing.

4. Governing Law
This Agreement shall be governed by the laws of California.""",
]

RISK_LABEL = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}

def review_contract(text: str, model: str):
    if not text.strip():
        return "", "", "", "", ""
    try:
        result: ContractReview = _client().beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": CONTRACT_SYSTEM},
                {"role": "user", "content": text},
            ],
            response_format=ContractReview,
        ).choices[0].message.parsed
    except Exception as e:
        return str(e), "", "", "", ""

    risk_md = "\n\n".join(
        f"**[{f.severity.upper()}] {f.category.replace('_', ' ').title()} — {f.clause_reference}**\n"
        f"- **Issue:** {f.issue}\n"
        f"- **Implication:** {f.implication}\n"
        f"- **Redline:** {f.recommended_redline}"
        for f in result.risk_findings
    ) or "_None identified._"

    protection_md = "\n\n".join(
        f"**{p.protection}**\n"
        f"- **Why needed:** {p.why_needed}\n"
        f"- **Suggested clause:** {p.suggested_clause}"
        for p in result.missing_protections
    ) or "_None identified._"

    groups: dict = {"must_have": [], "should_have": [], "nice_to_have": []}
    for n in result.negotiation_points:
        groups[n.priority].append(n)
    neg_parts = []
    for key, label in [("must_have", "Must Have"), ("should_have", "Should Have"), ("nice_to_have", "Nice to Have")]:
        if groups[key]:
            neg_parts.append(f"### {label}")
            neg_parts.extend(
                f"**{p.topic}**\n- **Current:** {p.current_position}\n- **Target:** {p.target_position}"
                for p in groups[key]
            )
    neg_md = "\n\n".join(neg_parts) or "_None identified._"

    return RISK_LABEL.get(result.overall_risk, result.overall_risk), result.executive_summary, risk_md, protection_md, neg_md

# ── App ──────────────────────────────────────────────────────────────────────

with gr.Blocks(title="Agent Use Cases") as demo:
    gr.Markdown(
        "# Agent Use Cases\n"
        "Three real-world AI agent demos — structured output via OpenRouter.\n"
        "Pick a model, paste your text, hit the button."
    )

    with gr.Tab("📄 Invoice Extractor"):
        gr.Markdown("Paste any invoice or receipt text → extract vendor, line items, and totals instantly.")
        inv_text = gr.Textbox(label="Invoice text", lines=10, placeholder="Paste invoice or receipt here…")
        with gr.Row():
            inv_model = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            inv_btn = gr.Button("Extract", variant="primary")
        gr.Examples(examples=[[s] for s in INVOICE_SAMPLES], inputs=inv_text, label="Sample invoices")
        with gr.Row():
            inv_vendor = gr.Textbox(label="Vendor")
            inv_num = gr.Textbox(label="Invoice #")
            inv_date = gr.Textbox(label="Date")
        inv_items = gr.Dataframe(headers=["Description", "Qty", "Unit Price", "Total"], interactive=False, label="Line items")
        with gr.Row():
            inv_sub = gr.Number(label="Subtotal ($)")
            inv_tax = gr.Number(label="Tax ($)")
            inv_total = gr.Number(label="Total ($)")
        inv_btn.click(
            extract_invoice,
            [inv_text, inv_model],
            [inv_vendor, inv_num, inv_date, inv_items, inv_sub, inv_tax, inv_total],
        )

    with gr.Tab("👤 Resume Screener"):
        gr.Markdown("Paste a resume → scored against a Senior Python Backend Engineer spec in seconds.")
        with gr.Row():
            with gr.Column():
                res_text = gr.Textbox(label="Resume text", lines=12, placeholder="Paste resume here…")
                res_model = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
                res_btn = gr.Button("Screen", variant="primary")
                gr.Examples(examples=[[s] for s in RESUME_SAMPLES], inputs=res_text, label="Sample resumes")
            with gr.Column():
                res_score = gr.Number(label="Score (1–10)")
                res_tier = gr.Textbox(label="Tier")
                res_matched = gr.Textbox(label="Skills matched")
                res_missing = gr.Textbox(label="Skills missing")
                res_standout = gr.Textbox(label="Standout")
                res_concern = gr.Textbox(label="Concern")
                res_action = gr.Textbox(label="Recommended action")
        res_btn.click(
            screen_resume,
            [res_text, res_model],
            [res_score, res_tier, res_matched, res_missing, res_standout, res_concern, res_action],
        )

    with gr.Tab("⚖️ Contract Reviewer"):
        gr.Markdown("Paste contract text → risk findings, missing protections, and negotiation playbook.")
        with gr.Row():
            with gr.Column(scale=2):
                con_text = gr.Textbox(label="Contract text", lines=14, placeholder="Paste contract here…")
                con_model = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
                con_btn = gr.Button("Review", variant="primary")
                gr.Examples(examples=[[s] for s in CONTRACT_SAMPLES], inputs=con_text, label="Sample contracts")
            with gr.Column(scale=3):
                con_risk = gr.Textbox(label="Overall risk", interactive=False)
                con_summary = gr.Textbox(label="Executive summary", lines=3, interactive=False)
                con_findings = gr.Markdown(label="Risk findings")
                con_missing = gr.Markdown(label="Missing protections")
                con_neg = gr.Markdown(label="Negotiation points")
        con_btn.click(
            review_contract,
            [con_text, con_model],
            [con_risk, con_summary, con_findings, con_missing, con_neg],
        )

if __name__ == "__main__":
    demo.launch()
