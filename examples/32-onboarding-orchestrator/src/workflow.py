from concurrent.futures import ThreadPoolExecutor, as_completed

from .agents import run_facilities, run_hr, run_it, synthesise
from .schema import NewHire, OnboardingPlan


def run(new_hire: NewHire) -> OnboardingPlan:
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_it, new_hire): "it",
            executor.submit(run_hr, new_hire): "hr",
            executor.submit(run_facilities, new_hire): "facilities",
        }
        results = {}
        for future in as_completed(futures):
            key = futures[future]
            results[key] = future.result()

    return synthesise(
        new_hire,
        it=results["it"],
        hr=results["hr"],
        facilities=results["facilities"],
    )
