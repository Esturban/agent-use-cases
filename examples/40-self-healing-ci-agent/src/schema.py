"""
Pydantic models for the self-healing CI agent.

Covers the full repair-loop lifecycle:
  CIFailure -> RepairAttempt(s) -> RepairPostmortem -> HealingResult

RepairAttempt now records actual tool calls and their observed results rather
than hypothetical patch descriptions — the agent calls real tools and the
schema captures what happened.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class CIFailure(BaseModel):
    """Input: a single CI job failure to be healed."""

    error_log: str = Field(
        description=(
            "Full error log from the CI job (stderr, traceback, exit output). "
            "This is passed verbatim to the agent as the problem to fix."
        )
    )
    job_name: str = Field(
        description="Name of the CI job that failed (e.g. 'build', 'test', 'lint')."
    )


class RepairAttempt(BaseModel):
    """Record of a single tool call made during the repair loop."""

    iteration: int = Field(
        description="1-based loop iteration in which this tool call occurred."
    )
    tool_called: str = Field(
        description=(
            "Name of the tool the agent invoked "
            "(apply_dependency_fix | apply_env_fix | apply_code_patch | run_tests)."
        )
    )
    arguments: dict = Field(
        description="Arguments passed to the tool, as a dict."
    )
    result: dict = Field(
        description="Return value from the tool, as a dict."
    )


class RepairPostmortem(BaseModel):
    """Terminal postmortem emitted when all retries are exhausted."""

    job_name: str = Field(
        description="Name of the CI job that could not be healed."
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
        description="Best recommended fix for a human engineer to apply manually."
    )
    escalation_notes: str = Field(
        description=(
            "Context and next steps for the on-call engineer or team receiving "
            "this escalation."
        )
    )


class HealingResult(BaseModel):
    """Top-level result returned by workflow.run()."""

    healed: bool = Field(
        description=(
            "True if the agent successfully healed the failure, False if retries "
            "were exhausted."
        )
    )
    iterations_used: int = Field(
        description="Total number of loop iterations consumed."
    )
    attempts: list[RepairAttempt] = Field(
        description="All tool calls made during the healing run, in order."
    )
    postmortem: RepairPostmortem | None = Field(
        default=None,
        description="Structured postmortem, populated only when healed=False.",
    )
