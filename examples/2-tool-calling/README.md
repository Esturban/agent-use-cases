# 2-tool-calling

Shows how to bind tools directly to a model with `bind_tools()` and route tool calls
manually using conditional edges — the mechanics behind `create_react_agent`.

**Keys:** `OPENAI_API_KEY`

```bash
python examples/2-tool-calling/main.py
```

### Graph

```
START -> agent --(tool_calls?)-> tools -> agent -> END
                \--(no tools)-> END
```
