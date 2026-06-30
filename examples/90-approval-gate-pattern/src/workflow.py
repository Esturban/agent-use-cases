"""LangGraph workflow for the human-in-the-loop approval-gate pattern.

Graph: draft_action -> human_review -> execute_or_log.

human_review calls interrupt() and genuinely halts the graph -- via the
checkpointer, execution pauses until a caller resumes it with
Command(resume=<ApprovalDecision dict>). This is the harness lesson: "route to
an approval tier" is a label on an output field, not an execution gate. A real
gate means the tool-call boundary is unreachable until a human decision comes
back in.

Public API is two functions, not one run(), to make the pause explicit:
  propose() runs the graph up to the interrupt and returns the draft + a
  thread_id. resume() takes that thread_id plus a human ApprovalDecision and
  finishes the graph. In a real deployment these would be two separate
  processes (a UI/queue sits between them); here they are two function calls
  in main.py so the pattern is visible end to end.
"""
from __future__ import annotations

import uuid
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .prompts import DRAFT_ACTION_SYSTEM
from .schema import ActionResult, ApprovalDecision, ProposedAction

_MODEL = "gpt-4.1-nano"


class GraphState(TypedDict):
    event_description: str
    proposed_action: dict
    decision: dict
    result: dict


def _draft_action(state: GraphState) -> dict:
    """Ask the LLM to draft a ProposedAction from the free-text event.

    Uses method="function_calling" rather than the strict json_schema default:
    ProposedAction.payload is an open dict (its shape depends on action_type),
    and OpenAI's strict structured-output mode requires every object schema to
    set additionalProperties=false, which an intentionally-open dict can't.
    """
    llm = ChatOpenAI(model=_MODEL, temperature=0)
    proposed: ProposedAction = llm.with_structured_output(
        ProposedAction, method="function_calling"
    ).invoke([DRAFT_ACTION_SYSTEM, ("human", state["event_description"])])
    return {"proposed_action": proposed.model_dump()}


def _human_review(state: GraphState) -> dict:
    """Halt the graph and surface the proposed action for human review."""
    decision = interrupt({"proposed_action": state["proposed_action"]})
    return {"decision": decision}


def _execute_or_log(state: GraphState) -> dict:
    """Resolve the decision into an ActionResult. Only 'approve' or 'edit' execute."""
    proposed = state["proposed_action"]
    decision = ApprovalDecision.model_validate(state["decision"])

    if decision.decision == "reject":
        result = ActionResult(
            executed=False,
            final_payload=None,
            decision_log=(
                f"REJECTED: {proposed['summary']!r}. "
                f"Reason: {decision.rationale}"
            ),
        )
    else:
        final_payload = (
            decision.edited_payload
            if decision.decision == "edit" and decision.edited_payload is not None
            else proposed["payload"]
        )
        verb = "EDITED-THEN-EXECUTED" if decision.decision == "edit" else "EXECUTED"
        result = ActionResult(
            executed=True,
            final_payload=final_payload,
            decision_log=(
                f"{verb}: {proposed['summary']!r}. "
                f"Reason: {decision.rationale}"
            ),
        )
    return {"result": result.model_dump()}


def _build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("draft_action", _draft_action)
    graph.add_node("human_review", _human_review)
    graph.add_node("execute_or_log", _execute_or_log)
    graph.add_edge(START, "draft_action")
    graph.add_edge("draft_action", "human_review")
    graph.add_edge("human_review", "execute_or_log")
    graph.add_edge("execute_or_log", END)
    return graph.compile(checkpointer=InMemorySaver())


_APP = _build_graph()


def propose(event_description: str) -> tuple[ProposedAction, str]:
    """Run the graph up to the human-review interrupt.

    Returns the drafted ProposedAction and a thread_id. The thread_id is what
    a real system would hand to whatever queues the review (a UI, a Slack
    message, a ticket) so the matching resume() call can find this paused run.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    result = _APP.invoke({"event_description": event_description}, config=config)
    proposed = ProposedAction.model_validate(result["__interrupt__"][0].value["proposed_action"])
    return proposed, thread_id


def resume(thread_id: str, decision: ApprovalDecision) -> ActionResult:
    """Resume a paused run with a human's ApprovalDecision and return the result."""
    config = {"configurable": {"thread_id": thread_id}}
    result = _APP.invoke(Command(resume=decision.model_dump()), config=config)
    return ActionResult.model_validate(result["result"])
