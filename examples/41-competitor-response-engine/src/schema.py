"""Pydantic models for the competitor response engine."""

from typing import Literal

from pydantic import BaseModel, Field


class CompetitorSignal(BaseModel):
    source: Literal["news", "social", "press_release", "product_launch", "pricing"] = Field(
        description="Channel where the signal was detected."
    )
    headline: str = Field(description="Short headline or title of the signal.")
    summary: str = Field(description="2-4 sentence summary of what was detected.")
    competitor_name: str = Field(description="Name of the competitor who generated the signal.")
    brand_name: str = Field(description="Name of our brand being affected by this signal.")


class SignalBatch(BaseModel):
    brand_name: str = Field(description="Our brand name — used as context across all signals.")
    signals: list[CompetitorSignal] = Field(
        description="One or more competitor signals to evaluate together."
    )


ResponseUrgency = Literal["ignore", "watch", "respond"]


class SignalClassification(BaseModel):
    urgency: ResponseUrgency = Field(
        description=(
            "Urgency level: 'respond' for strong competitive threats or viral moments, "
            "'watch' for emerging patterns, 'ignore' for noise."
        )
    )
    reasoning: str = Field(
        description="Explanation of the urgency decision citing the strongest signal."
    )
    key_threat: str | None = Field(
        default=None,
        description="The primary competitive threat identified; populated when urgency is 'respond'.",
    )
    opportunity: str | None = Field(
        default=None,
        description="Counter-positioning opportunity for our brand; populated when urgency is 'respond'.",
    )


class CounterBrief(BaseModel):
    topic: str = Field(description="Campaign topic that directly addresses the competitive signal.")
    target_audience: str = Field(
        description="Audience segment most affected by the competitor move."
    )
    key_message: str = Field(
        description="Primary message that counter-positions our brand against the identified threat."
    )
    tone: str = Field(description="Desired tone for all content derived from this brief.")
    call_to_action: str = Field(
        description="The desired action the audience should take in response to this campaign."
    )
    counter_narrative: str = Field(
        description="The 1-2 sentence narrative that reframes the competitive threat in our favour."
    )


class EmailCopy(BaseModel):
    subject: str = Field(description="Email subject line (under 60 characters).")
    preview_text: str = Field(description="Email preview text (under 90 characters).")
    body: str = Field(description="Full email body in plain text (2-4 paragraphs).")
    cta_button_text: str = Field(description="Text for the primary call-to-action button.")


class SocialPost(BaseModel):
    platform: Literal["instagram", "linkedin", "twitter"] = Field(
        description="Target social platform."
    )
    caption: str = Field(description="Post caption optimised for the platform.")
    hashtags: list[str] = Field(description="3-5 relevant hashtags without the # symbol.")


class BlogOutline(BaseModel):
    title: str = Field(description="SEO-optimised blog post title.")
    meta_description: str = Field(
        description="Meta description for search engines (under 155 characters)."
    )
    sections: list[str] = Field(
        description="Ordered list of section headings for the blog post."
    )
    estimated_word_count: int = Field(
        description="Estimated total word count for the post."
    )


class ContentPack(BaseModel):
    topic: str = Field(description="Campaign topic.")
    email: EmailCopy = Field(description="Email marketing copy.")
    social: list[SocialPost] = Field(
        description="Social posts for Instagram, LinkedIn, and Twitter."
    )
    blog: BlogOutline = Field(description="Blog post outline.")


class ResponseEngineResult(BaseModel):
    brand_name: str = Field(description="Our brand name.")
    urgency: ResponseUrgency = Field(
        description="Classified urgency level for the signal batch."
    )
    classification: SignalClassification = Field(
        description="Full classification output from the gate agent."
    )
    counter_brief: CounterBrief | None = Field(
        default=None,
        description="Counter-campaign brief; only present when urgency is 'respond'.",
    )
    content_pack: ContentPack | None = Field(
        default=None,
        description="Full content pack; only present when urgency is 'respond'.",
    )
