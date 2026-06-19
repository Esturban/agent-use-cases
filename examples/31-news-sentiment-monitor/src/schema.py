from typing import Literal

from pydantic import BaseModel, Field


class ArticleSentiment(BaseModel):
    headline: str = Field(description="Article headline.")
    url: str = Field(description="Article URL.")
    source: str = Field(description="News source name.")
    published_at: str = Field(description="Publication timestamp (ISO-8601).")
    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="Sentiment classification for this article."
    )
    score: float = Field(
        description="Sentiment score: +1.0 (most positive) to -1.0 (most negative)."
    )
    summary: str = Field(description="One-sentence summary of why the sentiment was assigned.")


class SentimentDigest(BaseModel):
    brand: str = Field(description="Brand or company monitored.")
    articles_analysed: int = Field(description="Total number of articles processed.")
    positive_count: int = Field(description="Number of positive articles.")
    negative_count: int = Field(description="Number of negative articles.")
    neutral_count: int = Field(description="Number of neutral articles.")
    overall_sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="Aggregate sentiment across all articles."
    )
    trend_direction: Literal["improving", "worsening", "stable"] = Field(
        description="Week-over-week sentiment trend direction."
    )
    average_score: float = Field(
        description="Mean sentiment score across all articles."
    )
    notable_shifts: list[str] = Field(
        description="Up to 3 notable sentiment shifts or stories worth flagging."
    )
    week_summary: str = Field(
        description="2-3 sentence narrative digest of the week's coverage."
    )
    articles: list[ArticleSentiment] = Field(
        description="Per-article sentiment breakdown."
    )
