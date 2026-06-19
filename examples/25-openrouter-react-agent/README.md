# 25 — OpenRouter ReAct Agent

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/25-openrouter-react-agent/openrouter_react_agent_workbook.ipynb)

A minimal, dependency-free agent loop for developers who want to see exactly how tool-calling works at the API level — or who need to build one without pulling in an orchestration library.

---

## What it does

A question goes in, such as a multi-step arithmetic problem. The agent decides which calculation tool to call, runs it, reads the result, and keeps going until it has a final answer. Every intermediate step — the tool name, the arguments, and the result — is recorded and printed so you can see the full chain of reasoning before the final answer appears.

---

## How it works

The agent sends the question to the model along with two tool definitions: add and multiply. If the model wants to use a tool, the agent runs it locally and sends the result back as a new message. This repeats until the model responds with a plain answer and no further tool calls. A dispatch dictionary maps tool names to Python functions, so adding a new tool means adding one entry to that dict and one JSON definition — nothing else.

---

## What you'll see

```
Q: What is (3 + 4) * 5?
  [step 1] add({"a": 3, "b": 4}) = 7.0
  [step 2] multiply({"a": 7.0, "b": 5}) = 35.0
  [step 3] ANSWER → (3 + 4) * 5 = 35
Final: (3 + 4) * 5 = 35

Q: What is 100 + (6 * 7)?
  [step 1] multiply({"a": 6, "b": 7}) = 42.0
  [step 2] add({"a": 100, "b": 42.0}) = 142.0
  [step 3] ANSWER → 100 + (6 * 7) = 142
Final: 100 + (6 * 7) = 142

Q: If I have 12 items and each costs $8.50, what is the total cost?
  [step 1] multiply({"a": 12, "b": 8.5}) = 102.0
  [step 2] ANSWER → The total cost is $102.00
Final: The total cost is $102.00
```

---

## How to run

```bash
# Requires OPENROUTER_API_KEY in .env
python examples/25-openrouter-react-agent/main.py
```

---

## Files

```
25-openrouter-react-agent/
  src/schema.py      # AddArgs, MultiplyArgs, and AgentStep trace models
  src/workflow.py    # The tool-calling loop: reason, act, observe, repeat
  main.py            # Three math questions with step-by-step trace output
  README.md
```
