import json
import os

from openai import OpenAI

from .prompts import BEAR_SYSTEM, BULL_SYSTEM, RISK_SYSTEM, SYNTHESIS_SYSTEM
from .schema import AnalystOpinion, BoardMemo

_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
_MODEL = "gpt-4o-mini"


def _analyst(system: str, topic: str, reports: list[str]) -> AnalystOpinion:
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps({"topic": topic, "reports": reports}),
            },
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": "AnalystOpinion",
            "strict": True,
            "schema": AnalystOpinion.model_json_schema(),
        }},
    )
    return AnalystOpinion.model_validate_json(response.choices[0].message.content)


def run_bull(topic: str, reports: list[str]) -> AnalystOpinion:
    return _analyst(BULL_SYSTEM, topic, reports)


def run_bear(topic: str, reports: list[str]) -> AnalystOpinion:
    return _analyst(BEAR_SYSTEM, topic, reports)


def run_risk(topic: str, reports: list[str]) -> AnalystOpinion:
    return _analyst(RISK_SYSTEM, topic, reports)


def synthesise(
    topic: str,
    bull: AnalystOpinion,
    bear: AnalystOpinion,
    risk: AnalystOpinion,
) -> BoardMemo:
    payload = {
        "topic": topic,
        "bull": bull.model_dump(),
        "bear": bear.model_dump(),
        "risk": risk.model_dump(),
    }
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": SYNTHESIS_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": "BoardMemo",
            "strict": True,
            "schema": BoardMemo.model_json_schema(),
        }},
    )
    return BoardMemo.model_validate_json(response.choices[0].message.content)
