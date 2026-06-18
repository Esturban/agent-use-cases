# 4-lead-qualifier

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/4-lead-qualifier/lead_qualifier_workbook.ipynb)


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

### What you'll see

```
Company:  Meridian Payments
Score:    8/10  →  HOT
Action:   Schedule a demo this week — strong ICP fit, active buying signal, Q3 deadline creates urgency

Criteria met:    B2B SaaS buyer, $2k–4k/month budget matches pricing tier, 100–500 employees, ops pain with clear ROI, decision-maker engaged
Criteria missed: No existing contract to displace

Reasoning: Meridian Payments clears five of six ICP criteria. The manual reconciliation
problem (15 hrs/week) is a quantified pain point, budget is in range, and Sarah Chen
(VP of Operations) is both the economic buyer and the daily user. The only gap is the
absence of a legacy contract to displace, which lowers displacement risk rather than fit.
Recommend fast-track to demo before Q3 planning locks.
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
