"""
Manual ReAct loop -- reason → act → observe -- using only the openai SDK.

No LangGraph, no LangChain. The loop is explicit:
  1. Call the model with the current message history and tool definitions.
  2. If the response contains tool calls, execute them and append results.
  3. Repeat until the model returns a plain text answer (no tool calls).

This is exactly what LangGraph's create_react_agent() does internally.
"""
import json
import os

from openai import OpenAI

from .prompts import SYSTEM_PROMPT
from .schema import AgentStep
from .tools import DISPATCH, TOOLS


def run(question: str, model: str = "openai/gpt-4.1-nano") -> tuple[str, list[AgentStep]]:
    """
    Run a ReAct loop for a math question.

    Args:
        question: Natural-language math question (e.g. "What is (3 + 4) * 5?").
        model: OpenRouter model identifier string.

    Returns:
        Tuple of (final_answer, trace) where trace is a list of AgentStep records.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    trace: list[AgentStep] = []
    step = 0

    while True:
        step += 1
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        message = response.choices[0].message

        if not message.tool_calls:
            final = message.content or ""
            trace.append(AgentStep(step=step, action="final", input=final, observation=""))
            return final, trace

        messages.append(message.model_dump(exclude_unset=True))

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            result = DISPATCH[name](**args)
            observation = str(result)

            trace.append(
                AgentStep(
                    step=step,
                    action=name,
                    input=call.function.arguments,
                    observation=observation,
                )
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": observation,
                }
            )
