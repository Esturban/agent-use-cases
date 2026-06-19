# 37 — Campaign Brief Fan-Out

One campaign brief fans out in parallel to three specialist agents — email copywriter, social media strategist, and SEO blog planner — and assembles the results into a typed `ContentPack`.

## What it does

Takes a structured campaign brief (topic, audience, key message, tone, CTA) and runs three specialist LLM agents concurrently:

1. **Email Copywriter** — subject line, preview text, full body, and CTA button text
2. **Social Media Strategist** — platform-native posts for Instagram, LinkedIn, and Twitter
3. **Blog Planner** — SEO-optimised title, meta description, section outline, and word count estimate

All three run in parallel via `ThreadPoolExecutor`; the `ContentPack` is assembled once all three complete.

## Architecture

```
main.py
└── src/workflow.py        # run(brief) → ContentPack via ThreadPoolExecutor(max_workers=3)
    ├── src/agents.py      # _write_email / _write_social / _write_blog
    ├── src/prompts.py     # EMAIL_SYSTEM, SOCIAL_SYSTEM, BLOG_SYSTEM
    └── src/schema.py      # CampaignBrief, EmailCopy, SocialPost, BlogOutline, ContentPack
```

## Setup

```bash
pip install openai pydantic python-dotenv
```

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_key
```

## Usage

```bash
python main.py
```

## Output

```json
{
  "topic": "Launch of TaskFlow Pro",
  "email": {
    "subject": "Your team's chaos ends today",
    "preview_text": "AI-powered priorities, zero guesswork",
    "body": "...",
    "cta_button_text": "Start free trial"
  },
  "social": [
    {"platform": "instagram", "caption": "...", "hashtags": ["productivity", "startup"]},
    {"platform": "linkedin", "caption": "...", "hashtags": ["projectmanagement"]},
    {"platform": "twitter", "caption": "...", "hashtags": ["SaaS"]}
  ],
  "blog": {
    "title": "How AI Project Management Helps Startups Ship Faster",
    "meta_description": "...",
    "sections": ["Introduction", "The Priority Problem", "..."],
    "estimated_word_count": 1200
  }
}
```

## Workbook

Open `campaign_brief_fan_out_workbook.ipynb` for an interactive walkthrough.
