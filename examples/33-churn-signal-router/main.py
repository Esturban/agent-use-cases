import json

from src.schema import NpsResponse
from src.workflow import run


def main() -> None:
    responses = [
        NpsResponse(customer_id="C-001", score=2, comment="The product keeps crashing and support never replies."),
        NpsResponse(customer_id="C-002", score=9, comment="Fantastic tool, saves me hours every week. Love it!"),
        NpsResponse(customer_id="C-003", score=7, comment="It's okay but the reporting could be better."),
        NpsResponse(customer_id="C-004", score=5, comment="Not terrible, just not what I expected."),
        NpsResponse(customer_id="C-005", score=10, comment="Best decision we made. Highly recommend."),
        NpsResponse(customer_id="C-006", score=3, comment="Considering switching. Too many bugs."),
    ]

    batch = run(responses)

    print(f"Processed: {batch.total} responses")
    print(f"Retain: {batch.retain_count} | Neutral: {batch.neutral_count} | Escalate: {batch.escalate_count}")
    print()

    for r in batch.responses:
        print(f"[{r.segment.upper()}] {r.customer_id} (score {r.score})")
        print(f"  Reason: {r.reasoning}")
        print(f"  Draft: {r.follow_up_draft[:120]}...")
        print()

    print("Full batch:")
    print(json.dumps(batch.model_dump(), indent=2))


if __name__ == "__main__":
    main()
