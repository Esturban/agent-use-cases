"""Gradio demo -- Ledger Integrity Supervisor.

Pick a close-cycle preset, run the five deterministic checks, and -- if the
most material exception crosses the materiality threshold -- review and
resolve the human-controller approval gate before the final register and
audit narrative are shown.
"""

import json
import os

import gradio as gr
from dotenv import load_dotenv

from main import _clean_close_cycle, _correlated_close_cycle
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
# 97 · Ledger Integrity Supervisor
Run a period-close cycle through five deterministic control checks and see what it takes for the most material finding to become a controller-approved action.

> Journal-entry balance, bank matching, fixed-asset math, fraud rules, and segregation-of-duties\
 checks all run in plain Python -- no model judgment where a computed answer exists. If the most\
 material finding crosses the materiality threshold, the close pauses for a real controller\
 decision before it can be marked anything but blocked.
"""

PRESETS = {
    "Correlated -- P0 finding across 3 domains": _correlated_close_cycle,
    "Clean close -- nothing crosses materiality": _clean_close_cycle,
}

_STATUS_KIND = {"blocked": "red", "conditionally_closed": "orange", "closed": "green"}


def _badge(text: str, kind: str) -> str:
    cls = {"green": "badge-green", "red": "badge-red", "orange": "badge-orange"}.get(
        kind, "badge-gray"
    )
    return f'<span class="badge {cls}">{text.upper()}</span>'


def _register_rows(register):
    return [
        [exc.severity, exc.domain, exc.description, f"${exc.financial_exposure:,.2f}"]
        for exc in register.exceptions
    ]


def run_propose(preset_name):
    close_data = PRESETS[preset_name]()
    result = propose(close_data)

    if result["status"] == "paused":
        exc = result["exception"]
        proposed = result["proposed_action"]
        return (
            _badge(f"paused -- {exc.severity} {exc.domain}", "orange"),
            exc.description,
            proposed.payload,
            result["thread_id"],
            "",
            [],
            json.dumps(proposed.payload, indent=2),
        )

    register = result["register"]
    return (
        _badge(f"complete -- {register.close_status}", _STATUS_KIND[register.close_status]),
        "No exception required the approval gate.",
        {},
        None,
        register.audit_narrative or "",
        _register_rows(register),
        "",
    )


def run_resume(thread_id, decision, edited_payload_text, rationale):
    if not thread_id:
        raise gr.Error("Run a close cycle that pauses at the approval gate first.")
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
    register = resumed["register"]
    gate_result = resumed["gate_result"]
    status_kind = "green" if gate_result.executed else "red"
    return (
        _badge(
            f"{'executed' if gate_result.executed else 'blocked'} -- {register.close_status}",
            status_kind,
        ),
        gate_result.decision_log,
        register.audit_narrative or "",
        _register_rows(register),
    )


with gr.Blocks(title="Ledger Integrity Supervisor", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(HEADER)

    thread_state = gr.State(None)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1 · Run the close cycle")
            preset_input = gr.Dropdown(
                choices=list(PRESETS.keys()),
                label="Close cycle preset",
                value=list(PRESETS.keys())[0],
            )
            propose_btn = gr.Button("Run Close Cycle", variant="primary")

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

            gr.Markdown("### Controls exception register")
            narrative_out = gr.Textbox(label="Audit narrative", lines=4, interactive=False)
            findings_out = gr.Dataframe(
                headers=["Severity", "Domain", "Description", "Financial exposure"],
                label="Exceptions",
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
            narrative_out,
            findings_out,
            edited_payload_input,
        ],
    )

    resume_btn.click(
        fn=run_resume,
        inputs=[thread_state, decision_input, edited_payload_input, rationale_input],
        outputs=[status_out, gate_detail_out, narrative_out, findings_out],
    )

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set -- copy .env.example to .env")
    demo.launch()
