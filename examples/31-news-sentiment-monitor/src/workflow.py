import json
import os

from openai import OpenAI

from .news_client import fetch_articles
from .prompts import ANALYSIS_SYSTEM
from .schema import SentimentDigest


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
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": ANALYSIS_SYSTEM},
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
