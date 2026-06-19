import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

from .schema import NewHire, OnboardingPlan, SubAgentStatus

_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
_MODEL = "gpt-4o-mini"

_IT_SYSTEM = (
    "You are an IT provisioning specialist. Given a new hire's details, produce a SubAgentStatus "
    "for the IT domain. Include all hardware, software, access, and account setup tasks. "
    "Identify which tasks can be completed before Day 1 (completed) and which require the "
    "employee to be present (pending). Flag any blockers in notes."
)

_HR_SYSTEM = (
    "You are an HR onboarding specialist. Given a new hire's details, produce a SubAgentStatus "
    "for the HR domain. Include contract signing, payroll setup, benefits enrollment, policy "
    "acknowledgements, and compliance training. Identify tasks completable before Day 1 and "
    "those requiring the employee (pending). Flag any blockers in notes."
)

_FACILITIES_SYSTEM = (
    "You are a Facilities coordinator. Given a new hire's details, produce a SubAgentStatus "
    "for the Facilities domain. Include desk assignment, access badge, parking, building tour, "
    "and equipment delivery. Identify tasks completable before Day 1 and those requiring "
    "the employee to be present (pending). Flag any blockers in notes."
)

_SYNTHESIS_SYSTEM = (
    "You are an onboarding programme manager. Given the new hire's details and the IT, HR, "
    "and Facilities sub-agent reports, produce a complete OnboardingPlan. "
    "Set day1_ready to true only if there are no blocking tasks across all three domains. "
    "List all blockers. Write a 2-3 sentence summary of overall readiness."
)


def _run_sub_agent(system: str, new_hire: NewHire) -> SubAgentStatus:
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


def _synthesise(
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
            {"role": "system", "content": _SYNTHESIS_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": "OnboardingPlan",
            "strict": True,
            "schema": OnboardingPlan.model_json_schema(),
        }},
    )
    return OnboardingPlan.model_validate_json(response.choices[0].message.content)


def run(new_hire: NewHire) -> OnboardingPlan:
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_run_sub_agent, _IT_SYSTEM, new_hire): "it",
            executor.submit(_run_sub_agent, _HR_SYSTEM, new_hire): "hr",
            executor.submit(_run_sub_agent, _FACILITIES_SYSTEM, new_hire): "facilities",
        }
        results = {}
        for future in as_completed(futures):
            results[futures[future]] = future.result()

    return _synthesise(
        new_hire,
        it=results["it"],
        hr=results["hr"],
        facilities=results["facilities"],
    )
