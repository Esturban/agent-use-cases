"""
Self-healing CI agent — bounded ReAct repair loop.

Loop structure (max_retries iterations):
  1. classify()       — identify error type, root cause, suggested strategy
  2. propose_repair() — propose a concrete patch based on classification + history
  3. validate()       — assess whether the patch resolves the original failure
  4. if pass: return HealingResult(resolved=True)
  5. if retries exhausted: write_postmortem() -> HealingResult(resolved=False)

All LLM calls use structured JSON output via OpenAI response_format.
"""
from __future__ import annotations

import json
import os

from openai import OpenAI

from .prompts import CLASSIFY_SYSTEM, POSTMORTEM_SYSTEM, REPAIR_SYSTEM, VALIDATE_SYSTEM
from .schema import (
    CIFailure,
    FailureClassification,
    HealingResult,
    RepairAttempt,
    RepairPostmortem,
)

_MODEL = "gpt-4o-mini"


def _get_client() -> OpenAI:
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def _classify(failure: CIFailure) -> FailureClassification:
    """Call the LLM to classify the CI failure."""
    client = _get_client()
    user_content = (
        f"Job: {failure.job_name}\n"
        f"Step: {failure.step_name}\n"
        f"Exit code: {failure.exit_code}\n\n"
        f"Log snippet:\n{failure.log_snippet}"
    )
    resp = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": CLASSIFY_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "FailureClassification",
                "strict": True,
                "schema": FailureClassification.model_json_schema(),
            },
        },
    )
    return FailureClassification.model_validate_json(resp.choices[0].message.content)


def _propose_repair(
    failure: CIFailure,
    classification: FailureClassification,
    attempts: list[RepairAttempt],
) -> RepairAttempt:
    """Call the LLM to propose the next repair action."""
    client = _get_client()
    user_content = json.dumps(
        {
            "failure": failure.model_dump(),
            "classification": classification.model_dump(),
            "prior_attempts": [a.model_dump() for a in attempts],
        },
        indent=2,
    )
    resp = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": REPAIR_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "RepairAttempt",
                "strict": True,
                "schema": RepairAttempt.model_json_schema(),
            },
        },
    )
    attempt = RepairAttempt.model_validate_json(resp.choices[0].message.content)
    attempt.notes = attempt.notes or "pending"
    return attempt


def _validate(failure: CIFailure, attempt: RepairAttempt) -> RepairAttempt:
    """Validate whether the repair attempt resolves the failure.

    Fills attempt.validation_result and attempt.notes and returns the updated attempt.
    """
    client = _get_client()
    user_content = json.dumps(
        {
            "attempt": attempt.model_dump(),
            "original_log_snippet": failure.log_snippet,
        },
        indent=2,
    )
    resp = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": VALIDATE_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
    )
    verdict = json.loads(resp.choices[0].message.content)
    attempt.validation_result = verdict.get("validation_result", "inconclusive")
    attempt.notes = verdict.get("notes", attempt.notes)
    return attempt


def _write_postmortem(
    failure: CIFailure,
    classification: FailureClassification,
    attempts: list[RepairAttempt],
) -> RepairPostmortem:
    """Write a terminal postmortem after retries are exhausted."""
    client = _get_client()
    user_content = json.dumps(
        {
            "failure": failure.model_dump(),
            "classification": classification.model_dump(),
            "attempts": [a.model_dump() for a in attempts],
        },
        indent=2,
    )
    resp = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": POSTMORTEM_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "RepairPostmortem",
                "strict": True,
                "schema": RepairPostmortem.model_json_schema(),
            },
        },
    )
    return RepairPostmortem.model_validate_json(resp.choices[0].message.content)


def run(failure: CIFailure, max_retries: int = 3) -> HealingResult:
    """
    Run the bounded self-healing loop for a CI failure.

    Steps:
      1. Classify the failure.
      2. Loop up to max_retries times:
         a. Propose a repair.
         b. Validate the repair.
         c. If validation_result == "pass", return resolved HealingResult.
      3. If the loop exhausts retries, write a postmortem and return unresolved.

    Args:
        failure:     The CI failure to heal.
        max_retries: Maximum repair attempts before giving up (default 3).

    Returns:
        HealingResult with resolved=True and final_strategy on success, or
        resolved=False with a populated postmortem on terminal failure.
    """
    classification = _classify(failure)
    attempts: list[RepairAttempt] = []

    for _ in range(max_retries):
        attempt = _propose_repair(failure, classification, attempts)
        attempt = _validate(failure, attempt)
        attempts.append(attempt)

        if attempt.validation_result == "pass":
            return HealingResult(
                job_name=failure.job_name,
                resolved=True,
                attempts_taken=len(attempts),
                final_strategy=attempt.strategy,
            )

    postmortem = _write_postmortem(failure, classification, attempts)
    return HealingResult(
        job_name=failure.job_name,
        resolved=False,
        attempts_taken=len(attempts),
        final_strategy=None,
        postmortem=postmortem,
    )
