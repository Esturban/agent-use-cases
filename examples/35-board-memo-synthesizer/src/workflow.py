from concurrent.futures import ThreadPoolExecutor, as_completed

from .agents import run_bear, run_bull, run_risk, synthesise
from .schema import BoardMemo


def run(topic: str, reports: list[str]) -> BoardMemo:
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_bull, topic, reports): "bull",
            executor.submit(run_bear, topic, reports): "bear",
            executor.submit(run_risk, topic, reports): "risk",
        }
        results = {}
        for future in as_completed(futures):
            key = futures[future]
            results[key] = future.result()

    return synthesise(
        topic,
        bull=results["bull"],
        bear=results["bear"],
        risk=results["risk"],
    )
