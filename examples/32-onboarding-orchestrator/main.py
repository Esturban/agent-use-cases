import json

from src.schema import NewHire
from src.workflow import run


def main() -> None:
    scenarios = [
        NewHire(
            name="Jane Smith",
            role="Senior Software Engineer",
            department="Engineering",
            start_date="2026-07-14",
            location="New York",
        ),
        NewHire(
            name="Carlos Rivera",
            role="Marketing Manager",
            department="Marketing",
            start_date="2026-07-21",
            location="remote",
        ),
    ]

    for hire in scenarios:
        print(f"\n--- Onboarding Plan: {hire.name} ({hire.role}) ---")
        plan = run(hire)
        print(f"Day 1 Ready: {plan.day1_ready}")
        print(f"Blockers: {plan.blockers or 'None'}")
        print(f"Summary: {plan.summary}")
        print("\nIT Tasks:", plan.it_status.completed)
        print("HR Tasks:", plan.hr_status.completed)
        print("Facilities Tasks:", plan.facilities_status.completed)
        print("\nFull plan:")
        print(json.dumps(plan.model_dump(), indent=2))


if __name__ == "__main__":
    main()
