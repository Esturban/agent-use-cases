"""Gradio demo — Security Operations Supervisor.

Pick a daily digest preset, run the supervisor, and -- if any finding is
P0/P1 -- review and resolve the human-approval gate before the posture
brief is shown. Same two-stage shape as the 90-approval-gate-pattern demo,
applied on top of conditional multi-domain dispatch.
"""

import json
import os

import gradio as gr
from dotenv import load_dotenv

from main import _busy_day_digest, _quiet_day_digest
from src.schema import ApprovalDecision
from src.workflow import propose, resume

load_dotenv()

CSS = """
.badge {
    display: inline-block;
    padding: 5px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85em;
    letter-spacing: 0.03em;
}
.badge-green  { background: #d1fae5; color: #065f46; }
.badge-red    { background: #fee2e2; color: #991b1b; }
.badge-orange { background: #fef3c7; color: #92400e; }
.badge-gray   { background: #f3f4f6; color: #374151; }
footer { display: none !important; }
"""

HEADER = """\
# 91 · Security Operations Supervisor
Run a daily security signal digest and see which specialists actually get called, and what it takes for a risky recommendation to become an approved action.

> Only the domains with active signal in the digest run at all. If the most urgent finding is P0/P1,\
 the brief pauses for a real human decision -- approve, edit the payload, or reject -- before that\
 recommendation is treated as anything more than a suggestion.
"""

PRESETS = {
    "Busy day -- correlated P0 incident": _busy_day_digest,
    "Quiet day -- single low-severity CVE": _quiet_day_digest,
}

_POSTURE_KIND = {"red": "red", "amber": "orange", "green": "green"}
_SEVERITY_KIND = {"P0": "red", "P1": "orange", "P2": "gray", "P3": "gray"}


def _badge(text: str, kind: str) -> str:
    cls = {"green": "badge-green", "red": "badge-red", "orange": "badge-orange"}.get(
        kind, "badge-gray"
    )
    return f'<span class="badge {cls}">{text.upper()}</span>'


def _brief_rows(brief):
    return [
        [finding.severity, finding.domain, finding.summary, finding.recommended_action]
        for finding in brief.findings
    ]


def run_propose(preset_name):
    digest = PRESETS[preset_name]()
    result = propose(digest)

    if result["status"] == "paused":
        finding = result["finding"]
        proposed = result["proposed_action"]
        return (
            _badge(f"paused -- {finding.severity} {finding.domain}", "orange"),
            finding.summary,
            proposed.payload,
            result["thread_id"],
            "",
            [],
            json.dumps(proposed.payload, indent=2),
        )

    brief = result["brief"]
    return (
        _badge(f"complete -- {brief.overall_posture}", _POSTURE_KIND[brief.overall_posture]),
        "No P0/P1 finding required the approval gate.",
        {},
        None,
        "\n".join(brief.cross_domain_correlations) or "(none)",
        _brief_rows(brief),
        "",
    )


def run_resume(thread_id, decision, edited_payload_text, rationale):
    if not thread_id:
        raise gr.Error("Run a digest that pauses at the approval gate first.")
    if not rationale or not rationale.strip():
        raise gr.Error("A rationale is required for every decision.")

    edited_payload = None
    if decision == "edit":
        if not edited_payload_text or not edited_payload_text.strip():
            raise gr.Error("Decision is 'edit' but no edited payload was provided.")
        try:
            edited_payload = json.loads(edited_payload_text)
        except json.JSONDecodeError as exc:
            raise gr.Error(f"Edited payload is not valid JSON: {exc}") from exc

    approval = ApprovalDecision(decision=decision, edited_payload=edited_payload, rationale=rationale)
    resumed = resume(thread_id, approval)
    brief = resumed["brief"]
    gate_result = resumed["gate_result"]
    status_kind = "green" if gate_result.executed else "red"
    return (
        _badge(f"{'executed' if gate_result.executed else 'blocked'} -- {brief.overall_posture}", status_kind),
        gate_result.decision_log,
        "\n".join(brief.cross_domain_correlations) or "(none)",
        _brief_rows(brief),
    )


with gr.Blocks(title="Security Operations Supervisor", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(HEADER)

    thread_state = gr.State(None)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1 · Run the daily digest")
            preset_input = gr.Dropdown(
                choices=list(PRESETS.keys()),
                label="Digest preset",
                value=list(PRESETS.keys())[0],
            )
            propose_btn = gr.Button("Run Daily Brief", variant="primary")

            gr.Markdown("### 2 · Resolve the gate (if paused)")
            decision_input = gr.Radio(
                choices=["approve", "edit", "reject"], label="Decision", value="approve"
            )
            edited_payload_input = gr.Code(
                label="Edited payload (JSON, used only when decision = edit)",
                language="json",
                lines=4,
            )
            rationale_input = gr.Textbox(
                label="Rationale", lines=2, placeholder="Why -- always logged, even on approve."
            )
            resume_btn = gr.Button("Submit Decision", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### Status")
            status_out = gr.HTML(label="Status")
            gate_detail_out = gr.Textbox(label="Gate detail / audit log", lines=2, interactive=False)
            gate_payload_out = gr.JSON(label="Proposed payload (while paused)")

            gr.Markdown("### Posture brief")
            correlations_out = gr.Textbox(label="Cross-domain correlations", lines=2, interactive=False)
            findings_out = gr.Dataframe(
                headers=["Severity", "Domain", "Summary", "Recommended action"],
                label="Findings",
                interactive=False,
                wrap=True,
            )

    propose_btn.click(
        fn=run_propose,
        inputs=[preset_input],
        outputs=[
            status_out,
            gate_detail_out,
            gate_payload_out,
            thread_state,
            correlations_out,
            findings_out,
            edited_payload_input,
        ],
    )

    resume_btn.click(
        fn=run_resume,
        inputs=[thread_state, decision_input, edited_payload_input, rationale_input],
        outputs=[status_out, gate_detail_out, correlations_out, findings_out],
    )

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set — copy .env.example to .env")
    demo.launch()
