from dotenv import load_dotenv

load_dotenv()

from src.schema import CampaignBrief  # noqa: E402
from src.workflow import run  # noqa: E402

BRIEF = CampaignBrief(
    topic="Launch of TaskFlow Pro — AI-powered project management",
    target_audience="Startup founders and team leads at companies with 10-100 employees who are drowning in project chaos",
    key_message="TaskFlow Pro uses AI to automatically prioritise your team's work so you ship faster with less stress",
    tone="casual",
    call_to_action="Start your free 14-day trial at taskflow.io",
)

if __name__ == "__main__":
    print(f"Generating content pack for: {BRIEF.topic}\n")
    pack = run(BRIEF)

    print("=== EMAIL ===")
    print(f"Subject: {pack.email.subject}")
    print(f"Preview: {pack.email.preview_text}")
    print(f"CTA Button: {pack.email.cta_button_text}")
    print(f"\n{pack.email.body}")

    print("\n=== SOCIAL POSTS ===")
    for post in pack.social:
        print(f"\n[{post.platform.upper()}]")
        print(post.caption)
        print("  #" + "  #".join(post.hashtags))

    print("\n=== BLOG OUTLINE ===")
    print(f"Title: {pack.blog.title}")
    print(f"Meta: {pack.blog.meta_description}")
    print(f"~{pack.blog.estimated_word_count} words")
    for i, section in enumerate(pack.blog.sections, 1):
        print(f"  {i}. {section}")
