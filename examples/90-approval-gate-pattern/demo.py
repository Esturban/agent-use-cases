"""Gradio demo — Approval Gate Pattern.

Two-stage interaction on purpose: "Propose" runs the graph up to the
interrupt and genuinely halts (thread_id is stashed in gr.State); "Submit
Decision" is a separate click that calls resume() with whatever the human
picked. Nothing downstream of human_review is reachable until that second
click fires -- the same gate main.py exercises with scripted decisions, here
driven by real UI input.
"""

import json
import os

import gradio as gr
from dotenv import load_dotenv

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
# 90 · Approval Gate Pattern
Draft an irreversible action, then gate it behind a real human decision before anything executes.

> **Harness concept — interrupt-and-resume gate:** "Propose" runs the graph up to `human_review` and\
 the graph genuinely halts there via a checkpointer. Nothing in `execute_or_log` is reachable until\
 "Submit Decision" resumes the same paused run with your decision. Reject or edit and the original\
 draft never silently fires.
"""

SCENARIOS = [
    "Post a $4,200 accrual for Q2 consulting fees to cost centre CC1001.",
    "Revoke admin access for the contractor identity CTR-4471, offboarding effective today.",
    "Send a final notice collection letter to customer ACME Corp for invoice INV-9981, "
    "$58,000 outstanding 95 days.",
]


def _badge(text: str, kind: str) -> str:
    cls = {"green": "badge-green", "red": "badge-red", "orange": "badge-orange"}.get(
        kind, "badge-gray"
    )
    return f'<span class="badge {cls}">{text.upper()}</span>'


def run_propose(event_description):
    if not event_description or not event_description.strip():
        raise gr.Error("Enter an event description first.")
    proposed, thread_id = propose(event_description)
    risk_kind = {"low": "green", "medium": "orange", "high": "red"}.get(
        proposed.risk_level, "gray"
    )
    return (
        proposed.action_type,
        proposed.summary,
        proposed.payload,
        _badge(proposed.risk_level, risk_kind),
        json.dumps(proposed.payload, indent=2),
        thread_id,
        proposed.payload,
        "",
        "",
        "",
    )


def run_resume(thread_id, decision, edited_payload_text, rationale):
    if not thread_id:
        raise gr.Error("Propose an action before submitting a decision.")
    if not rationale or not rationale.strip():
        raise gr.Error("A rationale is required for every decision.")

    edited_payload = None
    if decision == "edit":
        try:
            edited_payload = json.loads(edited_payload_text)
        except json.JSONDecodeError as exc:
            raise gr.Error(f"Edited payload is not valid JSON: {exc}") from exc

    approval = ApprovalDecision(
        decision=decision, edited_payload=edited_payload, rationale=rationale
    )
    result = resume(thread_id, approval)
    status_kind = "green" if result.executed else "red"
    return (
        _badge("executed" if result.executed else "blocked", status_kind),
        result.final_payload or {},
        result.decision_log,
    )


with gr.Blocks(title="Approval Gate Pattern", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(HEADER)

    thread_state = gr.State(None)
    proposed_payload_state = gr.State(None)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1 · Propose")
            event_input = gr.Textbox(
                label="Event description",
                lines=3,
                placeholder="e.g. Post a $4,200 accrual for Q2 consulting fees to cost centre CC1001.",
            )
            propose_btn = gr.Button("Propose Action", variant="primary")

            gr.Markdown("### 2 · Review & Decide")
            decision_input = gr.Radio(
                choices=["approve", "edit", "reject"],
                label="Decision",
                value="approve",
            )
            edited_payload_input = gr.Code(
                label="Edited payload (JSON, used only when decision = edit)",
                language="json",
                lines=6,
            )
            rationale_input = gr.Textbox(
                label="Rationale",
                lines=2,
                placeholder="Why -- always logged, even on approve.",
            )
            resume_btn = gr.Button("Submit Decision", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### Proposed action (paused at human_review)")
            action_type_out = gr.Textbox(label="Action type", interactive=False)
            summary_out = gr.Textbox(label="Summary", interactive=False)
            payload_out = gr.JSON(label="Payload")
            risk_out = gr.HTML(label="Risk level")

            gr.Markdown("### Result (after resume)")
            executed_out = gr.HTML(label="Status")
            final_payload_out = gr.JSON(label="Final payload")
            decision_log_out = gr.Textbox(label="Audit log", lines=2, interactive=False)

    propose_btn.click(
        fn=run_propose,
        inputs=[event_input],
        outputs=[
            action_type_out,
            summary_out,
            payload_out,
            risk_out,
            edited_payload_input,
            thread_state,
            proposed_payload_state,
            executed_out,
            final_payload_out,
            decision_log_out,
        ],
    )

    resume_btn.click(
        fn=run_resume,
        inputs=[thread_state, decision_input, edited_payload_input, rationale_input],
        outputs=[executed_out, final_payload_out, decision_log_out],
    )

    gr.Markdown("---\n### Try an example")
    gr.Examples(
        examples=[[scenario] for scenario in SCENARIOS],
        inputs=[event_input],
        label="Pre-filled events",
    )

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set — copy .env.example to .env")
    demo.launch()
