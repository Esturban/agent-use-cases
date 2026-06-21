import json
import os

import gradio as gr
from openai import OpenAI


def add(x: int, y: int) -> int:
    return x + y


def multiply(x: int, y: int) -> int:
    return x * y


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two integers",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                },
                "required": ["x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Multiply two integers",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                },
                "required": ["x", "y"],
            },
        },
    },
]

TOOL_FNS = {"add": add, "multiply": multiply}


def run_agent(question: str, model: str) -> tuple[str, str]:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "**Error:** `OPENROUTER_API_KEY` environment variable is not set.", ""

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    messages = [
        {
            "role": "system",
            "content": "You are a math assistant. Solve problems using only the provided tools. Do not compute answers yourself.",
        },
        {"role": "user", "content": question},
    ]
    trace_lines = []

    for step in range(10):
        response = client.chat.completions.create(
            model=model, messages=messages, tools=TOOLS, tool_choice="auto"
        )
        msg = response.choices[0].message

        messages.append(
            {
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in (msg.tool_calls or [])
                ],
            }
        )

        if msg.tool_calls:
            for tc in msg.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                result = TOOL_FNS[fn_name](**fn_args)
                args_str = ", ".join(f"{k}={v}" for k, v in fn_args.items())
                trace_lines.append(
                    f"**Step {step + 1}:** `{fn_name}({args_str})` → `{result}`"
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": str(result),
                    }
                )
        else:
            return "\n\n".join(trace_lines) or "_No tools called_", msg.content or ""

    return "\n\n".join(trace_lines), "Max iterations reached."


MODELS = [
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]

SAMPLE_QUESTIONS = [
    ["What is (3 + 4) multiplied by 5?"],
    ["Add 15 and 27, then multiply the result by 3."],
    [
        "A team of 7 earns 450 per person per month. 3 of them receive a 120 bonus. What is the total monthly payroll?"
    ],
    ["What is (12 + 8) × (6 + 4)?"],
]

with gr.Blocks(title="Basic ReAct Agent") as demo:
    gr.Markdown("# Basic ReAct Agent")
    gr.Markdown(
        "The agent can only **add** and **multiply** — watch it chain tool calls to solve multi-step problems."
    )

    with gr.Row():
        with gr.Column(scale=2):
            question = gr.Textbox(label="Math question", lines=3)
            model = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Ask Agent", variant="primary")
            gr.Examples(examples=SAMPLE_QUESTIONS, inputs=question)

        with gr.Column(scale=3):
            trace = gr.Markdown(label="Tool call trace")
            answer = gr.Textbox(label="Final answer", lines=3)

    run_btn.click(fn=run_agent, inputs=[question, model], outputs=[trace, answer])

if __name__ == "__main__":
    demo.launch()
