"""
Lifecycle-stage state machine orchestrator.

run() is the single public entrypoint. It:
  1. Appends the incoming signal to the CustomerRecord.
  2. Dispatches to the specialist agent for the CURRENT stage only.
  3. Asks the transition agent whether a stage change is warranted.
  4. Updates the record and returns an OrchestratorResult.
"""
import json
import os
from typing import Any

from openai import OpenAI

from .prompts import (
    CHURN_SYSTEM,
    HEALTH_SYSTEM,
    ONBOARD_SYSTEM,
    QUALIFY_SYSTEM,
    RENEWAL_SYSTEM,
    TRANSITION_SYSTEM,
)
from .schema import (
    ChurnResponse,
    CustomerRecord,
    CustomerSignal,
    HealthAssessment,
    LifecycleStage,
    OnboardingStatus,
    OrchestratorResult,
    QualificationResult,
    RenewalPackage,
    StageOutput,
)

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
_MODEL = "gpt-4.1-nano"

# Map each stage to its specialist (system prompt, schema name, Pydantic model)
_STAGE_AGENTS: dict[str, tuple[str, str, Any]] = {
    "lead": (QUALIFY_SYSTEM, "QualificationResult", QualificationResult),
    "onboarding": (ONBOARD_SYSTEM, "OnboardingStatus", OnboardingStatus),
    "healthy": (HEALTH_SYSTEM, "HealthAssessment", HealthAssessment),
    "at_risk": (CHURN_SYSTEM, "ChurnResponse", ChurnResponse),
    "renewal": (RENEWAL_SYSTEM, "RenewalPackage", RenewalPackage),
}


def _run_stage_agent(
    record: CustomerRecord,
    system: str,
    schema_name: str,
    schema: Any,
) -> dict:
    """Call the specialist agent for the current stage and return its output as a dict."""
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": record.model_dump_json()},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": schema.model_json_schema(),
            },
        },
    )
    validated = schema.model_validate_json(resp.choices[0].message.content)
    return validated.model_dump()


def _check_transition(
    record: CustomerRecord,
    stage_output_dict: dict,
) -> tuple[bool, LifecycleStage | None]:
    """
    Ask the transition agent whether the account should move to a new stage.

    Returns (should_transition, next_stage).
    """
    payload = {
        "customer_record": record.model_dump(),
        "stage_output": stage_output_dict,
    }
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": TRANSITION_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_object"},
    )
    decision = json.loads(resp.choices[0].message.content)
    should_transition: bool = bool(decision.get("should_transition", False))
    next_stage_raw: str | None = decision.get("next_stage")
    next_stage: LifecycleStage | None = (
        next_stage_raw if should_transition and next_stage_raw else None
    )
    return should_transition, next_stage


def _update_record(
    record: CustomerRecord,
    stage_output_dict: dict,
    next_stage: LifecycleStage | None,
) -> CustomerRecord:
    """
    Apply updates from the stage output back to the CustomerRecord.

    Updates health_score if the output contains one, transitions the stage
    if next_stage is set, and appends a summary note.
    """
    updates: dict = {}

    if next_stage is not None:
        updates["stage"] = next_stage

    # Propagate health_score from HealthAssessment or RenewalPackage outputs
    if "health_score" in stage_output_dict:
        updates["health_score"] = stage_output_dict["health_score"]

    # Propagate NPS if a new nps_score signal was submitted
    if "nps_score" in stage_output_dict:
        updates["nps_score"] = stage_output_dict["nps_score"]

    # Append a brief agent note for traceability
    current_stage = record.stage
    note = f"[{current_stage}] agent ran"
    if next_stage:
        note += f"; transitioned to {next_stage}"
    updated_notes = list(record.notes) + [note]
    updates["notes"] = updated_notes

    return record.model_copy(update=updates)


def run(record: CustomerRecord, signal: CustomerSignal) -> OrchestratorResult:
    """
    Process a single incoming signal for a customer account.

    Steps:
      1. Append the signal to the record.
      2. Dispatch to the specialist agent for the current stage.
      3. Check whether a stage transition is warranted.
      4. Update the record with any changes.
      5. Return an OrchestratorResult.
    """
    previous_stage: LifecycleStage = record.stage

    # 1. Append signal
    updated_signals = list(record.signals) + [signal]
    record = record.model_copy(update={"signals": updated_signals})

    # 2. Dispatch to the correct specialist agent
    system, schema_name, schema = _STAGE_AGENTS[record.stage]
    stage_output_dict = _run_stage_agent(record, system, schema_name, schema)

    # 3. Check transition
    should_transition, next_stage = _check_transition(record, stage_output_dict)

    # 4. Update record
    updated_record = _update_record(record, stage_output_dict, next_stage)

    return OrchestratorResult(
        customer_id=record.customer_id,
        previous_stage=previous_stage,
        stage_output=StageOutput(
            stage_handled=previous_stage,
            output=stage_output_dict,
            next_stage=next_stage,
            updated_record=updated_record,
        ),
        transition_occurred=should_transition and next_stage is not None,
    )
