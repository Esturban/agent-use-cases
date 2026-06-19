"""
Self-healing CI agent — real OpenAI tool-calling loop.

Loop structure (up to max_iterations turns):
  Each turn the LLM may call one or more tools.
  The agent observes each tool result and decides its next action.
  The loop exits when:
    (a) run_tests returns passed=true  -> healed
    (b) the LLM stops calling tools    -> unhealed, write postmortem
    (c) max_iterations is reached      -> unhealed, write postmortem

All LLM tool calls use the OpenAI function-calling API (tools= parameter).
The postmortem is generated via structured JSON output.
"""
from __future__ import annotations

import json
import os

from openai import OpenAI

from .prompts import HEAL_SYSTEM, POSTMORTEM_SYSTEM
from .schema import CIFailure, HealingResult, RepairAttempt, RepairPostmortem
from .tools import TOOL_DEFINITIONS, TOOL_MAP, reset_state

_MODEL = "gpt-4o-mini"


def _get_client() -> OpenAI:
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def _write_postmortem(
    failure: CIFailure,
    attempts: list[RepairAttempt],
) -> RepairPostmortem:
    """Generate a structured postmortem after all iterations are exhausted."""
    client = _get_client()
    user_content = json.dumps(
        {
            "job_name": failure.job_name,
            "error_log": failure.error_log,
            "tool_calls_made": [a.model_dump() for a in attempts],
        },
        indent=2,
    )
    resp = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": POSTMORTEM_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "RepairPostmortem",
                "strict": True,
                "schema": RepairPostmortem.model_json_schema(),
            },
        },
    )
    return RepairPostmortem.model_validate_json(resp.choices[0].message.content)


def run(failure: CIFailure, max_iterations: int = 8) -> HealingResult:
    """
    Run the real tool-calling self-healing loop for a CI failure.

    The LLM receives the error log and a set of tools. It calls tools
    iteratively, observing each result, until it either heals the failure
    (run_tests returns passed=true) or exhausts max_iterations.

    Args:
        failure:        The CI failure to heal.
        max_iterations: Maximum loop turns before giving up (default 8).

    Returns:
        HealingResult with healed=True when tests pass, or
        healed=False with a populated postmortem on terminal failure.
    """
    reset_state()
    client = _get_client()

    messages: list[dict] = [
        {"role": "system", "content": HEAL_SYSTEM},
        {
            "role": "user",
            "content": (
                f"CI job: {failure.job_name}\n\n"
                f"Failure log:\n\n{failure.error_log}\n\n"
                "Fix it using the available tools."
            ),
        },
    ]

    attempts: list[RepairAttempt] = []

    for i in range(max_iterations):
        resp = client.chat.completions.create(
            model=_MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message

        # Build assistant message dict — include tool_calls when present
        assistant_msg: dict = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
        messages.append(assistant_msg)

        # If the LLM stopped calling tools, the repair loop is done
        if not msg.tool_calls:
            break

        # Dispatch each tool call and append results to the message thread
        for tc in msg.tool_calls:
            fn = TOOL_MAP.get(tc.function.name)
            if fn is None:
                result = {"error": f"Unknown tool: {tc.function.name}"}
            else:
                args = json.loads(tc.function.arguments)
                result = fn(**args)  # type: ignore[operator]

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                }
            )

            attempt = RepairAttempt(
                iteration=i + 1,
                tool_called=tc.function.name,
                arguments=json.loads(tc.function.arguments),
                result=result,
            )
            attempts.append(attempt)

            # Tests passed — failure is healed
            if tc.function.name == "run_tests" and result.get("passed"):
                return HealingResult(
                    healed=True,
                    iterations_used=i + 1,
                    attempts=attempts,
                    postmortem=None,
                )

    # Exhausted iterations or LLM stopped — write postmortem
    postmortem = _write_postmortem(failure, attempts)
    return HealingResult(
        healed=False,
        iterations_used=len(attempts),
        attempts=attempts,
        postmortem=postmortem,
    )
