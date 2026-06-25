"""Entry point for the AR Collection Agent.

Runs the aging-bucket state machine over 6 customers spanning all aging buckets
and escalation tiers. Prints a summary of the resulting collection plan.
"""

from src.schema import ARCustomer
from src.workflow import run

# ---------------------------------------------------------------------------
# Sample customers — one per aging bucket / escalation tier
# ---------------------------------------------------------------------------

CUSTOMERS = [
    # current -> no_action
    ARCustomer(
        customer_id="CUST-001",
        customer_name="Apex Corp",
        invoice_number="INV-2025-0441",
        invoice_date="2025-06-10",
        due_date="2025-06-24",
        outstanding_amount=8750.00,
        days_overdue=0,
        prior_contact_count=0,
        credit_limit=50000.00,
        total_exposure=8750.00,
    ),
    # 1_30 -> friendly_reminder
    ARCustomer(
        customer_id="CUST-002",
        customer_name="BrightPath Ltd",
        invoice_number="INV-2025-0388",
        invoice_date="2025-05-17",
        due_date="2025-06-06",
        outstanding_amount=12400.00,
        days_overdue=18,
        prior_contact_count=0,
        credit_limit=50000.00,
        total_exposure=12400.00,
    ),
    # 31_60 -> formal_notice
    ARCustomer(
        customer_id="CUST-003",
        customer_name="Coastal Trading",
        invoice_number="INV-2025-0312",
        invoice_date="2025-04-20",
        due_date="2025-05-10",
        outstanding_amount=31500.00,
        days_overdue=45,
        prior_contact_count=1,
        credit_limit=50000.00,
        total_exposure=31500.00,
    ),
    # 61_90 -> final_demand
    ARCustomer(
        customer_id="CUST-004",
        customer_name="Delta Enterprises",
        invoice_number="INV-2025-0244",
        invoice_date="2025-03-15",
        due_date="2025-04-14",
        outstanding_amount=22000.00,
        days_overdue=72,
        prior_contact_count=2,
        credit_limit=50000.00,
        total_exposure=22000.00,
    ),
    # 90_plus -> legal_referral + credit_hold (days > 90 AND exposure > 80% of limit)
    ARCustomer(
        customer_id="CUST-005",
        customer_name="Echo Systems",
        invoice_number="INV-2025-0180",
        invoice_date="2025-02-10",
        due_date="2025-03-12",
        outstanding_amount=85000.00,
        days_overdue=97,
        prior_contact_count=3,
        credit_limit=100000.00,
        total_exposure=120000.00,
    ),
    # 31_60 -> formal_notice (second account in this tier)
    ARCustomer(
        customer_id="CUST-006",
        customer_name="Frontier Corp",
        invoice_number="INV-2025-0201",
        invoice_date="2025-04-25",
        due_date="2025-05-20",
        outstanding_amount=4200.00,
        days_overdue=35,
        prior_contact_count=0,
        credit_limit=50000.00,
        total_exposure=4200.00,
    ),
]

AS_OF_DATE = "2025-06-24"


def main() -> None:
    """Run the AR collection agent and print the collection plan."""
    print("=" * 70)
    print("AR Collection Agent — Collection Plan")
    print(f"As of: {AS_OF_DATE}")
    print("=" * 70)

    plan = run(customers=CUSTOMERS, as_of_date=AS_OF_DATE)

    print("\nCustomer Actions (sorted by priority, high to low):\n")
    print(
        f"{'Customer':<22} {'Days OD':>8} {'Tier':<20} {'Score':>6} "
        f"{'Hold':>6} {'Amount':>12}"
    )
    print("-" * 80)

    for action in plan.actions:
        customer = next(c for c in CUSTOMERS if c.customer_id == action.customer_id)
        hold_flag = "YES" if action.credit_hold_recommended else "no"
        amount_str = f"${customer.outstanding_amount:,.2f}"
        print(
            f"{customer.customer_name:<22} {customer.days_overdue:>8} "
            f"{action.escalation_tier:<20} {action.priority_score:>6} "
            f"{hold_flag:>6} {amount_str:>12}"
        )

    print("\n" + "-" * 80)
    print("\nCollection Letters (first 200 chars):\n")
    for action in plan.actions:
        customer = next(c for c in CUSTOMERS if c.customer_id == action.customer_id)
        preview = action.collection_letter[:200].replace("\n", " ")
        print(f"[{action.escalation_tier}] {customer.customer_name}:")
        print(f"  {preview}...")
        print()

    print("=" * 70)
    print("Plan Totals")
    print("=" * 70)
    print(f"  Total AR outstanding : ${plan.total_ar_outstanding:,.2f}")
    print(f"  Credit holds          : {plan.credit_hold_count}")
    print(f"  Legal referrals       : {plan.legal_referral_count}")
    print(f"\nSummary:\n  {plan.collection_summary}")


if __name__ == "__main__":
    main()
