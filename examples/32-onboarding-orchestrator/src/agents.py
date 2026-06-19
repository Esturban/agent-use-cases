import json
import os

from openai import OpenAI

from .prompts import FACILITIES_SYSTEM, HR_SYSTEM, IT_SYSTEM, SYNTHESIS_SYSTEM
from .schema import NewHire, OnboardingPlan, SubAgentStatus

_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
_MODEL = "gpt-4o-mini"


def run_sub_agent(system: str, new_hire: NewHire) -> SubAgentStatus:
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(new_hire.model_dump())},
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": "SubAgentStatus",
            "strict": True,
            "schema": SubAgentStatus.model_json_schema(),
        }},
    )
    return SubAgentStatus.model_validate_json(response.choices[0].message.content)


def synthesise(
    new_hire: NewHire,
    it: SubAgentStatus,
    hr: SubAgentStatus,
    facilities: SubAgentStatus,
) -> OnboardingPlan:
    payload = {
        "new_hire": new_hire.model_dump(),
        "it": it.model_dump(),
        "hr": hr.model_dump(),
        "facilities": facilities.model_dump(),
    }
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": SYNTHESIS_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": "OnboardingPlan",
            "strict": True,
            "schema": OnboardingPlan.model_json_schema(),
        }},
    )
    return OnboardingPlan.model_validate_json(response.choices[0].message.content)


def run_it(new_hire: NewHire) -> SubAgentStatus:
    return run_sub_agent(IT_SYSTEM, new_hire)


def run_hr(new_hire: NewHire) -> SubAgentStatus:
    return run_sub_agent(HR_SYSTEM, new_hire)


def run_facilities(new_hire: NewHire) -> SubAgentStatus:
    return run_sub_agent(FACILITIES_SYSTEM, new_hire)
