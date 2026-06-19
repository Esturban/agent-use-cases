# 6 — Resume Screener

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/6-resume-screener/resume_screener_workbook.ipynb)

Hiring teams waste hours reading resumes that don't fit the role. This agent scores every candidate against a job spec and ranks them instantly, so recruiters can focus their time on the people most worth calling.

---

## What it does

A batch of resumes goes in alongside a job specification. The agent reads each resume and returns a structured score: a numeric fit rating, a hiring tier, which required skills were found or missing, a standout signal, and a specific concern. After all candidates are scored, the results are sorted by score so the strongest fits appear first.

---

## How it works

The same scoring schema is applied to every resume, which makes the outputs directly comparable in plain Python — no text parsing needed after the fact. A job spec and scoring rubric are embedded in the prompt, so the model evaluates each candidate against identical criteria. The final ranking is a simple sort on the numeric score field. Gap reporting is explicit: the agent is required to name missing skills and surface the biggest concern for each candidate, not just highlight positives.

---

## What you'll see

```
RESUME SCREENING RESULTS
============================================================

Alex Kim
  Score:    9/10  |  Tier: strong_yes
  Action:   schedule_interview
  Matched:  Python, FastAPI, PostgreSQL, AWS, Docker, Pydantic, Git
  Missing:  None
  Standout: 7 years of production Python at fintech scale with $2M/day transaction volume.
  Concern:  No obvious gaps; verify team leadership depth in interview.

Jordan Lee
  Score:    5/10  |  Tier: maybe
  Action:   hold_for_review
  Matched:  Python, SQL, Flask
  Missing:  FastAPI, AWS, Docker, Pydantic
  Standout: Strong ML background with real e-commerce production impact.
  Concern:  Flask work was internal only; no cloud deployment or production API experience.

Sam Nguyen
  Score:    4/10  |  Tier: no
  Action:   pass
  Matched:  Python, Django, PostgreSQL, Git
  Missing:  FastAPI, AWS, Docker, CI/CD, team leadership
  Standout: Hands-on PostgreSQL and REST API work despite junior tenure.
  Concern:  2 years experience and still learning Docker and CI/CD — too early for this role.

============================================================
RANKING
  1. Alex Kim          9/10  strong_yes
  2. Jordan Lee        5/10  maybe
  3. Sam Nguyen        4/10  no
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/6-resume-screener/main.py
```

---

## Files

```
6-resume-screener/
  src/schema.py      # ResumeScore model: score, tier, matched/missing skills, standout, concern, action
  src/workflow.py    # Sends each resume to the model with the job spec and scoring rubric
  main.py            # Runs three sample candidates and prints ranked results
  README.md
```
