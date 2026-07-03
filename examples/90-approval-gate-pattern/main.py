"""Entry point — runs three scenarios through the approval-gate pattern.

Each scenario calls propose() first (the graph runs up to the interrupt and
genuinely halts) and only then calls resume() with a human ApprovalDecision.
The print output separates the two calls on purpose: the proposed action is
printed *before* any decision exists, exactly as it would be if a human were
reading it from a queue before deciding anything.
"""

import os

from dotenv import load_dotenv

from src.schema import ApprovalDecision
from src.workflow import propose, resume

load_dotenv()


SCENARIOS = [
    {
        "label": "APPROVE",
        "event": (
            "Post a $4,200 accrual for Q2 consulting fees to cost centre CC1001."
        ),
        "decision": ApprovalDecision(
            decision="approve",
            rationale="Matches the signed SOW, approving as drafted.",
        ),
    },
    {
        "label": "EDIT THEN APPROVE",
        "event": (
            "Revoke admin access for the contractor identity CTR-4471, "
            "offboarding effective today."
        ),
        # edited_payload is filled in once the proposed payload is known (see main())
        "decision": None,
    },
    {
        "label": "REJECT",
        "event": (
            "Send a final notice collection letter to customer ACME Corp for "
            "invoice INV-9981, $58,000 outstanding 95 days."
        ),
        "decision": ApprovalDecision(
            decision="reject",
            rationale=(
                "Customer has an active payment plan on file -- escalate to "
                "account manager first, do not send a legal-toned notice yet."
            ),
        ),
    },
]


def main():
    for scenario in SCENARIOS:
        print(f"\n{'=' * 70}\nScenario: {scenario['label']}\n{'=' * 70}")
        print(f"Event: {scenario['event']}")

        proposed, thread_id = propose(scenario["event"])
        print("\n-- paused at human_review --")
        print(f"Proposed action_type : {proposed.action_type}")
        print(f"Summary               : {proposed.summary}")
        print(f"Payload               : {proposed.payload}")
        print(f"Risk level            : {proposed.risk_level}")

        decision = scenario["decision"]
        if decision is None:
            # The edit scenario needs the real proposed payload to edit against.
            decision = ApprovalDecision(
                decision="edit",
                edited_payload={**proposed.payload, "effective_date": "2026-07-07"},
                rationale=(
                    "Push effective date to next Monday per offboarding policy, "
                    "not same-day revocation."
                ),
            )

        result = resume(thread_id, decision)
        print("\n-- resumed with human decision --")
        print(f"Decision   : {decision.decision}")
        print(f"Executed   : {result.executed}")
        print(f"Final      : {result.final_payload}")
        print(f"Audit log  : {result.decision_log}")


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set — copy .env.example to .env")
    main()
