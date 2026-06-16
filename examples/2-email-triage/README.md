# 2-email-triage

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/2-email-triage/email_triage_workbook.ipynb)


An agent that reads a raw email and returns a **typed classification** --
urgency, category, a one-line summary, and a recommended action.

**What this teaches:** `with_structured_output()` forces the model to return
a Pydantic schema instead of free text. `urgency` is always `"high" | "medium" | "low"` --
never `"very urgent"` or `"kinda important"`. The schema is the contract.

**Keys:** `OPENAI_API_KEY`

```bash
python examples/2-email-triage/main.py
```

### How it works

```
email text  →  LLM + EmailTriage schema  →  typed result
```

The model never sees free-form output -- the schema constrains every field.
