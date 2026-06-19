"""
Demonstrates the customer lifecycle state machine with three customers
at different stages, each receiving one incoming signal.

  Customer A — lead who just submitted a form → qualification agent runs
  Customer B — at-risk customer with low NPS + ticket spike → churn response agent runs
  Customer C — renewal-stage customer with contract expiring in 30 days → renewal agent runs
"""
import json

from dotenv import load_dotenv

from src.schema import CustomerRecord, CustomerSignal
from src.workflow import run

load_dotenv()


def _print_result(label: str, result) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    print(f"  Customer : {result.customer_id}")
    print(f"  Stage    : {result.previous_stage}  ->  ", end="")
    if result.transition_occurred:
        print(result.stage_output.next_stage)
    else:
        print(f"{result.previous_stage} (no change)")
    print(f"  Transition: {result.transition_occurred}")
    print("\n  Stage output (summary):")
    for k, v in result.stage_output.output.items():
        display = str(v)
        if len(display) > 120:
            display = display[:117] + "..."
        print(f"    {k}: {display}")
    print()


def main() -> None:
    # ------------------------------------------------------------------
    # Customer A — lead, just submitted an inbound form
    # ------------------------------------------------------------------
    customer_a = CustomerRecord(
        customer_id="CUS-001",
        company_name="Flowstate Analytics",
        stage="lead",
        health_score=0.5,
        arr_usd=0.0,
        days_since_last_active=0,
        open_tickets=0,
        nps_score=None,
        notes=["Inbound demo request from CFO via website form."],
        signals=[],
    )
    signal_a = CustomerSignal(
        signal_type="form_submit",
        value=(
            "Demo request: 'We need to automate our compliance reporting"
            " -- current process is 100% manual.'"
        ),
        timestamp="2026-06-19T08:15:00Z",
    )

    result_a = run(customer_a, signal_a)
    _print_result("Customer A -- Lead Qualification", result_a)

    # ------------------------------------------------------------------
    # Customer B — at-risk, low NPS + ticket spike
    # ------------------------------------------------------------------
    customer_b = CustomerRecord(
        customer_id="CUS-002",
        company_name="Meridian Logistics",
        stage="at_risk",
        health_score=0.31,
        arr_usd=84000.0,
        days_since_last_active=18,
        open_tickets=6,
        nps_score=3,
        notes=[
            "Health dropped after Q1 migration -- data sync issues.",
            "CSM flagged account for executive attention on 2026-05-10.",
        ],
        signals=[
            CustomerSignal(
                signal_type="support_ticket",
                value="TKT-4421: Bulk export broken since 2.1 upgrade",
                timestamp="2026-06-01T11:00:00Z",
            ),
            CustomerSignal(
                signal_type="support_ticket",
                value="TKT-4502: Dashboard loading errors -- 504 timeouts",
                timestamp="2026-06-10T14:30:00Z",
            ),
        ],
    )
    signal_b = CustomerSignal(
        signal_type="churn_indicator",
        value="Customer emailed: 'We are evaluating alternatives and may not renew in August.'",
        timestamp="2026-06-19T09:00:00Z",
    )

    result_b = run(customer_b, signal_b)
    _print_result("Customer B -- At-Risk Churn Response", result_b)

    # ------------------------------------------------------------------
    # Customer C — renewal stage, contract expiring in 30 days
    # ------------------------------------------------------------------
    customer_c = CustomerRecord(
        customer_id="CUS-003",
        company_name="Vantage Capital Partners",
        stage="renewal",
        health_score=0.78,
        arr_usd=240000.0,
        days_since_last_active=2,
        open_tickets=1,
        nps_score=8,
        notes=[
            "Strong adoption across 4 business units.",
            "Champion (VP Ops) promoted to COO -- new contact needs warm handoff.",
        ],
        signals=[
            CustomerSignal(
                signal_type="login_activity",
                value="42 active users in the last 30 days",
                timestamp="2026-06-15T00:00:00Z",
            ),
        ],
    )
    signal_c = CustomerSignal(
        signal_type="contract_expiry",
        value="Contract ends 2026-07-19 -- 30 days remaining. Current ACV: $240,000.",
        timestamp="2026-06-19T10:00:00Z",
    )

    result_c = run(customer_c, signal_c)
    _print_result("Customer C -- Renewal Package", result_c)

    # ------------------------------------------------------------------
    # Full JSON dump for inspection
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Full OrchestratorResult JSON")
    print("=" * 60)
    all_results = [result_a, result_b, result_c]
    print(json.dumps([r.model_dump() for r in all_results], indent=2))


if __name__ == "__main__":
    main()
