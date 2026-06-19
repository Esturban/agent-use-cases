# 31 — News Sentiment Monitor

Brand and competitor news sentiment tracking via NewsAPI with week-over-week trend detection.

## What it does

Fetches the last N days of news articles for a brand from NewsAPI, then uses GPT-4o-mini with structured output to classify each article's sentiment and produce a `SentimentDigest` — counts, average score, trend direction, notable shifts, and a narrative week summary.

## Architecture

```
main.py
└── src/workflow.py          # run(brand, days_back) → SentimentDigest
    ├── src/news_client.py   # fetch_articles() via NewsAPI /v2/everything
    ├── src/prompts.py       # ANALYSIS_SYSTEM prompt constant
    └── src/schema.py        # ArticleSentiment + SentimentDigest Pydantic models
```

## Setup

```bash
pip install openai pydantic requests python-dotenv
```

Create a `.env` file:

```
NEWSAPI_KEY=your_newsapi_key
OPENAI_API_KEY=your_openai_key
```

Get a free NewsAPI key at [newsapi.org](https://newsapi.org).

## Usage

```bash
python main.py "Apple"
python main.py "Tesla" --days 14
```

## Output

```json
{
  "brand": "Apple",
  "articles_analysed": 18,
  "positive_count": 10,
  "negative_count": 4,
  "neutral_count": 4,
  "overall_sentiment": "positive",
  "trend_direction": "stable",
  "average_score": 0.32,
  "notable_shifts": ["Vision Pro supply concerns", "Strong Q2 earnings beat"],
  "week_summary": "Apple had a broadly positive week...",
  "articles": [...]
}
```

## Workbook

Open `news_sentiment_monitor_workbook.ipynb` for an interactive walkthrough.
