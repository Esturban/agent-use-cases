from typing import Literal

from pydantic import BaseModel, Field


class CampaignBrief(BaseModel):
    topic: str = Field(description="Campaign topic or product/service being promoted.")
    target_audience: str = Field(description="Description of the target audience.")
    key_message: str = Field(description="Primary message the campaign should convey.")
    tone: Literal["professional", "casual", "playful", "urgent"] = Field(
        description="Desired tone for all content."
    )
    call_to_action: str = Field(description="The desired action the audience should take.")


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
    estimated_word_count: int = Field(description="Estimated total word count for the post.")


class ContentPack(BaseModel):
    topic: str = Field(description="Campaign topic.")
    email: EmailCopy = Field(description="Email marketing copy.")
    social: list[SocialPost] = Field(
        description="Social posts for Instagram, LinkedIn, and Twitter."
    )
    blog: BlogOutline = Field(description="Blog post outline.")
