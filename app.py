"""
Hugging Face Spaces entry point — six agent demos in one tabbed interface.
Set OPENROUTER_API_KEY as a Space secret before launching.
"""

import json
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

class TicketClassification(BaseModel):
    ticket_type: Literal["billing", "technical", "account", "feature_request", "other"]
    urgency: Literal["critical", "high", "medium", "low"]
    team: Literal["billing", "engineering", "account_management", "product", "general_support"]
    confidence: float
    reasoning: str

class DraftReply(BaseModel):
    subject: str
    body: str
    internal_note: str
    escalate: bool

class LeadScore(BaseModel):
    company: str
    score: int = Field(ge=1, le=10)
    tier: Literal["hot", "warm", "cold"]
    criteria_met: List[str]
    criteria_missed: List[str]
    recommended_action: str
    reasoning: str

# ── Shared ───────────────────────────────────────────────────────────────────

MODELS = [
    "openai/gpt-4.1-nano",
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

# ── Tab 4: Support Ticket Router ─────────────────────────────────────────────

TICKET_CLASSIFIER_SYSTEM = (
    "You are a customer support ticket classifier. Given a support ticket, classify:\n"
    "- ticket_type: billing | technical | account | feature_request | other\n"
    "- urgency: critical (service down/data loss/security) | high (major feature broken/billing dispute)"
    " | medium (degraded perf/billing question) | low (general question/feature request)\n"
    "- team: billing | engineering | account_management | product | general_support\n"
    "- confidence: 0.0-1.0\n"
    "- reasoning: one sentence explaining the routing decision"
)

DRAFTER_SYSTEMS = {
    "billing": "Draft a first-response email for the billing support team. Empathetic, acknowledge issue, set 1-2 business day resolution expectation. Set escalate=True for disputes over $500 or subscription cancellations.",
    "engineering": "Draft a first-response email for the engineering/technical support team. Acknowledge issue, ask for relevant details if not provided. Set escalate=True for outages, data loss, or security.",
    "account_management": "Draft a first-response email for the account management team. Warm and professional. For cancellations, offer retention path. Set escalate=True for enterprise accounts.",
    "product": "Draft a first-response email for the product team. Thank customer, confirm feedback logged, no timeline commitments. escalate=False unless blocking.",
    "general_support": "Draft a first-response email for general support. Helpful and concise, aim to resolve in one reply. escalate=True only if account access or billing changes needed.",
}

URGENCY_EMOJI = {"critical": "🔴 critical", "high": "🟠 high", "medium": "🟡 medium", "low": "🟢 low"}

TICKET_SAMPLES = [
    ["Charged twice this month - invoice #4821", "Sarah Chen", "schen@example.com",
     "I noticed my credit card was charged $99 twice on June 1st. Invoice #4821 shows a duplicate charge. Please refund ASAP."],
    ["Dashboard not loading - production down", "Marcus Torres", "m.torres@bigcorp.com",
     "Our entire team cannot access the dashboard since 9 AM EST. Getting 502 errors. Enterprise plan."],
    ["How do I add team members?", "Priya Patel", "priya@startup.io",
     "I'm trying to invite my colleagues to our workspace but can't find where to do it."],
]

def route_and_draft(subject: str, name: str, email: str, body: str, model: str):
    if not body.strip():
        return "", "", "", "", "", "", "", ""
    try:
        client = _client()
        clf: TicketClassification = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": TICKET_CLASSIFIER_SYSTEM},
                {"role": "user", "content": f"Subject: {subject}\nFrom: {name} <{email}>\n---\n{body}"},
            ],
            response_format=TicketClassification,
        ).choices[0].message.parsed
        draft_msg = (
            f"You are replying to this support ticket:\nSubject: {subject}\nFrom: {name} <{email}>\n"
            f"---\n{body}\n---\nClassification: {clf.ticket_type} / {clf.urgency} urgency → routed to {clf.team}"
        )
        draft: DraftReply = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": DRAFTER_SYSTEMS.get(clf.team, DRAFTER_SYSTEMS["general_support"])},
                {"role": "user", "content": draft_msg},
            ],
            response_format=DraftReply,
        ).choices[0].message.parsed
    except Exception as e:
        return str(e), "", "", "", "", "", "", ""
    return (
        URGENCY_EMOJI.get(clf.urgency, clf.urgency),
        clf.team.replace("_", " "),
        f"{clf.confidence * 100:.0f}%",
        clf.reasoning,
        draft.subject,
        draft.body,
        draft.internal_note,
        "⚠️ Yes" if draft.escalate else "No",
    )

# ── Tab 5: Lead Qualifier ─────────────────────────────────────────────────────

LEAD_SYSTEM = """You are a sales qualification assistant. Score inbound leads against this ICP rubric.

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
reasoning must explain the score in 1-2 sentences. Never invent data not present in the lead."""

LEAD_SAMPLES = [
    "Company: Meridian Payments | Industry: FinTech | Size: 120 employees | Contact: Sarah Chen, VP of Operations | Notes: Team reconciling invoices manually across 3 spreadsheets, ~15 hours/week. Pay ~$8k/month in SaaS tools, looking to consolidate before Q3. Budget $2k–4k/month.",
    "Company: Coreflow | Industry: SaaS (HR tech) | Size: 210 employees | Contact: Marcus Reid, COO | Notes: 4-person ops team spending 20hrs/week manually moving data between Workday, Salesforce, and their billing system. Current SaaS spend ~$14k/month. Actively evaluating automation vendors before their Series C closes in 90 days.",
    "Company: BloomRetail | Industry: E-commerce | Size: 35 employees | Contact: James Park, Head of Marketing | Notes: Struggling with inventory data across Shopify and their WMS. No dedicated ops person. Budget unclear but interested in a demo.",
    "Company: Riverside Law Group | Industry: Legal | Size: 12 attorneys | Contact: Office Manager | Notes: Looking for a better way to track billable hours. Currently using spreadsheets. Very small team, no budget discussed.",
]

TIER_EMOJI = {"hot": "🔥 hot", "warm": "🟡 warm", "cold": "❄️ cold"}

def qualify(lead_text: str, model: str):
    if not lead_text.strip():
        return None, "", "", "", "", ""
    try:
        result: LeadScore = _client().beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": LEAD_SYSTEM},
                {"role": "user", "content": lead_text},
            ],
            response_format=LeadScore,
        ).choices[0].message.parsed
    except Exception as e:
        return None, str(e), "", "", "", ""
    return (
        result.score,
        TIER_EMOJI.get(result.tier, result.tier),
        "\n".join(result.criteria_met),
        "\n".join(result.criteria_missed),
        result.recommended_action,
        result.reasoning,
    )

# ── Tab 6: Basic ReAct Agent ──────────────────────────────────────────────────

def _add(x: int, y: int) -> int:
    return x + y

def _multiply(x: int, y: int) -> int:
    return x * y

REACT_TOOLS = [
    {"type": "function", "function": {"name": "add", "description": "Add two integers", "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}}},
    {"type": "function", "function": {"name": "multiply", "description": "Multiply two integers", "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}}},
]
REACT_FNS = {"add": _add, "multiply": _multiply}

REACT_SAMPLES = [
    ["What is (3 + 4) multiplied by 5?"],
    ["Add 15 and 27, then multiply the result by 3."],
    ["A team of 7 earns 450 per person per month. 3 of them receive a 120 bonus. What is the total monthly payroll?"],
    ["What is (12 + 8) × (6 + 4)?"],
]

def run_agent(question: str, model: str):
    if not question.strip():
        return "", ""
    try:
        client = _client()
    except ValueError as e:
        return str(e), ""
    messages = [
        {"role": "system", "content": "You are a math assistant. Solve problems using only the provided tools. Do not compute answers yourself."},
        {"role": "user", "content": question},
    ]
    trace_lines = []
    for step in range(10):
        response = client.chat.completions.create(model=model, messages=messages, tools=REACT_TOOLS, tool_choice="auto")
        msg = response.choices[0].message
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in (msg.tool_calls or [])],
        })
        if msg.tool_calls:
            for tc in msg.tool_calls:
                fn_args = json.loads(tc.function.arguments)
                result = REACT_FNS[tc.function.name](**fn_args)
                args_str = ", ".join(f"{k}={v}" for k, v in fn_args.items())
                trace_lines.append(f"**Step {step + 1}:** `{tc.function.name}({args_str})` → `{result}`")
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})
        else:
            return "\n\n".join(trace_lines) or "_No tools called_", msg.content or ""
    return "\n\n".join(trace_lines), "Max iterations reached."

# ── App ──────────────────────────────────────────────────────────────────────

with gr.Blocks(title="Agent Use Cases") as demo:
    gr.Markdown(
        "# Agent Use Cases\n"
        "Six real-world AI agent demos — structured output via OpenRouter.\n"
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

    with gr.Tab("🎫 Support Ticket Router"):
        gr.Markdown("Paste a customer ticket → routed to the right team with a ready-to-send draft reply.")
        with gr.Row():
            with gr.Column():
                tkt_subject = gr.Textbox(label="Subject")
                tkt_name = gr.Textbox(label="Customer name")
                tkt_email = gr.Textbox(label="Customer email")
                tkt_body = gr.Textbox(label="Ticket body", lines=6)
                tkt_model = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
                tkt_btn = gr.Button("Route & Draft", variant="primary")
                gr.Examples(examples=TICKET_SAMPLES, inputs=[tkt_subject, tkt_name, tkt_email, tkt_body], label="Sample tickets")
            with gr.Column():
                gr.Markdown("#### Classification")
                tkt_urgency = gr.Textbox(label="Urgency", interactive=False)
                tkt_team = gr.Textbox(label="Team", interactive=False)
                tkt_conf = gr.Textbox(label="Confidence", interactive=False)
                tkt_reason = gr.Textbox(label="Reasoning", interactive=False)
                gr.Markdown("#### Draft reply")
                tkt_ds = gr.Textbox(label="Subject", interactive=False)
                tkt_db = gr.Textbox(label="Body", lines=7, interactive=False)
                tkt_note = gr.Textbox(label="Internal note", interactive=False)
                tkt_esc = gr.Textbox(label="Escalate", interactive=False)
        tkt_btn.click(route_and_draft, [tkt_subject, tkt_name, tkt_email, tkt_body, tkt_model],
                      [tkt_urgency, tkt_team, tkt_conf, tkt_reason, tkt_ds, tkt_db, tkt_note, tkt_esc])

    with gr.Tab("🎯 Lead Qualifier"):
        gr.Markdown(
            "Paste inbound lead notes → ICP fit score, tier, and recommended next action.\n\n"
            "**Built for:** sales teams and RevOps who need a first-pass triage before a rep touches a lead."
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
                "**Score → Tier:** `8–10` = 🔥 Hot · `5–7` = 🟡 Warm · `1–4` = ❄️ Cold\n\n"
                "_The model never invents signals — if a criterion isn't mentioned in the notes, it counts as missed._"
            )
        with gr.Row():
            with gr.Column():
                lead_text = gr.Textbox(label="Lead description", lines=10, placeholder="Paste lead notes here…")
                lead_model = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
                lead_btn = gr.Button("Qualify Lead", variant="primary")
                gr.Examples(examples=[[s] for s in LEAD_SAMPLES], inputs=lead_text, label="Sample leads")
            with gr.Column():
                lead_score = gr.Number(label="ICP Score (1–10)")
                lead_tier = gr.Textbox(label="Tier")
                lead_met = gr.Textbox(label="Criteria met")
                lead_missed = gr.Textbox(label="Criteria missed")
                lead_action = gr.Textbox(label="Recommended action")
                lead_reason = gr.Textbox(label="Reasoning", lines=3)
        lead_btn.click(qualify, [lead_text, lead_model],
                       [lead_score, lead_tier, lead_met, lead_missed, lead_action, lead_reason])

    with gr.Tab("🤖 ReAct Agent"):
        gr.Markdown(
            "Ask a multi-step math question → watch the agent chain **add** and **multiply** tool calls to solve it.\n\n"
            "*The agent has no calculator — it can only call tools. This shows what 'agentic' actually means.*"
        )
        with gr.Row():
            with gr.Column(scale=2):
                react_q = gr.Textbox(label="Math question", lines=3, placeholder="e.g. What is (3 + 4) multiplied by 5?")
                react_model = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
                react_btn = gr.Button("Ask Agent", variant="primary")
                gr.Examples(examples=REACT_SAMPLES, inputs=react_q, label="Sample questions")
            with gr.Column(scale=3):
                react_trace = gr.Markdown(label="Tool call trace")
                react_ans = gr.Textbox(label="Final answer", lines=3)
        react_btn.click(run_agent, [react_q, react_model], [react_trace, react_ans])

if __name__ == "__main__":
    demo.launch()
