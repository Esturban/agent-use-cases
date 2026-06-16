# 1-basic-react-agent

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/1-basic-react-agent/basic_react_agent_workbook.ipynb)


A minimal ReAct agent with two math tools (`add`, `multiply`). The model reasons,
calls a tool, observes the result, and answers -- using only the tools, never its
own arithmetic.

**Keys:** `OPENAI_API_KEY`

```bash
python examples/1-basic-react-agent/main.py
```

### Graph

```
START -> agent  (reason -> call tool -> observe) -> END
              tools: add | multiply
```
