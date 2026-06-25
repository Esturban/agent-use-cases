import json
import os

from openai import OpenAI

from .fda_client import search_trials
from .prompts import ELIGIBILITY_SYSTEM
from .schema import PatientCriteria, TrialSearchResult

_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
_MODEL = "gpt-4.1-nano"


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
            {"role": "system", "content": ELIGIBILITY_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": "TrialSearchResult",
            "strict": True,
            "schema": TrialSearchResult.model_json_schema(),
        }},
    )
    return TrialSearchResult.model_validate_json(response.choices[0].message.content)
