"""Gradio demo — Commercial Due Diligence via OpenRouter structured output."""

import os
import sys

import gradio as gr
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(raise_error_if_not_found=False))

sys.path.insert(0, os.path.dirname(__file__))
from src.schema import DDReport, DocumentFindings  # noqa: E402

EXTRACTOR_SYSTEM = (
    "You are a due diligence analyst extracting structured findings from a single document. "
    "Be specific and factual. Every key_finding must be a concrete, verifiable statement from "
    "the document -- not an interpretation or inference. Every red_flag must cite specific "
    "evidence. Do not repeat the same finding in both key_findings and red_flags."
)

SYNTHESISER_SYSTEM = (
    "You are a senior M&A advisor synthesising multiple due diligence document reviews "
    "into a unified risk register for a deal committee. "
    "Consolidate overlapping findings, score each risk on severity and likelihood, "
    "source every risk item to the document(s) it came from, and make a clear "
    "overall_assessment (proceed / proceed_with_conditions / do_not_proceed). "
    "Do not pad the report with low-quality observations. Quality over quantity."
)

SAMPLE_DOCS = {
    "Management Accounts (FY2024)": """\
ACME TECHNOLOGIES LTD -- MANAGEMENT ACCOUNTS FY2024 (UNAUDITED)

Revenue: GBP 4.2m (FY2023: GBP 3.1m, +35%)
Gross margin: 61% | EBITDA: GBP 0.3m | Net cash: GBP 0.1m | Burn: GBP 180k/mo

Revenue: RetailCo GBP 2.1m (50%) | LogisCorp GBP 0.8m (19%) | Other GBP 1.3m
Recurring SaaS: 68% | Professional services: 32%

Headcount: 34 FTE. Three senior engineers resigned in Q4 2024.
Debtor days: 87 (benchmark: 45). Two RetailCo invoices GBP 310k overdue 90+ days.""",
    "Key Customer Contract (RetailCo)": """\
MASTER SERVICES AGREEMENT -- ACME TECHNOLOGIES LTD AND RETAILCO PLC

Term: 24 months, expires 28 Feb 2025. No auto-renewal. ACV: GBP 2.1m.
Termination for Convenience: 30-day notice, no fee.
IP: All custom dev for RetailCo becomes RetailCo's property.
SLA breach (3 consecutive months below 99.5%) entitles RetailCo to terminate without penalty.
Annual benchmarking: RetailCo can demand renegotiation if pricing >15% above market.""",
    "CEO Biography": """\
JAMES WHITFIELD -- CO-FOUNDER AND CEO

Co-founded Acme 2019. BSc Computer Science. Owns 45%. Co-founder Sarah Chen (CTO) owns 40%.
Prior venture: DataFlow Ltd (2014) entered administration 2017. Creditors received 12p/GBP.
James relocating to Singapore Q3 2025; remote working agreed for 12 months.""",
    "ICO Enforcement Notice": """\
INFORMATION COMMISSIONER'S OFFICE -- ENFORCEMENT NOTICE (14 Nov 2024)

Acme breached UK GDPR Article 32: data incident Aug 2024, ~12,000 RetailCo customer records exposed.
Required: comprehensive infosec programme by 31 Mar 2025; appoint DPO by 28 Feb 2025.
Penalty if non-compliant: up to GBP 17.5m or 4% of global turnover.""",
}

ASSESSMENT_LABELS = {
    "proceed": "✅ Proceed",
    "proceed_with_conditions": "⚠️ Proceed with conditions",
    "do_not_proceed": "🔴 Do not proceed",
}
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
MODELS = [
    "openai/gpt-5.4-nano",
    "minimax/minimax-m3",
    "openai/gpt-4.1-nano",
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]


def _extract(client: OpenAI, model: str, doc_name: str, doc_text: str) -> DocumentFindings:
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": EXTRACTOR_SYSTEM},
            {"role": "user", "content": f"Document name: {doc_name}\n\nDocument text:\n{doc_text}"},
        ],
        response_format=DocumentFindings,
    )
    return completion.choices[0].message.parsed


def _synthesise(client: OpenAI, model: str, all_findings: list) -> DDReport:
    findings_text = "\n\n".join(
        f"=== {f.document_name} ({f.document_type}) ===\n"
        "Key findings:\n" + "\n".join(f"- {x}" for x in f.key_findings) + "\n"
        "Red flags:\n" + "\n".join(f"- {x}" for x in f.red_flags) + "\n"
        "Questions raised:\n" + "\n".join(f"- {x}" for x in f.questions_raised)
        for f in all_findings
    )
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYNTHESISER_SYSTEM},
            {
                "role": "user",
                "content": "Synthesise the following per-document findings into a unified DD report:\n\n"
                + findings_text,
            },
        ],
        response_format=DDReport,
    )
    return completion.choices[0].message.parsed


def _format_risks(report: DDReport) -> str:
    if not report.risk_items:
        return "No risks identified."
    risks = sorted(report.risk_items, key=lambda r: (SEVERITY_ORDER.get(r.severity, 9), r.area))
    lines = []
    for r in risks:
        icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(r.severity, "")
        lines.append(f"### {icon} {r.title} ({r.area})")
        lines.append(f"**Severity:** {r.severity} | **Likelihood:** {r.likelihood}  ")
        lines.append(f"**Finding:** {r.finding}  ")
        lines.append(f"**Source:** {r.source_document}  ")
        lines.append(f"**Mitigation:** {r.mitigation}")
        lines.append("")
    return "\n".join(lines)


def run_dd(d1n, d1t, d2n, d2t, d3n, d3t, d4n, d4t, model):
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return "Set OPENAI_API_KEY env var", "", "", "", ""
    docs = {n: t for n, t in [(d1n, d1t), (d2n, d2t), (d3n, d3t), (d4n, d4t)] if n.strip() and t.strip()}
    if not docs:
        return "No documents provided.", "", "", "", ""
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    all_findings = [_extract(client, model, name, text) for name, text in docs.items()]
    report = _synthesise(client, model, all_findings)
    assessment = ASSESSMENT_LABELS.get(report.overall_assessment, report.overall_assessment)
    conditions = "\n".join(f"• {c}" for c in report.key_conditions) or "None"
    further = "\n".join(f"• {f}" for f in report.further_investigation) or "None"
    return assessment, report.executive_summary, conditions, further, _format_risks(report)


sample_names = list(SAMPLE_DOCS.keys()) + [""] * 4
sample_texts = list(SAMPLE_DOCS.values()) + [""] * 4

with gr.Blocks(title="Due Diligence Analyzer") as demo:
    gr.Markdown(
        "## 🔍 Commercial Due Diligence\n"
        "Paste up to 4 deal documents → the agent extracts findings from each in parallel, "
        "then synthesises a unified risk register with an overall deal verdict.\n\n"
        "**Built for:** M&A advisors, corporate development teams, and PE analysts who need "
        "a structured first-pass risk register before committing to full diligence."
    )

    with gr.Accordion("How it works — 2-step agent pipeline", open=True):
        gr.Markdown(
            "**Step 1 — Extract:** one API call per document pulls key findings, red flags, "
            "and unanswered questions from each source independently.\n\n"
            "**Step 2 — Synthesise:** a second call consolidates all per-document findings "
            "into a unified risk register, scores each risk by severity and likelihood, "
            "and returns a deal verdict: Proceed / Proceed with conditions / Do not proceed.\n\n"
            "| Risk level | Meaning |\n"
            "|------------|--------|\n"
            "| 🔴 Critical | Deal-breaker — must resolve before proceeding |\n"
            "| 🟠 High | Material risk — negotiate conditions or price adjust |\n"
            "| 🟡 Medium | Monitor — flag in SPA reps & warranties |\n"
            "| 🟢 Low | Note for record — not a blocker |\n\n"
            "_Sample: Acme Technologies Ltd — Series B target with customer concentration, "
            "ICO enforcement action, and a CEO relocation risk._"
        )

    with gr.Accordion("Documents (edit or replace)", open=True):
        doc_rows = []
        for i in range(4):
            with gr.Row():
                nb = gr.Textbox(label=f"Doc {i+1} name", value=sample_names[i], scale=1)
                tb = gr.Textbox(label=f"Doc {i+1} text", value=sample_texts[i], lines=5, scale=3)
                doc_rows.append((nb, tb))

    model_select = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model (via OpenRouter)")
    run_btn = gr.Button("Run Due Diligence", variant="primary")
    assessment_out = gr.Textbox(label="Overall assessment", interactive=False)
    summary_out = gr.Textbox(label="Executive summary", lines=3, interactive=False)
    conditions_out = gr.Textbox(label="Key conditions", lines=3, interactive=False)
    further_out = gr.Textbox(label="Further investigation", lines=3, interactive=False)
    risks_out = gr.Markdown(label="Risk register")

    flat_inputs = [x for pair in doc_rows for x in pair] + [model_select]
    run_btn.click(
        fn=run_dd,
        inputs=flat_inputs,
        outputs=[assessment_out, summary_out, conditions_out, further_out, risks_out],
    )

if __name__ == "__main__":
    demo.launch()
