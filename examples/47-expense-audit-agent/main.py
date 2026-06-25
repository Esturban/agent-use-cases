"""Entry point for the Expense Audit Agent.

Runs three expense reports:
  Report 1 (EXP-2025-001) — Alice Chen: clean report, auto_approve
  Report 2 (EXP-2025-002) — Bob Kumar: mixed violations, finance_director
  Report 3 (EXP-2025-003) — Carol Davis: missing receipts, rejected
"""

from src.schema import ExpenseLine
from src.workflow import run


def print_result(result) -> None:
    """Pretty-print an AuditResult to stdout."""
    print(f"\n{'=' * 60}")
    print(f"Report:   {result.report_id}")
    print(f"Employee: {result.employee_name}")
    print(f"Total:    ${result.total_claimed:,.2f}")
    print(f"Tier:     {result.approval_tier.upper()}")
    print(f"Lines:    {result.compliant_lines} compliant, {result.violation_lines} violation(s)")
    if result.violations:
        print("\nViolations:")
        for v in result.violations:
            print(f"  [{v.severity.upper():5}] {v.rule_id} — {v.violation_detail}")
    else:
        print("\nNo policy violations found.")
    print(f"\nSummary: {result.audit_summary}")


def main() -> None:
    # ------------------------------------------------------------------
    # Report 1: Alice Chen — clean report, should auto_approve
    # ------------------------------------------------------------------
    alice_lines = [
        ExpenseLine(
            line_id="L01",
            date="2025-06-10",
            category="transport",
            amount=380.00,
            city="NYC",
            description="Economy flight NYC return",
            receipt_attached=True,
            pre_approved=True,
            class_of_travel="economy",
        ),
        ExpenseLine(
            line_id="L02",
            date="2025-06-11",
            category="accommodation",
            amount=320.00,
            city="NYC",
            description="Hotel stay NYC — 1 night",
            receipt_attached=True,
        ),
        ExpenseLine(
            line_id="L03",
            date="2025-06-11",
            category="meals",
            amount=95.00,
            city="NYC",
            description="Team working lunch",
            receipt_attached=True,
        ),
        ExpenseLine(
            line_id="L04",
            date="2025-06-11",
            category="transport",
            amount=35.00,
            city="NYC",
            description="Taxi to client office",
            receipt_attached=True,
            class_of_travel=None,
        ),
    ]
    result1 = run(
        report_id="EXP-2025-001",
        employee_name="Alice Chen",
        lines=alice_lines,
    )
    print_result(result1)

    # ------------------------------------------------------------------
    # Report 2: Bob Kumar — multiple violations, finance_director
    # ------------------------------------------------------------------
    bob_lines = [
        ExpenseLine(
            line_id="L01",
            date="2025-06-05",
            category="transport",
            amount=3200.00,
            city="NYC",
            description="Business class flight to NYC",
            receipt_attached=True,
            pre_approved=False,
            class_of_travel="business",
        ),
        ExpenseLine(
            line_id="L02",
            date="2025-06-06",
            category="accommodation",
            amount=420.00,
            city="NYC",
            description="Hotel NYC — above policy limit",
            receipt_attached=True,
        ),
        ExpenseLine(
            line_id="L03",
            date="2025-06-06",
            category="meals",
            amount=150.00,
            city="NYC",
            description="Client dinner meals — over limit",
            receipt_attached=True,
        ),
        ExpenseLine(
            line_id="L04",
            date="2025-06-07",
            category="entertainment",
            amount=280.00,
            city="NYC",
            description="Client entertainment event",
            receipt_attached=True,
        ),
        ExpenseLine(
            line_id="L05",
            date="2025-06-08",
            category="equipment",
            amount=620.00,
            city="NYC",
            description="Laptop for home office",
            receipt_attached=True,
        ),
    ]
    result2 = run(
        report_id="EXP-2025-002",
        employee_name="Bob Kumar",
        lines=bob_lines,
    )
    print_result(result2)

    # ------------------------------------------------------------------
    # Report 3: Carol Davis — missing receipts, rejected
    # ------------------------------------------------------------------
    carol_lines = [
        ExpenseLine(
            line_id="L01",
            date="2025-06-15",
            category="meals",
            amount=75.00,
            city="SF",
            description="Working lunch — receipt lost",
            receipt_attached=False,
        ),
        ExpenseLine(
            line_id="L02",
            date="2025-06-15",
            category="transport",
            amount=45.00,
            city="SF",
            description="Taxi to airport — no receipt",
            receipt_attached=False,
            class_of_travel=None,
        ),
        ExpenseLine(
            line_id="L03",
            date="2025-06-16",
            category="accommodation",
            amount=340.00,
            city="SF",
            description="Hotel SF — 1 night, receipt attached",
            receipt_attached=True,
        ),
    ]
    result3 = run(
        report_id="EXP-2025-003",
        employee_name="Carol Davis",
        lines=carol_lines,
    )
    print_result(result3)

    print(f"\n{'=' * 60}")
    print("Audit run complete.")


if __name__ == "__main__":
    main()
