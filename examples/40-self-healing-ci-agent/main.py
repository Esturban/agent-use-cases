"""
Example 40 — Self-Healing CI Agent

Two CI failure scenarios:
  A. Dependency conflict — missing package should resolve within retries.
  B. Flaky test — keeps failing, exhausts retries, emits a structured postmortem.
"""
from dotenv import load_dotenv

load_dotenv()

from src.schema import CIFailure  # noqa: E402
from src.workflow import run  # noqa: E402

# ---------------------------------------------------------------------------
# Scenario A — dependency conflict (expected to resolve)
# ---------------------------------------------------------------------------
SCENARIO_A = CIFailure(
    job_name="build",
    step_name="install-dependencies",
    exit_code=1,
    log_snippet=(
        "Collecting dependencies from requirements.txt\n"
        "ERROR: Could not find a version that satisfies the requirement requests>=2.28.0\n"
        "ERROR: No matching distribution found for requests>=2.28.0\n"
        "ModuleNotFoundError: No module named 'requests'\n"
        "Command 'pip install -r requirements.txt' returned non-zero exit status 1."
    ),
)

# ---------------------------------------------------------------------------
# Scenario B — flaky test (expected to exhaust retries and emit postmortem)
# ---------------------------------------------------------------------------
SCENARIO_B = CIFailure(
    job_name="test",
    step_name="run-unit-tests",
    exit_code=1,
    log_snippet=(
        "FAILED tests/test_payment_processor.py::test_stripe_charge_idempotency\n"
        "AssertionError: assert response.status_code == 200\n"
        "  where response.status_code = 500\n"
        "E   requests.exceptions.ConnectionError: "
        "HTTPSConnectionPool(host='api.stripe.com'): "
        "Max retries exceeded with url: /v1/charges\n"
        "FAILED tests/test_payment_processor.py::test_stripe_charge_idempotency - "
        "ConnectionError\n"
        "1 failed, 47 passed in 12.34s\n"
        "This test fails intermittently on CI runners due to network timeouts. "
        "Retry count: 3/3 exhausted."
    ),
)


def _print_result(label: str, failure: CIFailure) -> None:
    print(f"\n{'=' * 60}")
    print(f"Scenario {label}: {failure.job_name} / {failure.step_name}")
    print("=" * 60)

    result = run(failure, max_retries=3)

    print(f"Job:           {result.job_name}")
    print(f"Resolved:      {result.resolved}")
    print(f"Attempts:      {result.attempts_taken}")

    if result.resolved:
        print(f"Final strategy: {result.final_strategy}")
    else:
        pm = result.postmortem
        if pm:
            print("\n--- Postmortem ---")
            print(f"Error type:      {pm.error_type}")
            print(f"Root cause:      {pm.root_cause}")
            print(f"Recommended fix: {pm.recommended_fix}")
            print(f"Escalation:      {pm.escalation_notes}")
            print(f"\nAttempts made: {len(pm.attempts)}")
            for attempt in pm.attempts:
                print(
                    f"  [{attempt.attempt_number}] {attempt.strategy} "
                    f"-> {attempt.validation_result}: {attempt.action_taken}"
                )


if __name__ == "__main__":
    _print_result("A", SCENARIO_A)
    _print_result("B", SCENARIO_B)
