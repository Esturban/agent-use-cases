"""The audit-trail synthesizer -- the only LLM call in this example.

Every other domain check in checks.py is deterministic Python; this is the
one step that's genuinely a writing task (assembling a citable narrative
from typed findings and a decision record), which is why it's the one place
an LLM call belongs.
"""

import json
from typing import Optional

from langchain_openai import ChatOpenAI

from .prompts import AUDIT_TRAIL_SYSTEM
from .schema import ActionResult, ControlException

_MODEL = "gpt-4.1-nano"


def audit_trail_synthesizer(
    exceptions: list[ControlException],
    gated_exception: Optional[ControlException],
    gate_result: Optional[ActionResult],
) -> str:
    llm = ChatOpenAI(model=_MODEL, temperature=0)
    payload = {
        "exceptions": [e.model_dump() for e in exceptions],
        "gated_exception": gated_exception.model_dump() if gated_exception else None,
        "gate_result": gate_result.model_dump() if gate_result else None,
    }
    response = llm.invoke([AUDIT_TRAIL_SYSTEM, ("human", json.dumps(payload))])
    return response.content
