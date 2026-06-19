import json
import os

from openai import OpenAI

from .fda_client import search_trials
from .schema import PatientCriteria, TrialSearchResult

_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
_MODEL = "gpt-4o-mini"

_ELIGIBILITY_SYSTEM = (
    "You are a clinical research coordinator. Given a patient's profile and a list of clinical trials, "
    "filter and rank the trials by eligibility fit. For each trial:\n"
    "- Write a plain-language 2-3 sentence eligibility_summary (not raw inclusion/exclusion text)\n"
    "- Set match_confidence: 'high' if the patient clearly meets all listed criteria, "
    "'medium' if likely matches but some criteria are ambiguous, "
    "'low' if significant criteria are unclear or only partially met\n"
    "- Write a one-sentence why_matches explaining the fit\n"
    "- Exclude trials where the patient clearly fails an exclusion criterion\n"
    "- Rank matches by confidence (high first)\n"
    "Only include trials that are plausible matches. Do not include implausible ones."
)


def run(criteria: PatientCriteria) -> TrialSearchResult:
    trials = search_trials(criteria.condition)
    if not trials:
        return TrialSearchResult(
            condition=criteria.condition,
            trials_found=0,
            matches=[],
        )

    payload = {
        "patient": criteria.model_dump(),
        "trials": trials,
    }

    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _ELIGIBILITY_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": "TrialSearchResult",
            "strict": True,
            "schema": TrialSearchResult.model_json_schema(),
        }},
    )
    return TrialSearchResult.model_validate_json(response.choices[0].message.content)
