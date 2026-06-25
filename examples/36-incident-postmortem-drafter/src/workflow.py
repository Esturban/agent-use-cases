import os

from openai import OpenAI

from .prompts import PARSE_SYSTEM, POSTMORTEM_SYSTEM
from .schema import IncidentTimeline, Postmortem

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
_MODEL = "gpt-4.1-nano"


def _parse_timeline(raw_log: str) -> IncidentTimeline:
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": PARSE_SYSTEM},
            {"role": "user", "content": raw_log},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "IncidentTimeline",
                "strict": True,
                "schema": IncidentTimeline.model_json_schema(),
            },
        },
    )
    return IncidentTimeline.model_validate_json(resp.choices[0].message.content)


def _draft_postmortem(timeline: IncidentTimeline) -> Postmortem:
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": POSTMORTEM_SYSTEM},
            {"role": "user", "content": timeline.model_dump_json()},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "Postmortem",
                "strict": True,
                "schema": Postmortem.model_json_schema(),
            },
        },
    )
    return Postmortem.model_validate_json(resp.choices[0].message.content)


def run(raw_log: str) -> Postmortem:
    timeline = _parse_timeline(raw_log)
    return _draft_postmortem(timeline)
