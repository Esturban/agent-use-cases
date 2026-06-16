# 4-lead-qualifier

An agent that scores a sales lead against an Ideal Customer Profile (ICP)
and returns a typed result -- score, tier, and the exact criteria met or missed.

**What this teaches:** The ICP rubric lives in the system prompt, not in code.
The model must cite which criteria it used (`criteria_met`, `criteria_missed`),
so the score is always explainable -- never a black-box number.
This is the grounded reasoning pattern: constrain *what* the model scores against,
then force it to show its work.

**Keys:** `OPENAI_API_KEY`

```bash
python examples/4-lead-qualifier/main.py
```

### How it works

```
ICP rubric (system prompt)
        +
lead description (human message)
        ↓
  LLM + LeadScore schema
        ↓
  score  tier  criteria_met  criteria_missed  reasoning
```

### Schema

```
LeadScore
  company          str
  score            int   (1–10, validated)
  tier             "hot" | "warm" | "cold"
  criteria_met     List[str]   ← exact ICP criteria this lead satisfies
  criteria_missed  List[str]   ← exact ICP criteria this lead doesn't satisfy
  recommended_action  str
  reasoning           str      ← must cite criteria
```
