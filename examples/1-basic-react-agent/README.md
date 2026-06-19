# 1-basic-react-agent

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/1-basic-react-agent/basic_react_agent_workbook.ipynb)


A minimal ReAct agent with two math tools (`add`, `multiply`). The model reasons,
calls a tool, observes the result, and answers -- using only the tools, never its
own arithmetic.

**Keys:** `OPENAI_API_KEY`

```bash
python examples/1-basic-react-agent/main.py
```

## What you'll see

```
Q: What is (3 + 4) multiplied by 5?
------------------------------------------------------------
================================ Human Message =================================
What is (3 + 4) multiplied by 5?
================================== Ai Message ==================================
Tool Calls:
  add (call_a1b2c3)
  Args: x=3, y=4
================================= Tool Message =================================
Name: add
7
================================== Ai Message ==================================
Tool Calls:
  multiply (call_d4e5f6)
  Args: x=7, y=5
================================= Tool Message =================================
Name: multiply
35
================================== Ai Message ==================================
(3 + 4) multiplied by 5 is **35**.

Q: Add 15 and 27, then multiply the result by 3.
------------------------------------------------------------
================================ Human Message =================================
Add 15 and 27, then multiply the result by 3.
================================== Ai Message ==================================
Tool Calls:
  add (call_g7h8i9)
  Args: x=15, y=27
================================= Tool Message =================================
Name: add
42
================================== Ai Message ==================================
Tool Calls:
  multiply (call_j1k2l3)
  Args: x=42, y=3
================================= Tool Message =================================
Name: multiply
126
================================== Ai Message ==================================
15 + 27 = 42, and 42 × 3 = **126**.

Q: A team of 7 earns 450 per person per month. 3 of them receive a 120 bonus this month. What is the total monthly payroll?
------------------------------------------------------------
================================ Human Message =================================
A team of 7 earns 450 per person per month. 3 of them receive a 120 bonus this month. What is the total monthly payroll?
================================== Ai Message ==================================
Tool Calls:
  multiply (call_m4n5o6)
  Args: x=7, y=450
================================= Tool Message =================================
Name: multiply
3150
================================== Ai Message ==================================
Tool Calls:
  multiply (call_p7q8r9)
  Args: x=3, y=120
================================= Tool Message =================================
Name: multiply
360
================================== Ai Message ==================================
Tool Calls:
  add (call_s1t2u3)
  Args: x=3150, y=360
================================= Tool Message =================================
Name: add
3510
================================== Ai Message ==================================
The total monthly payroll is **3510** (7 × 450 base + 3 × 120 bonus).
```

### Graph

```
START -> agent  (reason -> call tool -> observe) -> END
              tools: add | multiply
```
