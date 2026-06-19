# 32 — Onboarding Orchestrator

Multi-agent onboarding coordinator that fans out IT, HR, and Facilities tasks in parallel.

## What it does

Given a new hire's name, role, department, start date, and location, fans out three specialist sub-agents simultaneously — IT provisioning, HR documentation, and Facilities setup — then synthesises their outputs into a single `OnboardingPlan` with a Day 1 readiness verdict and a list of blockers.

## Architecture

```
main.py
└── src/workflow.py             # run(new_hire) → OnboardingPlan via ThreadPoolExecutor
    ├── src/agents.py           # run_it / run_hr / run_facilities / synthesise
    ├── src/prompts.py          # IT_SYSTEM, HR_SYSTEM, FACILITIES_SYSTEM, SYNTHESIS_SYSTEM
    └── src/schema.py           # NewHire, SubAgentStatus, OnboardingPlan Pydantic models
```

## Setup

```bash
pip install openai pydantic python-dotenv
```

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_key
```

## Usage

```bash
python main.py
```

## Output

```json
{
  "new_hire": {"name": "Jane Smith", "role": "Senior Software Engineer", "start_date": "2026-07-14", "location": "New York"},
  "it_status": {"domain": "IT", "completed": ["Laptop order placed", "Email account created"], "pending": ["Device handover"], "notes": ""},
  "hr_status": {"domain": "HR", "completed": ["Contract sent"], "pending": ["Signed contract return"], "notes": ""},
  "facilities_status": {"domain": "Facilities", "completed": ["Desk assigned"], "pending": ["Access badge"], "notes": ""},
  "day1_ready": true,
  "blockers": [],
  "summary": "Jane's onboarding is on track with all critical tasks scheduled before Day 1."
}
```

## Workbook

Open `onboarding_orchestrator_workbook.ipynb` for an interactive walkthrough.
