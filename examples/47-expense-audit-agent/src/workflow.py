"""Workflow entrypoint for the Expense Audit Agent.

Uses LangChain with structured output (gpt-4.1-nano via langchain-openai).
Policy limits are injected as context into the user message so the LLM
evaluates each line against the exact configured thresholds.
Approval routing is deterministic and applied after the LLM audit completes.
"""

import json
import os
from typing import List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from .prompts import AUDITOR_PROMPT
from .schema import AuditResult, ExpenseLine, PolicyViolation
from .tools import (
    POLICY,
    get_accommodation_limit,
    get_meal_limit,
)

load_dotenv()


def _build_policy_context(lines: List[ExpenseLine]) -> str:
    """Build a formatted policy context string for each expense line.

    Returns a JSON-serialisable block listing each line's applicable limits
    so the LLM can evaluate without needing to know the POLICY structure.
    """
    per_line = []
    for line in lines:
        limits: dict = {}
        if line.category == "meals":
            limits["daily_meal_limit"] = get_meal_limit(line.city)
        elif line.category == "accommodation":
            limits["nightly_accommodation_limit"] = get_accommodation_limit(line.city)
        elif line.category == "entertainment":
            limits["entertainment_limit"] = POLICY["entertainment_limit"]
        elif line.category == "equipment":
            limits["equipment_limit"] = POLICY["equipment_limit"]
        elif line.category == "transport":
            limits["requires_pre_approval_classes"] = POLICY["transport"]["requires_pre_approval"]
        limits["receipt_threshold"] = POLICY["receipt_threshold"]
        per_line.append(
            {
                "line": line.model_dump(),
                "applicable_limits": limits,
            }
        )
    return json.dumps(per_line, indent=2)


def _determine_approval_tier(
    violations: List[PolicyViolation],
    total_claimed: float,
    lines: List[ExpenseLine],
) -> str:
    """Determine the approval routing tier from the audit result.

    Routing logic (deterministic):
    - No violations                          -> auto_approve
    - Only info/warn violations              -> line_manager
    - Any block + total < 5000              -> finance_director
    - Any block + total >= 5000             -> rejected
    - Missing receipt on claim > threshold  -> rejected
    """
    has_block = any(v.severity == "block" for v in violations)
    missing_receipt_above_threshold = any(
        not line.receipt_attached and line.amount > POLICY["receipt_threshold"]
        for line in lines
    )

    if not violations:
        return "auto_approve"
    if not has_block and not missing_receipt_above_threshold:
        return "line_manager"
    if has_block and total_claimed < 5000.0:
        return "finance_director"
    return "rejected"


def run(
    report_id: str,
    employee_name: str,
    lines: List[ExpenseLine],
    model: str = "gpt-4.1-nano",
) -> AuditResult:
    """Audit an expense report and return a fully populated AuditResult.

    Args:
        report_id: Unique identifier for the expense report.
        employee_name: Full name of the submitting employee.
        lines: List of ExpenseLine objects to audit.
        model: LangChain-compatible model identifier.

    Returns:
        AuditResult with violations, tier routing, and audit summary.
    """
    total_claimed = sum(line.amount for line in lines)
    policy_context = _build_policy_context(lines)

    user_message = (
        f"Expense report: {report_id}\n"
        f"Employee: {employee_name}\n"
        f"Total claimed: {total_claimed:.2f}\n\n"
        f"Expense lines with applicable policy limits:\n"
        f"{policy_context}\n\n"
        f"Approval routing rules:\n"
        f"  - No violations -> auto_approve\n"
        f"  - info/warn only -> line_manager\n"
        f"  - any block + total < 5000 -> finance_director\n"
        f"  - any block + total >= 5000 OR missing receipt above {POLICY['receipt_threshold']} -> rejected\n\n"
        f"Return a complete AuditResult."
    )

    llm = ChatOpenAI(
        model=model,
        temperature=0,
        api_key=os.environ["OPENAI_API_KEY"],
    )
    auditor = AUDITOR_PROMPT | llm.with_structured_output(AuditResult)
    result: AuditResult = auditor.invoke({"messages": [{"role": "user", "content": user_message}]})

    approval_tier = _determine_approval_tier(result.violations, total_claimed, lines)
    line_ids_with_violations = {v.line_id for v in result.violations}
    violation_lines = len(line_ids_with_violations)
    compliant_lines = len(lines) - violation_lines

    return AuditResult(
        report_id=report_id,
        employee_name=employee_name,
        total_claimed=total_claimed,
        violations=result.violations,
        compliant_lines=compliant_lines,
        violation_lines=violation_lines,
        approval_tier=approval_tier,
        audit_summary=result.audit_summary,
    )
