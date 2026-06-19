import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

from .prompts import BLOG_SYSTEM, EMAIL_SYSTEM, SOCIAL_SYSTEM
from .schema import BlogOutline, CampaignBrief, ContentPack, EmailCopy, SocialPost

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
_MODEL = "gpt-4o-mini"


def _brief_user_message(brief: CampaignBrief) -> str:
    return json.dumps(brief.model_dump())


def _write_email(brief: CampaignBrief) -> EmailCopy:
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": EMAIL_SYSTEM},
            {"role": "user", "content": _brief_user_message(brief)},
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


def _write_social(brief: CampaignBrief) -> list[SocialPost]:
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
            {"role": "user", "content": _brief_user_message(brief)},
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


def _write_blog(brief: CampaignBrief) -> BlogOutline:
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": BLOG_SYSTEM},
            {"role": "user", "content": _brief_user_message(brief)},
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


def run(brief: CampaignBrief) -> ContentPack:
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

    return ContentPack(
        topic=brief.topic,
        email=results["email"],
        social=results["social"],
        blog=results["blog"],
    )
