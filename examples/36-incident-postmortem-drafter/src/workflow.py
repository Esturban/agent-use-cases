import os

from openai import OpenAI

from .schema import IncidentTimeline, Postmortem

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
_MODEL = "gpt-4o-mini"

_PARSE_SYSTEM = """You are an incident timeline parser.

Given raw incident log text, extract a structured IncidentTimeline JSON object.

Rules:
- Assign severity "critical" for complete outages or data loss, "warning" for degraded service, "info" for monitoring/mitigation steps.
- Use ISO-8601 timestamps (YYYY-MM-DDTHH:MM:SSZ) for all times.
- Calculate duration_minutes from start_time to end_time.
- List every distinct service, API, or database mentioned as affected.
- Return ONLY valid JSON matching the schema — no prose."""

_POSTMORTEM_SYSTEM = """You are a senior site reliability engineer drafting a blameless postmortem.

Given a structured IncidentTimeline JSON, produce a complete Postmortem document as JSON.

Rules:
- root_cause: one concise sentence naming the single primary cause.
- contributing_factors: list secondary factors (misconfiguration, missing alerting, capacity gap).
- impact_summary: 2-3 sentences covering estimated users affected, downtime duration, and business impact.
- action_items: specific, actionable items — each should mention an owner role and a target completion timeframe.
- detection_improvements: concrete changes to monitoring, alerting thresholds, or runbooks.
- executive_summary: 1-2 paragraphs suitable for a VP or board update — no jargon, focus on business impact and remediation commitment.
- Return ONLY valid JSON matching the schema — no prose."""


def _parse_timeline(raw_log: str) -> IncidentTimeline:
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _PARSE_SYSTEM},
            {"role": "user", "content": raw_log},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "IncidentTimeline",
                "strict": True,
                "schema": IncidentTimeline.model_json_schema(),
            },
        },
    )
    return IncidentTimeline.model_validate_json(resp.choices[0].message.content)


def _draft_postmortem(timeline: IncidentTimeline) -> Postmortem:
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _POSTMORTEM_SYSTEM},
            {"role": "user", "content": timeline.model_dump_json()},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "Postmortem",
                "strict": True,
                "schema": Postmortem.model_json_schema(),
            },
        },
    )
    return Postmortem.model_validate_json(resp.choices[0].message.content)


def run(raw_log: str) -> Postmortem:
    timeline = _parse_timeline(raw_log)
    return _draft_postmortem(timeline)
