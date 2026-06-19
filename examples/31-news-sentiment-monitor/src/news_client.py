import os
from datetime import datetime, timedelta, timezone

import requests


def fetch_articles(brand: str, days_back: int = 7) -> list[dict]:
    api_key = os.environ["NEWSAPI_KEY"]
    from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime(
        "%Y-%m-%d"
    )
    resp = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": brand,
            "from": from_date,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 20,
            "apiKey": api_key,
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("articles", [])
