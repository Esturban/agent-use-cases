import json

from src.schema import PatientCriteria
from src.workflow import run


def main() -> None:
    scenarios = [
        PatientCriteria(
            condition="type 2 diabetes",
            age=55,
            location="United States",
            exclusions=["insulin dependent", "severe kidney disease"],
        ),
        PatientCriteria(
            condition="non-small cell lung cancer",
            age=62,
            location="",
            exclusions=["prior immunotherapy"],
        ),
    ]

    result = None
    for criteria in scenarios:
        print(f"\n--- Clinical Trial Search: {criteria.condition} (age {criteria.age}) ---")
        result = run(criteria)
        print(f"Trials found via API: {result.trials_found}")
        print(f"Eligible matches: {len(result.matches)}")
        print()
        for match in result.matches:
            print(f"  [{match.match_confidence.upper()}] {match.nct_id} -- {match.title}")
            print(f"  Phase: {match.phase} | Status: {match.status}")
            print(f"  {match.eligibility_summary}")
            print(f"  Why matches: {match.why_matches}")
            print()

    if result:
        print("Full result (last search):")
        print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()
