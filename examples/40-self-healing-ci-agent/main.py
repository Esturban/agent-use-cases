"""
Example 40 — Self-Healing CI Agent

Two CI failure scenarios demonstrating real OpenAI tool-calling:
  A. Missing dependency (ModuleNotFoundError) — agent calls apply_dependency_fix
     then run_tests; tests pass on the first attempt.
  B. Flaky network timeout — agent cannot resolve the failure; retries exhaust
     and a structured postmortem is emitted.
"""
from dotenv import load_dotenv

load_dotenv()

from src.schema import CIFailure  # noqa: E402
from src.workflow import run  # noqa: E402

# ---------------------------------------------------------------------------
# Scenario A — missing dependency (expected to heal)
# ---------------------------------------------------------------------------
SCENARIO_A = CIFailure(
    job_name="build",
    error_log=(
        "Collecting dependencies from requirements.txt\n"
        "ERROR: Could not find a version that satisfies the requirement requests>=2.28.0\n"
        "ERROR: No matching distribution found for requests>=2.28.0\n"
        "ModuleNotFoundError: No module named 'requests'\n"
        "Command 'pip install -r requirements.txt' returned non-zero exit status 1."
    ),
)

# ---------------------------------------------------------------------------
# Scenario B — flaky network timeout (expected to exhaust retries + postmortem)
# ---------------------------------------------------------------------------
SCENARIO_B = CIFailure(
    job_name="test",
    error_log=(
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
    print(f"Scenario {label}: {failure.job_name}")
    print("=" * 60)

    result = run(failure, max_iterations=8)

    print(f"Healed:          {result.healed}")
    print(f"Iterations used: {result.iterations_used}")
    print(f"Tool calls made: {len(result.attempts)}")

    if result.attempts:
        print("\n--- Tool call trace ---")
        for attempt in result.attempts:
            status = ""
            if attempt.tool_called == "run_tests":
                passed = attempt.result.get("passed")
                status = " [PASSED]" if passed else " [FAILED]"
            print(
                f"  [iter {attempt.iteration}] {attempt.tool_called}"
                f"({', '.join(f'{k}={v!r}' for k, v in attempt.arguments.items())})"
                f"{status}"
            )
            if attempt.tool_called == "run_tests":
                print(f"    output: {attempt.result.get('output', '')}")

    if result.healed:
        passing_run = next(
            (a for a in reversed(result.attempts) if a.tool_called == "run_tests"),
            None,
        )
        if passing_run:
            print(f"\nTests passed on iteration {passing_run.iteration}.")
    else:
        pm = result.postmortem
        if pm:
            print("\n--- Postmortem ---")
            print(f"Root cause:      {pm.root_cause}")
            print(f"Recommended fix: {pm.recommended_fix}")
            print(f"Escalation:      {pm.escalation_notes}")


if __name__ == "__main__":
    _print_result("A", SCENARIO_A)
    _print_result("B", SCENARIO_B)
