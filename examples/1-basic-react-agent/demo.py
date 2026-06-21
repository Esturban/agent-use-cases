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

MODELS = [
    "openai/gpt-5.4-nano",
    "minimax/minimax-m3",
    "openai/gpt-4.1-nano",
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]

SAMPLE_QUESTIONS = [
    ["What is (3 + 4) multiplied by 5?"],
    ["Add 15 and 27, then multiply the result by 3."],
    ["A team of 7 earns 450 per person per month. 3 of them receive a 120 bonus. What is the total monthly payroll?"],
    ["What is (12 + 8) × (6 + 4)?"],
    ["A warehouse has 3 sections. Section A holds 48 pallets, section B holds 36, section C holds 57. If each pallet weighs 25 kg, what is the total weight in kg?"],
]


def run_agent(question: str, model: str) -> tuple[str, str]:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "**Error:** `OPENROUTER_API_KEY` environment variable is not set.", ""

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a math assistant. Solve problems using only the provided tools. "
                "Do not compute answers yourself — every arithmetic step must go through a tool call."
            ),
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
                    f"**Step {step + 1}:** `{fn_name}({args_str})` → **`{result}`**"
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


with gr.Blocks(title="ReAct Agent") as demo:
    gr.Markdown(
        "## 🤖 ReAct Agent\n"
        "Ask a multi-step math question → watch the agent chain **add** and **multiply** "
        "tool calls to solve it step by step.\n\n"
        "**Built for:** understanding how AI agents actually work — "
        "this is the foundation of every agent you'll ever build."
    )

    with gr.Accordion("How a ReAct agent works", open=True):
        gr.Markdown(
            "**ReAct = Reason + Act.** The agent loops between two phases until it has an answer:\n\n"
            "1. **Reason** — the model reads the question and decides which tool to call next\n"
            "2. **Act** — the tool runs (in Python, on your machine) and the result goes back to the model\n"
            "3. Repeat until the model has enough context to give a final answer\n\n"
            "This agent has exactly **two tools** — `add(x, y)` and `multiply(x, y)`. "
            "It cannot compute anything itself; every arithmetic step must go through a tool call. "
            "That constraint makes every decision the model makes visible in the trace below.\n\n"
            "**Why this matters:** swap `add` and `multiply` for `search_web`, `query_database`, "
            "`send_email`, or `read_file` — and you have a real-world agent. The loop is identical."
        )

    with gr.Row():
        with gr.Column(scale=2):
            question = gr.Textbox(
                label="Math question",
                lines=3,
                placeholder="e.g. What is (3 + 4) multiplied by 5?",
            )
            model = gr.Dropdown(choices=MODELS, value=MODELS[0], label="Model")
            run_btn = gr.Button("Ask Agent", variant="primary")
            gr.Examples(
                examples=SAMPLE_QUESTIONS,
                inputs=question,
                label="Sample questions — click to load",
            )

        with gr.Column(scale=3):
            gr.Markdown("#### Tool call trace")
            trace = gr.Markdown(label="Tool call trace")
            answer = gr.Textbox(label="Final answer", lines=3, interactive=False)

    run_btn.click(fn=run_agent, inputs=[question, model], outputs=[trace, answer])

if __name__ == "__main__":
    demo.launch()
