"""Entry point -- runs two period-close cycles through the ledger-integrity supervisor.

Scenario 1 has a deliberate cross-domain correlation: 'jsmith' prepares an
imbalanced JV entry to 'Quantum Wire Transfers', holds both AP-create and
AP-approve (a segregation-of-duties conflict), and 'Quantum Wire Transfers'
is also the counterparty on an unmatched, fraud-flagged bank transaction --
three findings that should read as one connected issue, not three unrelated
exceptions. It also produces a P0 finding above the materiality threshold,
so it exercises the full path through human_review/resolve_gate.

Scenario 2 is a clean close: every entry balances, every bank transaction
matches, no SoD conflicts -- so no exception requires approval and the graph
never pauses.
"""

import os

from dotenv import load_dotenv

from src.schema import (
    ApprovalDecision,
    BankTransaction,
    FixedAsset,
    GLCashEntry,
    JournalEntry,
    JournalLine,
    PaymentTransaction,
    SoDRoleGrant,
)
from src.workflow import propose, resume

load_dotenv()

MATERIALITY_THRESHOLD = 10_000.0


def _correlated_close_cycle() -> dict:
    journal_entries = [
        JournalEntry(
            entry_id="JE-4471",
            description="Manual accrual reversal for Q2 consulting fees",
            counterparty="Quantum Wire Transfers",
            lines=[
                JournalLine(side="debit", account_code="6100", amount=18500.0, prepared_by="jsmith"),
                JournalLine(side="credit", account_code="2100", amount=12500.0, prepared_by="jsmith"),
            ],
        ),
        JournalEntry(
            entry_id="JE-4472",
            description="Routine monthly rent accrual",
            counterparty="Meridian Properties",
            lines=[
                JournalLine(side="debit", account_code="6200", amount=4200.0, prepared_by="apark"),
                JournalLine(side="credit", account_code="2110", amount=4200.0, prepared_by="apark"),
            ],
        ),
    ]
    bank_transactions = [
        BankTransaction(txn_id="BT-001", date="2026-06-28", amount=-4200.0, counterparty="Meridian Properties"),
        BankTransaction(
            txn_id="BT-002", date="2026-06-29", amount=-22750.0, counterparty="Quantum Wire Transfers"
        ),
    ]
    gl_entries = [
        GLCashEntry(entry_id="GL-9001", date="2026-06-28", amount=-4200.0, reference="JE-4472"),
    ]
    fixed_assets = [
        FixedAsset(asset_id="FA-201", cost=50000.0, accumulated_depreciation=48000.0, useful_life_years=5),
        FixedAsset(
            asset_id="FA-202",
            cost=12000.0,
            accumulated_depreciation=13500.0,
            useful_life_years=3,
        ),
    ]
    payment_transactions = [
        PaymentTransaction(txn_id="PT-01", date="2026-06-25", payee="Acme Supplies", amount=8000.0),
        PaymentTransaction(txn_id="PT-02", date="2026-06-25", payee="Acme Supplies", amount=8000.0),
        PaymentTransaction(txn_id="PT-03", date="2026-06-26", payee="Acme Supplies", amount=8000.0),
        PaymentTransaction(
            txn_id="PT-04",
            date="2026-06-27",
            payee="Nova Consulting LLC",
            amount=15000.0,
            is_new_payee=True,
        ),
    ]
    sod_role_grants = [
        SoDRoleGrant(identity="jsmith", role="AP-create"),
        SoDRoleGrant(identity="jsmith", role="AP-approve"),
        SoDRoleGrant(identity="apark", role="AP-create"),
    ]
    return {
        "period": "2026-06",
        "materiality_threshold": MATERIALITY_THRESHOLD,
        "journal_entries": [e.model_dump() for e in journal_entries],
        "bank_transactions": [t.model_dump() for t in bank_transactions],
        "gl_entries": [g.model_dump() for g in gl_entries],
        "fixed_assets": [a.model_dump() for a in fixed_assets],
        "payment_transactions": [p.model_dump() for p in payment_transactions],
        "sod_role_grants": [r.model_dump() for r in sod_role_grants],
    }


def _clean_close_cycle() -> dict:
    journal_entries = [
        JournalEntry(
            entry_id="JE-5001",
            description="Monthly insurance accrual",
            counterparty="Harbor Insurance Co",
            lines=[
                JournalLine(side="debit", account_code="6300", amount=2100.0, prepared_by="tlee"),
                JournalLine(side="credit", account_code="2120", amount=2100.0, prepared_by="tlee"),
            ],
        ),
    ]
    bank_transactions = [
        BankTransaction(txn_id="BT-101", date="2026-06-30", amount=-2100.0, counterparty="Harbor Insurance Co"),
    ]
    gl_entries = [
        GLCashEntry(entry_id="GL-9101", date="2026-06-30", amount=-2100.0, reference="JE-5001"),
    ]
    fixed_assets = [
        FixedAsset(asset_id="FA-301", cost=30000.0, accumulated_depreciation=9000.0, useful_life_years=10),
    ]
    payment_transactions = [
        PaymentTransaction(txn_id="PT-101", date="2026-06-29", payee="Office Supplies Co", amount=450.0),
    ]
    sod_role_grants = [
        SoDRoleGrant(identity="tlee", role="AP-create"),
    ]
    return {
        "period": "2026-06",
        "materiality_threshold": MATERIALITY_THRESHOLD,
        "journal_entries": [e.model_dump() for e in journal_entries],
        "bank_transactions": [t.model_dump() for t in bank_transactions],
        "gl_entries": [g.model_dump() for g in gl_entries],
        "fixed_assets": [a.model_dump() for a in fixed_assets],
        "payment_transactions": [p.model_dump() for p in payment_transactions],
        "sod_role_grants": [r.model_dump() for r in sod_role_grants],
    }


def main():
    scenarios = [
        ("CORRELATED -- P0 finding across 3 domains", _correlated_close_cycle()),
        ("CLEAN CLOSE -- nothing crosses materiality", _clean_close_cycle()),
    ]

    for label, close_data in scenarios:
        print(f"\n{'=' * 70}\nScenario: {label}\n{'=' * 70}")
        result = propose(close_data)

        if result["status"] == "paused":
            exc = result["exception"]
            proposed = result["proposed_action"]
            print("\n-- paused at human_review --")
            print(f"Gated exception domain : {exc.domain}")
            print(f"Financial exposure     : ${exc.financial_exposure:,.2f}")
            print(f"Description            : {exc.description}")
            print(f"Proposed action        : {proposed.action_type} -- {proposed.summary}")

            decision = ApprovalDecision(
                decision="approve",
                rationale="Confirmed with controller; escalating to investigations immediately.",
            )
            resumed = resume(result["thread_id"], decision)
            print("\n-- resumed with controller decision --")
            print(f"Executed  : {resumed['gate_result'].executed}")
            print(f"Audit log : {resumed['gate_result'].decision_log}")
            register = resumed["register"]
        else:
            register = result["register"]

        print("\n-- ControlsExceptionRegister --")
        print(f"Close status    : {register.close_status}")
        print(f"Total exposure  : ${register.total_exposure:,.2f}")
        print(f"Correlations    : {register.cross_domain_correlations}")
        for exc in register.exceptions:
            print(f"  [{exc.severity}] {exc.domain}: {exc.description}")
        print(f"\nAudit narrative:\n{register.audit_narrative}")


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set -- copy .env.example to .env")
    main()
