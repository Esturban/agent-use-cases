import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

from .schema import BlogOutline, CampaignBrief, ContentPack, EmailCopy, SocialPost

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
_MODEL = "gpt-4o-mini"

_EMAIL_SYSTEM = """You are an expert email marketing copywriter.

Given a campaign brief (topic, target audience, key message, tone, call to action), write compelling email marketing copy.

Rules:
- subject: punchy, under 60 characters, creates curiosity or urgency
- preview_text: extends the subject hook, under 90 characters
- body: 2-4 paragraphs; lead with the problem or aspiration, introduce the offer, build desire, close with the CTA
- cta_button_text: 2-5 words, action-oriented
- Match the specified tone exactly
- Return ONLY valid JSON matching the schema — no prose."""

_SOCIAL_SYSTEM = """You are an expert social media content strategist.

Given a campaign brief, create three social media posts — one each for Instagram, LinkedIn, and Twitter.

Rules:
- Instagram: visual-first language, emotive, 150-220 characters, 3-5 hashtags
- LinkedIn: professional, insight-led, 200-300 characters, 3-4 hashtags
- Twitter: concise, punchy, under 280 characters including hashtags, 2-3 hashtags
- Each caption must feel native to its platform — do not copy-paste
- Match the specified tone exactly
- Return ONLY valid JSON: an array of three SocialPost objects — no prose."""

_BLOG_SYSTEM = """You are an expert SEO content strategist.

Given a campaign brief, produce a blog post outline that will rank for the target topic.

Rules:
- title: include the primary keyword naturally, under 65 characters
- meta_description: summarise the post value proposition, under 155 characters, include the keyword
- sections: 5-8 section headings — start with an intro hook, include a problem/context section, 2-4 substantive sections, and a conclusion/CTA
- estimated_word_count: realistic total for the outlined sections (typically 800-1500)
- Return ONLY valid JSON matching the schema — no prose."""


def _brief_user_message(brief: CampaignBrief) -> str:
    return json.dumps(brief.model_dump())


def _write_email(brief: CampaignBrief) -> EmailCopy:
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _EMAIL_SYSTEM},
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
            {"role": "system", "content": _SOCIAL_SYSTEM},
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
            {"role": "system", "content": _BLOG_SYSTEM},
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
