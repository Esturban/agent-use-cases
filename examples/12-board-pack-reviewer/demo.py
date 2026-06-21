"""Gradio demo — Board Pack Reviewer via OpenRouter structured output."""

import os
import sys

import gradio as gr
from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(raise_error_if_not_found=False))

sys.path.insert(0, os.path.dirname(__file__))
from src.schema import DirectorBriefing  # noqa: E402

SYSTEM_PROMPT = (
    "You are an experienced non-executive director reviewing a board pack before a meeting. "
    "Your job is to protect shareholders and stakeholders — not to make management comfortable.\n\n"
    "Produce a structured briefing with these rules:\n"
    "- Frame every risk as a board concern, not a management update\n"
    "- Name information gaps explicitly — 'the pack does not disclose X' is more useful than silence\n"
    "- Questions for management must be probing: challenge assumptions, not process\n"
    "- overall_pack_quality reflects governance fitness, not length or formatting\n"
    "- If something looks sanitised, incomplete, or is missing context, say so directly\n"
    "- For Saudi/GCC context: flag Saudization (Nitaqat) compliance gaps, Vision 2030 alignment "
    "risks, related party exposure, and any governance structure concerns common in family-owned entities\n\n"
    "You serve shareholders and stakeholders, not management."
)

MODELS = [
    "openai/gpt-5.4-nano",
    "openai/gpt-4.1-nano",
    "openai/gpt-4o",
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "minimax/minimax-m3",
]

# ── Sample 1: Saudi giga-project developer (Vision 2030) ─────────────────────

SAMPLE_PACK_1 = """WADI TAMEER REAL ESTATE DEVELOPMENT CO.
BOARD OF DIRECTORS — MEETING 22 SEPTEMBER 2025
STRICTLY CONFIDENTIAL — FOR DIRECTOR USE ONLY

ATTENDEES: Chairman (Non-Executive), CEO, CFO, Chief Projects Officer, 3 Independent NEDs,
Government Representative (Ministry of Housing, observer)

1. FINANCIAL PERFORMANCE — H1 2025
Revenue: SAR 312m (H1 2024: SAR 218m, +43%)
Gross margin: 18% (H1 2024: 27%) — margin compression driven by subcontractor cost escalation
EBITDA: SAR 22m (budget: SAR 51m, -57%)
Cash: SAR 38m (Dec 2024: SAR 94m) — SAR 56m consumed in H1
Receivables: SAR 189m outstanding, of which SAR 67m is >120 days overdue (government clients)
Net debt: SAR 445m (debt covenants require net debt/EBITDA < 8x; current ratio: 20x)

2. PROJECT PORTFOLIO UPDATE
Active projects: 14 (total contracted value: SAR 2.8bn)
On-time delivery: 4 of 14 projects (29%) — 10 projects report delays of 3-18 months
Cost-to-complete variance: SAR +340m above original project budgets (aggregate across portfolio)
Three government clients (Ministry of Housing, NHC, PIF subsidiary) have issued formal delay notices.
One client (SAR 180m contract) has threatened liquidated damages of up to SAR 36m.

3. RISK REGISTER (management update)
Risks reported: 6 items, all rated "amber" or below. No red-rated risks.
Changes since last meeting: none reported. Risk register last updated March 2025.

4. RELATED PARTY TRANSACTIONS
SAR 78m in subcontracting awarded to Al Qimam Construction (owned by the Chairman's brother-in-law)
in H1 2025. Audit committee approval noted; independent market benchmarking not documented.

5. PEOPLE & SAUDIZATION
Current Nitaqat ratio: 28% Saudi nationals (Platinum band requires 35%)
HRDF penalty risk: company has received one warning letter. Next inspection: October 2025.
Chief Projects Officer has tendered resignation, effective 31 October 2025. Replacement not identified.

6. FINANCING
SAR 200m revolving credit facility due for renewal 30 November 2025. Lead bank (Riyad Bank)
has requested updated financial projections before confirming renewal terms.
Management has not yet engaged the bank on renewal terms.

7. RESOLUTIONS REQUIRED
7.1 Approve revised FY2025 budget (revenue guidance reduced from SAR 720m to SAR 540m)
7.2 Ratify H1 2025 related party transactions (Al Qimam Construction subcontracts)
7.3 Approve interim appointment of Acting Chief Projects Officer
7.4 Authorise management to commence bank negotiations for facility renewal
"""

# ── Sample 2: Saudi family holding company ────────────────────────────────────

SAMPLE_PACK_2 = """AL BARRAK HOLDING GROUP
BOARD OF DIRECTORS — QUARTERLY MEETING Q3 2025
RIYADH — 15 OCTOBER 2025 | CONFIDENTIAL

DIRECTORS PRESENT: Chairman & Founder (H.E. Abdullah Al Barrak), Vice Chairman (son, Fahad Al Barrak),
CEO (non-family), CFO, 2 Independent NEDs, Family Office Representative

1. GROUP FINANCIAL SUMMARY — 9 MONTHS TO SEPTEMBER 2025
Consolidated revenue: SAR 1.04bn (FY target: SAR 1.35bn — 77% achieved at 75% of year)
EBITDA: SAR 89m (margin: 8.6%, prior year: 14.2%)
Net cash position: SAR (212m) — net debt position for first time in group history
Distribution to family shareholders (Q1-Q3 2025): SAR 145m
Capital expenditure (Q1-Q3 2025): SAR 310m (original FY budget: SAR 180m — 172% of full-year budget)

SEGMENT PERFORMANCE:
- Real Estate (42% of revenue): SAR 437m, EBITDA SAR 18m (margin 4.1%)
- Logistics (31% of revenue): SAR 322m, EBITDA SAR 41m (margin 12.7%)
- Food & Hospitality (27% of revenue): SAR 281m, EBITDA SAR 30m (margin 10.7%)

2. STRATEGIC UPDATE — NEOM LOGISTICS PARTNERSHIP
Management proposes a joint venture with a European logistics operator to bid for a SAR 800m
NEOM supply chain contract. JV requires Al Barrak to contribute SAR 120m in equity by Q1 2026.
Due diligence on the European partner has not commenced. No formal business plan presented.
Board asked to approve the JV framework agreement today.

3. RISK REGISTER
Format unchanged from Q1 2023. Risks listed: commodity prices, labour, regulatory.
No financial leverage risk noted despite group moving to net debt position.
No succession risk noted despite Chairman being 74 years old and no documented succession plan.

4. PEOPLE
CEO (non-family) has been in role 11 months. Previous CEO resigned after 7 months.
No reason given for prior CEO departure in this or previous board packs.
Fahad Al Barrak (Vice Chairman) is actively involved in day-to-day operations
of the Real Estate segment alongside the segment GM — dual authority structure not resolved.

5. SAUDIZATION & COMPLIANCE
Nitaqat ratio: 34% (Platinum band: 35% required). One percentage point below threshold.
3 Saudi graduates hired under the government Tamheer programme left within 4 months.
ZATCA e-invoicing Phase 2 integration: management reports "in progress" — no completion date.

6. RESOLUTIONS REQUIRED
6.1 Approve NEOM JV framework agreement (SAR 120m equity commitment)
6.2 Approve revised FY2025 capex budget (increase from SAR 180m to SAR 390m)
6.3 Approve Q4 2025 family distribution of SAR 60m
"""

# ── Sample 3: Saudi private healthcare group ──────────────────────────────────

SAMPLE_PACK_3 = """SHIFAA HEALTHCARE GROUP
BOARD OF DIRECTORS — MEETING 8 OCTOBER 2025
STRICTLY CONFIDENTIAL

DIRECTORS PRESENT: Chairman (Independent NED), CEO, CFO, CMO, COO,
2 Independent NEDs, MOH Representative (observer), PIF Representative (minority shareholder, 30%)

1. FINANCIAL PERFORMANCE — 9M 2025
Revenue: SAR 628m (9M 2024: SAR 541m, +16%)
EBITDA: SAR 71m (margin: 11.3%, target: 18%)
Occupancy rate: 61% across 3 hospitals (benchmark for breakeven: 68%)
Average revenue per bed per day: SAR 2,840 (regional peer median: SAR 3,650)
Payor mix: 58% insurance, 34% self-pay, 8% government — insurance payor disputes up 41% YoY

2. CCHI ACCREDITATION STATUS
Al Riyadh Hospital (flagship, 280 beds): CCHI accreditation expired August 2025.
Renewal inspection scheduled November 2025. Management rates risk as "low."
Operating without valid CCHI accreditation exposes the hospital to suspension of insurance
reimbursements (SAR 14m/month) and potential MOH enforcement.

3. EXPANSION PROJECT — JEDDAH HOSPITAL (240 BEDS)
Construction: 78% complete (original target: 100% by June 2025, now guided Q2 2026)
Total project cost: SAR 420m (original budget: SAR 310m, +35% overrun)
Medical equipment procurement: not commenced. Lead time: 6-9 months.
Opening Q2 2026 is at material risk without immediate equipment orders.
No commissioning plan or staff recruitment plan presented.

4. INSURANCE RECEIVABLES
Outstanding insurance receivables: SAR 184m (DSO: 107 days; benchmark: 45 days)
Bupa Arabia (32% of insurance revenue): dispute over SAR 38m in denied claims — under arbitration.
No provision taken against disputed receivables in management accounts.

5. PEOPLE
CMO has not attended last 3 board meetings. No explanation provided in pack.
Nursing vacancy rate: 31% (target: <10%). Agency nursing cost: SAR 8.4m in 9M 2025.
Saudization (Nitaqat): 19% Saudi nationals (healthcare sector minimum: 15% — currently compliant,
but MOH has signalled the threshold will rise to 25% by 2027).

6. RESOLUTIONS REQUIRED
6.1 Approve additional Jeddah Hospital construction funding: SAR 80m
6.2 Approve medical equipment procurement mandate (SAR 55m)
6.3 Receive CCHI accreditation update (for noting — no resolution proposed)
"""

QUALITY_LABEL = {
    "strong": "✅ Strong — governance-ready pack",
    "adequate": "🟡 Adequate — usable but gaps exist",
    "weak": "🔴 Weak — material gaps, exercise caution before approving resolutions",
}

SEVERITY_ICON = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
}


def _format_risks(risks: list) -> str:
    if not risks:
        return "_No material risks identified._"
    lines = []
    for r in sorted(risks, key=lambda x: x.rank):
        icon = SEVERITY_ICON.get(r.severity, "")
        lines.append(
            f"**{r.rank}. {icon} {r.title}**\n"
            f"_{r.area.title()} risk · Severity: {r.severity}_\n\n"
            f"{r.detail}\n\n"
            f"Source: *{r.source_section}*\n\n"
            f"**Question to ask management:** {r.suggested_question}"
        )
    return "\n\n---\n\n".join(lines)


def _format_gaps(gaps: list) -> str:
    if not gaps:
        return "_No material information gaps identified._"
    return "\n\n".join(
        f"**{g.section}**\nMissing: {g.missing}\n\nWhy it matters: _{g.why_it_matters}_"
        for g in gaps
    )


def _format_decisions(decisions: list) -> str:
    if not decisions:
        return "_No formal resolutions in this pack._"
    parts = []
    for d in decisions:
        block = f"**{d.item}**\n\n{d.context}\n\n"
        if d.recommendation:
            block += f"Management recommends: *{d.recommendation}*\n\n"
        block += f"Key consideration before voting: **{d.key_consideration}**"
        parts.append(block)
    return "\n\n---\n\n".join(parts)


def review_board_pack(pack_text: str, model: str):
    if not pack_text.strip():
        return "", "", "", "", "", ""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise gr.Error("OPENAI_API_KEY is not set — export it in your shell or add it as a Space secret.")
    try:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Board pack to review:\n\n" + pack_text},
            ],
            response_format=DirectorBriefing,
        )
        r: DirectorBriefing = completion.choices[0].message.parsed
        if r is None:
            raise gr.Error(
                f"The model '{model}' did not return a structured response. "
                "Try openai/gpt-4o-mini or openai/gpt-4.1-nano — both reliably support structured output."
            )
    except gr.Error:
        raise
    except Exception as exc:
        raise gr.Error(f"API error: {exc}") from exc

    questions = "\n".join(f"• {q}" for q in r.questions_for_management)
    return (
        QUALITY_LABEL.get(r.overall_pack_quality, r.overall_pack_quality),
        r.executive_assessment,
        _format_risks(r.top_risks),
        _format_gaps(r.information_gaps),
        _format_decisions(r.decisions_required),
        questions,
    )


with gr.Blocks(title="Board Pack Reviewer") as demo:
    gr.Markdown(
        "## Board Pack Reviewer\n"
        "Paste any board pack and the AI reads it as an experienced independent director — "
        "identifying what management is downplaying, what information is missing, "
        "what the real risks are, and what questions to ask before approving anything.\n\n"
        "**Who this is for:** board directors, governance advisors, and investors who need to cut "
        "through management language quickly and walk into a meeting prepared."
    )

    with gr.Accordion("What the AI looks for — and what it produces", open=True):
        gr.Markdown(
            "Most board packs are written by management, for management. "
            "The AI reads them from the opposite direction — looking for what is being hidden, "
            "softened, or simply left out.\n\n"
            "| Output | What it tells you |\n"
            "|--------|-------------------|\n"
            "| **Pack quality rating** | Is this a governance-ready document or does it obscure more than it reveals? |\n"
            "| **Director briefing** | A 4-sentence summary you can read in the car on the way to the meeting |\n"
            "| **Top risks** | Up to 5 risks ranked by severity — framed as board concerns, not management euphemisms |\n"
            "| **Information gaps** | What the pack fails to disclose that the board needs before voting |\n"
            "| **Decisions required** | Every resolution dissected: what you are being asked to approve and what could go wrong |\n"
            "| **Questions for management** | Sharp, probing questions — not procedural check-ins |\n\n"
            "The AI is trained to flag Saudi-specific governance risks: Nitaqat compliance, "
            "Vision 2030 project delivery, related party transactions, and ZATCA/CCHI regulatory exposure.\n\n"
            "**Three sample board packs are pre-loaded — click any to try:**\n"
            "- _Wadi Tameer Real Estate: giga-project developer with cost overruns, covenant breach risk, "
            "and a related party transaction that needs scrutiny_\n"
            "- _Al Barrak Holding: family conglomerate moving to net debt while paying dividends and "
            "committing to a SAR 120m JV with no due diligence_\n"
            "- _Shifaa Healthcare: private hospital group with lapsed CCHI accreditation, "
            "a Jeddah expansion 35% over budget, and SAR 184m in disputed receivables_"
        )

    with gr.Row():
        with gr.Column(scale=2):
            pack_input = gr.Textbox(
                label="Board pack",
                lines=28,
                placeholder=(
                    "Paste the board pack text here.\n\n"
                    "Include: financial performance, strategic updates, risk register, "
                    "people/HR updates, and the resolutions management is asking the board to approve.\n\n"
                    "The more detail you include, the sharper the analysis."
                ),
                value=SAMPLE_PACK_1,
            )
            model_dd = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Review Board Pack", variant="primary")
            gr.Examples(
                examples=[[SAMPLE_PACK_1], [SAMPLE_PACK_2], [SAMPLE_PACK_3]],
                inputs=[pack_input],
                label="Sample board packs — click to load",
            )

        with gr.Column(scale=3):
            quality_out = gr.Textbox(
                label="Pack quality",
                interactive=False,
            )
            assessment_out = gr.Textbox(
                label="Director briefing — read this before anything else",
                lines=5,
                interactive=False,
            )
            gr.Markdown("#### Risks — ranked by severity")
            risks_out = gr.Markdown()
            gr.Markdown("#### Information gaps — what the pack fails to disclose")
            gaps_out = gr.Markdown()
            gr.Markdown("#### Decisions required — what you are being asked to approve")
            decisions_out = gr.Markdown()
            questions_out = gr.Textbox(
                label="Questions to ask management in the meeting",
                lines=8,
                interactive=False,
            )

    run_btn.click(
        fn=review_board_pack,
        inputs=[pack_input, model_dd],
        outputs=[quality_out, assessment_out, risks_out, gaps_out, decisions_out, questions_out],
    )

if __name__ == "__main__":
    demo.launch()
