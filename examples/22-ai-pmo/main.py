from dotenv import load_dotenv

from src.schema import UpdateInput
from src.workflow import run

load_dotenv()

PROJECT = "Platform Migration -- Phase 2"

UPDATES = [
    UpdateInput(
        source="Kick-off notes (Week 1)",
        content=(
            "Project kicked off. Three milestones identified: data migration by Q3-2024, "
            "UAT sign-off by Q4-2024, go-live by Q1-2025. Sarah Chen owns data migration, "
            "James Park owns UAT. No risks or blockers identified yet."
        ),
    ),
    UpdateInput(
        source="Weekly status call (Week 4)",
        content=(
            "Data migration milestone is now at risk. Vendor has not delivered the API spec "
            "as promised. This is blocking Sarah Chen's team. Risk raised: if the spec is not "
            "received by end of this week, the Q3 target will slip. Blocker owner: procurement "
            "needs to escalate to the vendor account manager."
        ),
    ),
    UpdateInput(
        source="Escalation email (Week 6)",
        content=(
            "API spec received after procurement escalation -- blocker resolved. However, "
            "the data migration timeline has slipped by three weeks. New target is early Q4-2024. "
            "UAT sign-off milestone pushed to late Q4-2024 as a result. Go-live target remains "
            "Q1-2025 but is now at risk. Overall project status should be amber."
        ),
    ),
]


def main() -> None:
    history = run(PROJECT, UPDATES)
    for i, state in enumerate(history):
        label = "INITIAL" if i == 0 else f"After update {i}: {UPDATES[i-1].source}"
        print(f"\n{'=' * 60}")
        print(label)
        print(f"Status: {state.overall_status.upper()}")
        print(f"Summary: {state.summary}")
        if state.milestones:
            print(f"\nMilestones ({len(state.milestones)}):")
            for m in state.milestones:
                print(f"  [{m.status}] {m.name} -- {m.due_date}")
        if state.blockers:
            print(f"\nBlockers ({len(state.blockers)}):")
            for b in state.blockers:
                print(f"  {b.description} (raised by {b.raised_by}, needs {b.resolution_needed_from})")
        if state.risks:
            print(f"\nRisks ({len(state.risks)}):")
            for r in state.risks:
                print(f"  [{r.severity.upper()}] {r.description} (owner: {r.owner})")


if __name__ == "__main__":
    main()
