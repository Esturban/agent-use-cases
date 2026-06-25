"""Gradio demo — Onboarding Orchestrator via OpenRouter structured output."""

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import gradio as gr
from openai import OpenAI

from src.schema import NewHire, OnboardingPlan, SubAgentStatus

IT_SYSTEM = (
    "You are an IT provisioning specialist. Given a new hire's details, produce a SubAgentStatus "
    "for the IT domain. Include all hardware, software, access, and account setup tasks. "
    "Identify which tasks can be completed before Day 1 (completed) and which require the "
    "employee to be present (pending). Flag any blockers in notes."
)
HR_SYSTEM = (
    "You are an HR onboarding specialist. Given a new hire's details, produce a SubAgentStatus "
    "for the HR domain. Include contract signing, payroll setup, benefits enrollment, policy "
    "acknowledgements, and compliance training. Identify tasks completable before Day 1 and "
    "those requiring the employee (pending). Flag any blockers in notes."
)
FACILITIES_SYSTEM = (
    "You are a Facilities coordinator. Given a new hire's details, produce a SubAgentStatus "
    "for the Facilities domain. Include desk assignment, access badge, parking, building tour, "
    "and equipment delivery. Identify tasks completable before Day 1 and those requiring "
    "the employee to be present (pending). Flag any blockers in notes."
)
SYNTHESIS_SYSTEM = (
    "You are an onboarding programme manager. Given the new hire's details and the IT, HR, "
    "and Facilities sub-agent reports, produce a complete OnboardingPlan. "
    "Set day1_ready to true only if there are no blocking tasks across all three domains. "
    "List all blockers. Write a 2-3 sentence summary of overall readiness."
)

MODELS = [
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]


def _run_sub_agent(client: OpenAI, model: str, system: str, new_hire: NewHire) -> SubAgentStatus:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(new_hire.model_dump())},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "SubAgentStatus",
                "strict": True,
                "schema": SubAgentStatus.model_json_schema(),
            },
        },
    )
    return SubAgentStatus.model_validate_json(response.choices[0].message.content)


def _synthesise(
    client: OpenAI,
    model: str,
    new_hire: NewHire,
    it: SubAgentStatus,
    hr: SubAgentStatus,
    facilities: SubAgentStatus,
) -> OnboardingPlan:
    payload = {
        "new_hire": new_hire.model_dump(),
        "it": it.model_dump(),
        "hr": hr.model_dump(),
        "facilities": facilities.model_dump(),
    }
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYNTHESIS_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "OnboardingPlan",
                "strict": True,
                "schema": OnboardingPlan.model_json_schema(),
            },
        },
    )
    return OnboardingPlan.model_validate_json(response.choices[0].message.content)


def _fmt_domain(status: SubAgentStatus) -> str:
    lines = []
    if status.completed:
        lines.append("**Pre-Day-1 (completable now):**")
        lines.extend(f"- ✅ {t}" for t in status.completed)
    if status.pending:
        lines.append("\n**Requires Day 1:**")
        lines.extend(f"- ⏳ {t}" for t in status.pending)
    if status.notes:
        lines.append(f"\n**Notes:** {status.notes}")
    return "\n".join(lines)


def run_onboarding(name, role, department, start_date, location, model):
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return "Set OPENROUTER_API_KEY env var", "", "", ""
    if not name.strip() or not role.strip():
        return "Fill in Name and Role at minimum.", "", "", ""

    new_hire = NewHire(
        name=name.strip(),
        role=role.strip(),
        department=department.strip(),
        start_date=start_date.strip(),
        location=location.strip(),
    )
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    results = {}
    domain_map = {"it": IT_SYSTEM, "hr": HR_SYSTEM, "facilities": FACILITIES_SYSTEM}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_run_sub_agent, client, model, system, new_hire): key
            for key, system in domain_map.items()
        }
        for future in as_completed(futures):
            results[futures[future]] = future.result()

    plan = _synthesise(client, model, new_hire, **results)

    readiness = "✅ Day 1 Ready" if plan.day1_ready else "⚠️ Blockers — not Day 1 ready"
    blockers = "\n".join(f"• {b}" for b in plan.blockers) if plan.blockers else "None"
    summary = f"**{readiness}**\n\n{plan.summary}\n\n**Blockers:**\n{blockers}"
    return summary, _fmt_domain(plan.it_status), _fmt_domain(plan.hr_status), _fmt_domain(plan.facilities_status)


with gr.Blocks(title="Onboarding Orchestrator") as demo:
    gr.Markdown(
        "## Onboarding Orchestrator\n"
        "Enter new hire details. IT, HR, and Facilities agents run in parallel — "
        "a coordinator then synthesises a Day 1 readiness plan."
    )
    with gr.Row():
        with gr.Column(scale=1):
            name_in = gr.Textbox(label="Full name", value="Alice Johnson")
            role_in = gr.Textbox(label="Role", value="Senior Software Engineer")
            dept_in = gr.Textbox(label="Department", value="Engineering")
            date_in = gr.Textbox(label="Start date (YYYY-MM-DD)", value="2026-07-14")
            loc_in = gr.Textbox(label="Location", value="London")
            model_sel = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model (via OpenRouter)")
            run_btn = gr.Button("Generate Plan", variant="primary")
        with gr.Column(scale=2):
            summary_out = gr.Markdown(label="Readiness summary")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### IT")
            it_out = gr.Markdown()
        with gr.Column():
            gr.Markdown("### HR")
            hr_out = gr.Markdown()
        with gr.Column():
            gr.Markdown("### Facilities")
            fac_out = gr.Markdown()

    run_btn.click(
        fn=run_onboarding,
        inputs=[name_in, role_in, dept_in, date_in, loc_in, model_sel],
        outputs=[summary_out, it_out, hr_out, fac_out],
    )

if __name__ == "__main__":
    demo.launch()
