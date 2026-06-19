"""
Pydantic models for the self-healing CI agent.

Covers the full repair-loop lifecycle:
  CIFailure → FailureClassification → RepairAttempt(s) → RepairPostmortem → HealingResult
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ErrorType = Literal["dependency", "config", "code", "test", "flaky", "unknown"]
RepairStrategy = Literal[
    "pin_dependency", "update_config", "fix_syntax", "skip_test", "retry", "escalate"
]


class CIFailure(BaseModel):
    """Input: a single CI job failure to be healed."""

    log_snippet: str = Field(
        description="Relevant excerpt from the CI job log (stderr, traceback, exit output)."
    )
    job_name: str = Field(
        description="Name of the CI job that failed (e.g. 'build', 'test', 'lint')."
    )
    step_name: str = Field(
        description="Name of the step within the job that produced the failure."
    )
    exit_code: int = Field(
        description="Process exit code returned by the failing step."
    )


class FailureClassification(BaseModel):
    """LLM output: classification of a CI failure."""

    error_type: ErrorType = Field(
        description=(
            "Category of the failure: dependency (missing/conflicting package), "
            "config (misconfigured env or CI YAML), code (syntax or runtime bug), "
            "test (deterministic test assertion failure), flaky (non-deterministic / "
            "intermittent failure), or unknown."
        )
    )
    root_cause: str = Field(
        description="One-sentence description of the most likely root cause."
    )
    suggested_strategy: RepairStrategy = Field(
        description=(
            "Recommended first repair strategy: pin_dependency, update_config, "
            "fix_syntax, skip_test, retry, or escalate."
        )
    )
    confidence: float = Field(
        description=(
            "Confidence score for this classification, between 0.0 (no confidence) "
            "and 1.0 (certain)."
        ),
        ge=0.0,
        le=1.0,
    )


class RepairAttempt(BaseModel):
    """Record of a single repair iteration."""

    attempt_number: int = Field(
        description="1-based index of this attempt within the current healing run."
    )
    strategy: RepairStrategy = Field(
        description="Repair strategy applied in this attempt."
    )
    action_taken: str = Field(
        description=(
            "Concrete action performed (e.g. 'pinned requests==2.31.0 in requirements.txt')."
        )
    )
    patch_description: str = Field(
        description=(
            "Human-readable description of what the patch changes and why it should "
            "resolve the failure."
        )
    )
    validation_result: Literal["pass", "fail", "inconclusive"] = Field(
        description=(
            "Outcome after applying the patch: pass (issue resolved), "
            "fail (patch did not help), or inconclusive (cannot determine)."
        )
    )
    notes: str = Field(
        description=(
            "Additional context, warnings, or rationale from the LLM about this attempt."
        )
    )


class RepairPostmortem(BaseModel):
    """Terminal postmortem emitted when all retries are exhausted."""

    job_name: str = Field(
        description="Name of the CI job that could not be healed."
    )
    error_type: ErrorType = Field(
        description="Error category as determined during the initial classification step."
    )
    attempts: list[RepairAttempt] = Field(
        description="All repair attempts made before giving up, in order."
    )
    terminal_failure: bool = Field(
        description=(
            "Always True for a postmortem — indicates the agent could not resolve "
            "the issue."
        )
    )
    root_cause: str = Field(
        description="Final assessment of the root cause after all repair attempts."
    )
    recommended_fix: str = Field(
        description=(
            "Best recommended fix for a human engineer to apply manually."
        )
    )
    escalation_notes: str = Field(
        description=(
            "Context and next steps for the on-call engineer or team receiving "
            "this escalation."
        )
    )


class HealingResult(BaseModel):
    """Top-level result returned by the orchestrator's run() function."""

    job_name: str = Field(
        description="Name of the CI job that was processed."
    )
    resolved: bool = Field(
        description=(
            "True if the agent successfully healed the failure, False if retries "
            "were exhausted."
        )
    )
    attempts_taken: int = Field(
        description="Total number of repair attempts made."
    )
    final_strategy: RepairStrategy | None = Field(
        default=None,
        description="Strategy that resolved the failure, or None if unresolved.",
    )
    postmortem: RepairPostmortem | None = Field(
        default=None,
        description="Structured postmortem, populated only when resolved=False.",
    )
