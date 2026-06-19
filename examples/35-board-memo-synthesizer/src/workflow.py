import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

from .schema import AnalystOpinion, BoardMemo

_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
_MODEL = "gpt-4o-mini"

_BULL_SYSTEM = (
    "You are a bull-case equity analyst. Read the analyst reports provided and produce an AnalystOpinion "
    "from the bull (upside) lens. Identify the strongest growth drivers, competitive advantages, and "
    "catalysts. Set lens to 'bull'. Be honest about confidence based on the evidence provided."
)

_BEAR_SYSTEM = (
    "You are a bear-case equity analyst. Read the analyst reports provided and produce an AnalystOpinion "
    "from the bear (downside) lens. Identify the most material risks, competitive threats, execution "
    "challenges, and valuation concerns. Set lens to 'bear'. Be honest about confidence based on evidence."
)

_RISK_SYSTEM = (
    "You are a risk officer. Read the analyst reports provided and produce an AnalystOpinion "
    "from the risk lens. Identify key strategic, operational, financial, and regulatory risks. "
    "Note any mitigations. Set lens to 'risk'. Be honest about confidence based on the evidence."
)

_SYNTHESIS_SYSTEM = (
    "You are a chief strategy officer preparing a board memo. You have received three analyst opinions "
    "(bull, bear, risk). Synthesise them into a BoardMemo:\n"
    "- Set recommended_position to 'proceed' if bull case dominates and risks are manageable, "
    "'pause' if significant risks or ambiguity exist, 'reject' if bear/risk cases dominate.\n"
    "- Write a 2-3 paragraph executive_summary that cites all three views fairly.\n"
    "- Write a crisp one_sentence_verdict.\n"
    "The memo must be suitable to present directly to a board of directors."
)


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


def _synthesise(
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
            {"role": "system", "content": _SYNTHESIS_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": "BoardMemo",
            "strict": True,
            "schema": BoardMemo.model_json_schema(),
        }},
    )
    return BoardMemo.model_validate_json(response.choices[0].message.content)


def run(topic: str, reports: list[str]) -> BoardMemo:
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_analyst, _BULL_SYSTEM, topic, reports): "bull",
            executor.submit(_analyst, _BEAR_SYSTEM, topic, reports): "bear",
            executor.submit(_analyst, _RISK_SYSTEM, topic, reports): "risk",
        }
        results = {}
        for future in as_completed(futures):
            key = futures[future]
            results[key] = future.result()

    return _synthesise(
        topic,
        bull=results["bull"],
        bear=results["bear"],
        risk=results["risk"],
    )
