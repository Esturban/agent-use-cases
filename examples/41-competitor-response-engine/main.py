"""Competitor response engine — runnable entry point.

Two scenarios:
  A) Competitor launches a directly competing product  → urgency: respond → full content pack
  B) Minor competitor publishes an unrelated blog post → urgency: ignore → no content generated
"""

from dotenv import load_dotenv

load_dotenv()

from src.schema import CompetitorSignal, SignalBatch  # noqa: E402
from src.workflow import run  # noqa: E402

# ---------------------------------------------------------------------------
# Scenario A — product launch that directly threatens our core offering
# Expected: urgency = "respond" → counter brief + full content pack generated
# ---------------------------------------------------------------------------
SCENARIO_A = SignalBatch(
    brand_name="Flowdesk",
    signals=[
        CompetitorSignal(
            source="product_launch",
            headline="NovaCRM launches free tier with full automation suite",
            summary=(
                "NovaCRM announced a permanent free tier that includes their full marketing "
                "automation suite — email sequences, CRM, and landing pages. The launch is "
                "backed by a $10M Series A and is explicitly targeting small businesses "
                "currently using Flowdesk. Early adopters report the product is feature-complete "
                "for most SMB use cases."
            ),
            competitor_name="NovaCRM",
            brand_name="Flowdesk",
        ),
        CompetitorSignal(
            source="social",
            headline="NovaCRM free tier announcement goes viral on LinkedIn",
            summary=(
                "NovaCRM's LinkedIn post announcing the free tier has over 4,200 reactions and "
                "600 comments in under 12 hours. Multiple small business owners are tagging "
                "Flowdesk and asking whether we plan to respond. Several threads compare "
                "pricing directly and call out Flowdesk's lack of a free plan."
            ),
            competitor_name="NovaCRM",
            brand_name="Flowdesk",
        ),
    ],
)

# ---------------------------------------------------------------------------
# Scenario B — minor competitor publishes a tangential blog post
# Expected: urgency = "ignore" → no brief or content pack generated
# ---------------------------------------------------------------------------
SCENARIO_B = SignalBatch(
    brand_name="Flowdesk",
    signals=[
        CompetitorSignal(
            source="news",
            headline="SmallReach publishes guide to cold email best practices",
            summary=(
                "SmallReach, a niche cold-email tool with under 500 customers, published a "
                "1,500-word blog post on cold email deliverability tips. The post has no paid "
                "distribution, targets enterprise sales teams (not our SMB segment), and does "
                "not mention Flowdesk or any competing product."
            ),
            competitor_name="SmallReach",
            brand_name="Flowdesk",
        ),
    ],
)


def _print_result(label: str, result) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    print(f"Brand:   {result.brand_name}")
    print(f"Urgency: {result.urgency.upper()}")
    print(f"Reason:  {result.classification.reasoning}")

    if result.urgency == "respond":
        print(f"\nKey Threat:  {result.classification.key_threat}")
        print(f"Opportunity: {result.classification.opportunity}")

        brief = result.counter_brief
        print("\n--- Counter Brief ---")
        print(f"Topic:     {brief.topic}")
        print(f"Audience:  {brief.target_audience}")
        print(f"Message:   {brief.key_message}")
        print(f"Tone:      {brief.tone}")
        print(f"CTA:       {brief.call_to_action}")
        print(f"Narrative: {brief.counter_narrative}")

        pack = result.content_pack
        print("\n--- Email ---")
        print(f"Subject:  {pack.email.subject}")
        print(f"Preview:  {pack.email.preview_text}")
        print(f"CTA Btn:  {pack.email.cta_button_text}")
        print(f"\n{pack.email.body}")

        print("\n--- Social Posts ---")
        for post in pack.social:
            print(f"\n[{post.platform.upper()}]")
            print(post.caption)
            print("  #" + "  #".join(post.hashtags))

        print("\n--- Blog Outline ---")
        print(f"Title: {pack.blog.title}")
        print(f"Meta:  {pack.blog.meta_description}")
        print(f"~{pack.blog.estimated_word_count} words")
        for i, section in enumerate(pack.blog.sections, 1):
            print(f"  {i}. {section}")
    else:
        print("\n[No content generated — urgency below response threshold]")


if __name__ == "__main__":
    print("Running Scenario A: Competitor product launch (expect: respond)")
    result_a = run(SCENARIO_A)
    _print_result("SCENARIO A — Product Launch Threat", result_a)

    print("\n\nRunning Scenario B: Minor blog post (expect: ignore)")
    result_b = run(SCENARIO_B)
    _print_result("SCENARIO B — Minor Blog Post", result_b)
