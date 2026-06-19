import json
import os

from openai import OpenAI

from .news_client import fetch_articles
from .schema import SentimentDigest

_ANALYSIS_SYSTEM = (
    "You are a media analyst tracking brand sentiment. Given a list of news articles "
    "about a brand or company, produce a SentimentDigest:\n"
    "- Classify each article as positive, negative, or neutral with a score from -1.0 to +1.0\n"
    "- Summarise in one sentence why that sentiment was assigned\n"
    "- Count positive, negative, and neutral articles accurately\n"
    "- Set overall_sentiment to the dominant category\n"
    "- Set trend_direction based on whether recent articles skew better or worse than earlier ones\n"
    "- Flag up to 3 notable shifts or stories in notable_shifts\n"
    "- Write a 2-3 sentence week_summary naming the most significant stories\n"
    "Base everything only on the articles provided. Do not invent coverage."
)


def run(brand: str, days_back: int = 7) -> SentimentDigest:
    articles = fetch_articles(brand, days_back)
    if not articles:
        return SentimentDigest(
            brand=brand,
            articles_analysed=0,
            positive_count=0,
            negative_count=0,
            neutral_count=0,
            overall_sentiment="neutral",
            trend_direction="stable",
            average_score=0.0,
            notable_shifts=[],
            week_summary="No articles found for the specified brand and time range.",
            articles=[],
        )

    article_list = [
        {
            "headline": a.get("title", ""),
            "url": a.get("url", ""),
            "source": (a.get("source") or {}).get("name", "Unknown"),
            "published_at": a.get("publishedAt", ""),
            "description": a.get("description", ""),
        }
        for a in articles
    ]

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _ANALYSIS_SYSTEM},
            {
                "role": "user",
                "content": (
                    f"Brand: {brand}\n\n"
                    f"Articles:\n{json.dumps(article_list, indent=2)}"
                ),
            },
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": "SentimentDigest",
            "strict": True,
            "schema": SentimentDigest.model_json_schema(),
        }},
    )

    raw = response.choices[0].message.content
    return SentimentDigest.model_validate_json(raw)
