# 34 — Clinical Trial Finder

Patient eligibility-filtered clinical trial search via ClinicalTrials.gov API with plain-language match summaries.

## What it does

Takes a patient's condition, age, location, and any exclusion criteria, queries the public ClinicalTrials.gov API (no key required), then uses GPT-4o-mini to filter and rank matching trials by eligibility confidence. Returns a structured result with plain-language eligibility summaries and match reasoning per trial.

## Architecture

```
main.py
└── src/workflow.py          # run(criteria) → TrialSearchResult
    ├── src/fda_client.py    # search_trials() via ClinicalTrials.gov /api/v2/studies
    ├── src/prompts.py       # ELIGIBILITY_SYSTEM prompt constant
    └── src/schema.py        # PatientCriteria, TrialMatch, TrialSearchResult Pydantic models
```

## Setup

```bash
pip install openai pydantic requests python-dotenv
```

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_key
```

No ClinicalTrials.gov API key required — public endpoint.

## Usage

```bash
python main.py
```

## Output

```json
{
  "condition": "type 2 diabetes",
  "trials_found": 10,
  "matches": [
    {
      "nct_id": "NCT01234567",
      "title": "A Study of Drug X in Adults with Type 2 Diabetes",
      "phase": "PHASE2",
      "status": "RECRUITING",
      "eligibility_summary": "Adults aged 18-70 with type 2 diabetes not on insulin...",
      "match_confidence": "high",
      "why_matches": "Patient age and condition match all listed inclusion criteria."
    }
  ]
}
```

## Workbook

Open `clinical_trial_finder_workbook.ipynb` for an interactive walkthrough.
