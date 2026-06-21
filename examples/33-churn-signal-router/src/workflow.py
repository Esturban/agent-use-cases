import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

from .prompts import ROUTER_SYSTEM
from .schema import ChurnBatch, NpsResponse, RoutedResponse

_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
_MODEL = "gpt-4.1-nano"


def _route_one(response: NpsResponse) -> RoutedResponse:
    result = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": ROUTER_SYSTEM},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "customer_id": response.customer_id,
                        "score": response.score,
                        "comment": response.comment,
                    }
                ),
            },
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": "RoutedResponse",
            "strict": True,
            "schema": RoutedResponse.model_json_schema(),
        }},
    )
    return RoutedResponse.model_validate_json(result.choices[0].message.content)


def run(responses: list[NpsResponse]) -> ChurnBatch:
    id_order = {r.customer_id: i for i, r in enumerate(responses)}
    routed: list[RoutedResponse] = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_route_one, r): r for r in responses}
        for future in as_completed(futures):
            routed.append(future.result())

    routed.sort(key=lambda r: id_order[r.customer_id])

    return ChurnBatch(
        total=len(routed),
        retain_count=sum(1 for r in routed if r.segment == "retain"),
        neutral_count=sum(1 for r in routed if r.segment == "neutral"),
        escalate_count=sum(1 for r in routed if r.segment == "escalate"),
        responses=routed,
    )
