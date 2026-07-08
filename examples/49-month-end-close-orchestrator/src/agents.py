"""The close-status narrative synthesizer -- the only LLM call in this example.

Readiness, blocked-task delay, and critical path are all deterministic graph
math computed in dag.py. This is the one genuinely open-ended writing task --
turning a typed CloseStatus snapshot into an executive narrative -- which is
why it is the one place an LLM call belongs, matching the convention set by
example 97's audit_trail_synthesizer.
"""

import json

from langchain_openai import ChatOpenAI

from .prompts import CLOSE_NARRATIVE_SYSTEM

_MODEL = "gpt-4.1-nano"


def close_narrative_synthesizer(close_status_payload: dict) -> str:
    """close_status_payload is a CloseStatus.model_dump() with narrative=None.

    All figures inside it (progress, delays, critical path hours) were
    computed by dag.py and are passed through unchanged -- the model narrates
    them, it does not recompute them.
    """
    llm = ChatOpenAI(model=_MODEL, temperature=0)
    response = llm.invoke(
        [("system", CLOSE_NARRATIVE_SYSTEM), ("human", json.dumps(close_status_payload))]
    )
    return response.content
