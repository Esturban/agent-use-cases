"""Regulatory change tracker workflow — delta-aware stateful extraction."""

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

from openai import OpenAI

from .prompts import EXPOSURE_SYSTEM, EXTRACTION_SYSTEM, STATE_UPDATE_SYSTEM
from .schema import (
    ChangeTrackerResult,
    ComplianceState,
    ContractExposure,
    NewObligation,
    ObligationImpact,
    ObligationRegister,
    RegulatoryUpdate,
)

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
_MODEL = "gpt-4.1-nano"


def _extract_obligations(
    update: RegulatoryUpdate,
    register: ObligationRegister,
) -> list[NewObligation]:
    """Stage 1: diff the update against the register; return only net-new obligations."""
    user_message = json.dumps(
        {
            "update": update.model_dump(),
            "existing_obligations": [o.model_dump() for o in register.obligations],
        }
    )
    array_schema = {
        "type": "object",
        "properties": {
            "obligations": {
                "type": "array",
                "items": NewObligation.model_json_schema(),
            }
        },
        "required": ["obligations"],
        "additionalProperties": False,
    }
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM},
            {"role": "user", "content": user_message},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "NewObligationList",
                "strict": True,
                "schema": array_schema,
            },
        },
    )
    data = json.loads(resp.choices[0].message.content)
    return [NewObligation.model_validate(o) for o in data["obligations"]]


def _assess_exposure(
    obligation: NewObligation,
    contracts: list[dict],
) -> ObligationImpact:
    """Stage 2: assess one net-new obligation against the full contract corpus."""
    user_message = json.dumps(
        {
            "obligation": obligation.model_dump(),
            "contracts": contracts,
        }
    )
    array_schema = {
        "type": "object",
        "properties": {
            "exposures": {
                "type": "array",
                "items": ContractExposure.model_json_schema(),
            }
        },
        "required": ["exposures"],
        "additionalProperties": False,
    }
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": EXPOSURE_SYSTEM},
            {"role": "user", "content": user_message},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "ContractExposureList",
                "strict": True,
                "schema": array_schema,
            },
        },
    )
    data = json.loads(resp.choices[0].message.content)
    exposures = [ContractExposure.model_validate(e) for e in data["exposures"]]

    _severity_rank = {"none": 0, "moderate": 1, "severe": 2}
    overall = (
        max(exposures, key=lambda e: _severity_rank[e.impact]).impact
        if exposures
        else "none"
    )
    severe_or_moderate = [e for e in exposures if e.impact != "none"]
    action = (
        severe_or_moderate[0].remediation_action
        if severe_or_moderate
        else "No action required"
    )
    return ObligationImpact(
        obligation=obligation,
        contract_exposures=exposures,
        overall_impact=overall,
        action_item=action,
    )


def _update_state(
    state: ComplianceState,
    assessments: list[ObligationImpact],
    update: RegulatoryUpdate,
) -> ComplianceState:
    """Stage 3: produce a new versioned ComplianceState incorporating the assessed obligations."""
    user_message = json.dumps(
        {
            "existing_state": state.model_dump(),
            "assessments": [a.model_dump() for a in assessments],
            "update_id": update.update_id,
            "today": date.today().isoformat(),
        }
    )
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": STATE_UPDATE_SYSTEM},
            {"role": "user", "content": user_message},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "ComplianceState",
                "strict": True,
                "schema": ComplianceState.model_json_schema(),
            },
        },
    )
    return ComplianceState.model_validate_json(resp.choices[0].message.content)


def run(
    update: RegulatoryUpdate,
    register: ObligationRegister,
    contracts: list[dict],
    state: ComplianceState,
) -> ChangeTrackerResult:
    """Run the full regulatory change tracking pipeline.

    Args:
        update: The incoming regulatory update to process.
        register: The existing obligation register to diff against.
        contracts: List of contract excerpts, each a dict with keys
                   ``contract_name`` and ``excerpt``.
        state: The current versioned ComplianceState to update.

    Returns:
        A ChangeTrackerResult containing the net-new count, per-obligation
        impact assessments, updated ComplianceState, and an executive summary.
    """
    # Stage 1 — extract net-new obligations via diff
    new_obligations = _extract_obligations(update, register)

    # Stage 2 — assess exposure for each new obligation in parallel
    assessments: list[ObligationImpact] = []
    if new_obligations:
        with ThreadPoolExecutor(max_workers=min(len(new_obligations), 5)) as executor:
            futures = {
                executor.submit(_assess_exposure, obl, contracts): obl
                for obl in new_obligations
            }
            for future in as_completed(futures):
                assessments.append(future.result())

    # Stage 3 — write versioned state update
    updated_state = _update_state(state, assessments, update)

    _severity_rank = {"none": 0, "moderate": 1, "severe": 2}
    top_impact = (
        max(assessments, key=lambda a: _severity_rank[a.overall_impact]).overall_impact
        if assessments
        else "none"
    )
    top_action = (
        next(
            (a.action_item for a in assessments if a.overall_impact == top_impact),
            "No action required",
        )
        if top_impact != "none"
        else "No action required"
    )
    summary = (
        f"Processed {update.update_id}: {len(new_obligations)} net-new obligation(s) identified "
        f"for {update.jurisdiction}. "
        f"Highest exposure level: {top_impact}. "
        f"Top priority action: {top_action}"
    )

    return ChangeTrackerResult(
        update_id=update.update_id,
        net_new_count=len(new_obligations),
        impact_assessments=assessments,
        updated_state=updated_state,
        summary=summary,
    )
