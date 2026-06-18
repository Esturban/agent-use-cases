# 25 — OpenRouter ReAct Agent (from scratch)

**Harness focus:** Manual ReAct loop — reason → act → observe — using only the `openai` SDK + OpenRouter. No LangGraph, no LangChain. Shows what orchestration frameworks abstract away.

---

## Business problem

You want to understand what a ReAct agent actually does at the API level — or you want to build one without any orchestration dependency. This example strips the loop to its core: message history, tool dispatch dict, and a `while` loop.

---

## What it demonstrates

- The three-step ReAct pattern in raw form:
  1. **Reason** — call the model, get a response
  2. **Act** — if the response has tool calls, execute them
  3. **Observe** — append tool results to message history, repeat
- Tool definitions as plain JSON (OpenAI function-calling format)
- A `DISPATCH` dict as the tool registry — no decorators, no framework magic
- Loop termination: when the model returns no tool calls, the answer is final
- Full execution trace as a list of typed `AgentStep` records

---

## The loop (abridged)

```python
while True:
    response = client.chat.completions.create(model=model, messages=messages, tools=TOOLS)
    message = response.choices[0].message

    if not message.tool_calls:          # model is done
        return message.content, trace

    for call in message.tool_calls:     # execute and observe
        result = DISPATCH[call.function.name](**json.loads(call.function.arguments))
        messages.append({"role": "tool", "content": str(result), ...})
```

Compare with [1-basic-react-agent](../1-basic-react-agent/README.md) which uses `create_react_agent()` — same behaviour, the framework collapses these ~20 lines into one call.

---

## How to run

```bash
# Add OPENROUTER_API_KEY to your .env
python examples/25-openrouter-react-agent/main.py
```

---

## Files

```
25-openrouter-react-agent/
  src/schema.py      # AddArgs, MultiplyArgs, AgentStep trace model
  src/workflow.py    # Manual ReAct loop (~80 lines)
  main.py            # 3 math questions with step-by-step trace output
  README.md
```
