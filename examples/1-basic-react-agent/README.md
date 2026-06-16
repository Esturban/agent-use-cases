# 1-basic-react-agent

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
