"""Competitor response engine workflow.

Signal-to-action pipeline:
1. Gate agent classifies urgency (ignore / watch / respond).
2. Only on "respond": build a counter-campaign brief.
3. Only on "respond": fan out email, social, and blog generation in parallel.
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

from .prompts import BLOG_SYSTEM, BRIEF_SYSTEM, CLASSIFY_SYSTEM, EMAIL_SYSTEM, SOCIAL_SYSTEM
from .schema import (
    BlogOutline,
    ContentPack,
    CounterBrief,
    EmailCopy,
    ResponseEngineResult,
    SignalBatch,
    SignalClassification,
    SocialPost,
)

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
_MODEL = "gpt-4o-mini"


def _classify(batch: SignalBatch) -> SignalClassification:
    """Gate agent: classify urgency for the entire signal batch."""
    user_content = json.dumps(batch.model_dump())
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": CLASSIFY_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "SignalClassification",
                "strict": True,
                "schema": SignalClassification.model_json_schema(),
            },
        },
    )
    return SignalClassification.model_validate_json(resp.choices[0].message.content)


def _build_brief(brand_name: str, classification: SignalClassification) -> CounterBrief:
    """Build a counter-campaign brief from the gate classification."""
    user_content = json.dumps(
        {
            "brand_name": brand_name,
            "key_threat": classification.key_threat,
            "opportunity": classification.opportunity,
            "reasoning": classification.reasoning,
        }
    )
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": BRIEF_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "CounterBrief",
                "strict": True,
                "schema": CounterBrief.model_json_schema(),
            },
        },
    )
    return CounterBrief.model_validate_json(resp.choices[0].message.content)


def _write_email(brief: CounterBrief) -> EmailCopy:
    """Generate email copy from the counter-campaign brief."""
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": EMAIL_SYSTEM},
            {"role": "user", "content": json.dumps(brief.model_dump())},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "EmailCopy",
                "strict": True,
                "schema": EmailCopy.model_json_schema(),
            },
        },
    )
    return EmailCopy.model_validate_json(resp.choices[0].message.content)


def _write_social(brief: CounterBrief) -> list[SocialPost]:
    """Generate platform-native social posts from the counter-campaign brief."""
    social_schema = {
        "type": "object",
        "properties": {
            "posts": {
                "type": "array",
                "items": SocialPost.model_json_schema(),
            }
        },
        "required": ["posts"],
        "additionalProperties": False,
    }
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": SOCIAL_SYSTEM},
            {"role": "user", "content": json.dumps(brief.model_dump())},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "SocialPosts",
                "strict": True,
                "schema": social_schema,
            },
        },
    )
    data = json.loads(resp.choices[0].message.content)
    return [SocialPost.model_validate(p) for p in data["posts"]]


def _write_blog(brief: CounterBrief) -> BlogOutline:
    """Generate a blog outline from the counter-campaign brief."""
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": BLOG_SYSTEM},
            {"role": "user", "content": json.dumps(brief.model_dump())},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "BlogOutline",
                "strict": True,
                "schema": BlogOutline.model_json_schema(),
            },
        },
    )
    return BlogOutline.model_validate_json(resp.choices[0].message.content)


def run(batch: SignalBatch) -> ResponseEngineResult:
    """Run the full competitor response pipeline.

    Steps:
    1. Gate agent classifies signal urgency.
    2. If not "respond", return early with no brief or content.
    3. Build counter-campaign brief from the classification.
    4. Fan out email / social / blog generation in parallel.
    5. Return full ResponseEngineResult.
    """
    classification = _classify(batch)

    if classification.urgency != "respond":
        return ResponseEngineResult(
            brand_name=batch.brand_name,
            urgency=classification.urgency,
            classification=classification,
        )

    brief = _build_brief(batch.brand_name, classification)

    tasks = {
        "email": lambda: _write_email(brief),
        "social": lambda: _write_social(brief),
        "blog": lambda: _write_blog(brief),
    }

    results: dict = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fn): key for key, fn in tasks.items()}
        for future in as_completed(futures):
            results[futures[future]] = future.result()

    content_pack = ContentPack(
        topic=brief.topic,
        email=results["email"],
        social=results["social"],
        blog=results["blog"],
    )

    return ResponseEngineResult(
        brand_name=batch.brand_name,
        urgency=classification.urgency,
        classification=classification,
        counter_brief=brief,
        content_pack=content_pack,
    )
