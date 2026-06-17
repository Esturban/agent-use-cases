# 12-board-pack-reviewer

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/12-board-pack-reviewer/board_pack_workbook.ipynb)

An agent that reads a board pack and produces a structured director briefing --
risks ranked by severity, information gaps named explicitly, decisions identified
with the key question a NED must ask, and probing questions for management.

## Harness focus

**Executive critique + structured risk prioritization**

The agent is prompted to think like a non-executive director: sceptical of management
framing, attentive to what the pack *doesn't* say, and focused on what the board
needs to govern effectively rather than what management wants noted.

Output is a `DirectorBriefing` -- not a summary of what the pack contains, but an
independent assessment of what matters and what's missing.

```
Board pack (long-form)
        |
        v
  [NED Reviewer]
        |
        v
DirectorBriefing
  |-- overall_pack_quality       (strong | adequate | weak)
  |-- executive_assessment       (3-4 sentences for a NED)
  |-- top_risks                  (ranked, severity x area, source cited)
  |     |-- suggested_question   (per risk)
  |-- information_gaps           (what the pack fails to disclose)
  |-- decisions_required         (what the board is being asked to approve)
  |-- questions_for_management   (probing, not procedural)
```

**Keys:** `OPENAI_API_KEY`

```bash
python examples/12-board-pack-reviewer/main.py
```

## Key concepts

| Concept | Where |
|---------|-------|
| NED framing in system prompt | `src/workflow.py` -- `REVIEWER_SYSTEM` |
| Risk ranking with source citation | `src/schema.py` -- `TopRisk.source_section` |
| Information gap as explicit output field | `src/schema.py` -- `InformationGap` |
| Decision identification with key consideration | `src/schema.py` -- `DecisionRequired` |
| Synthetic board pack with realistic governance issues | `main.py` -- Nexus Retail Group PLC |
