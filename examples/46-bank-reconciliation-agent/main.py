"""Bank Reconciliation Agent — runnable entry point.

Two scenarios are executed:
  Scenario 1 — Standard June 2025 month-end close (12 bank txns, 11 GL entries)
  Scenario 2 — Suspicious transactions with potential fraud indicator
"""

from src.workflow import run


# ---------------------------------------------------------------------------
# Scenario 1 — Standard June 2025 month-end close
# ---------------------------------------------------------------------------

BANK_TXNS_S1 = [
    # 9 items that will exact-match GL entries
    {"txn_id": "B01", "date": "2025-06-02", "description": "Customer payment – Invoice 1041", "debit": 0.0, "credit": 5200.00},
    {"txn_id": "B02", "date": "2025-06-04", "description": "Supplier payment – PO-8821", "debit": 3100.00, "credit": 0.0},
    {"txn_id": "B03", "date": "2025-06-07", "description": "Customer payment – Invoice 1042", "debit": 0.0, "credit": 8750.00},
    {"txn_id": "B04", "date": "2025-06-10", "description": "Payroll run June W1", "debit": 12400.00, "credit": 0.0},
    {"txn_id": "B05", "date": "2025-06-12", "description": "Customer payment – Invoice 1043", "debit": 0.0, "credit": 4620.00},
    {"txn_id": "B06", "date": "2025-06-14", "description": "Rent payment June", "debit": 3500.00, "credit": 0.0},
    {"txn_id": "B07", "date": "2025-06-18", "description": "Customer payment – Invoice 1044", "debit": 0.0, "credit": 6930.00},
    {"txn_id": "B08", "date": "2025-06-21", "description": "Utilities payment", "debit": 820.00, "credit": 0.0},
    {"txn_id": "B09", "date": "2025-06-25", "description": "Customer payment – Invoice 1045", "debit": 0.0, "credit": 2980.00},
    # Timing difference — deposit in transit (bank has it, GL does not yet)
    {"txn_id": "B10", "date": "2025-06-30", "description": "Customer payment – Invoice 1046 (deposit in transit)", "debit": 0.0, "credit": 1250.00},
    # Bank charge — service fee
    {"txn_id": "B11", "date": "2025-06-30", "description": "Monthly account service fee", "debit": 18.50, "credit": 0.0},
    # Probable match (GL date 2025-06-27, bank 2025-06-28 — 1 day diff)
    {"txn_id": "B12", "date": "2025-06-28", "description": "Supplier payment – PO-8830", "debit": 7680.00, "credit": 0.0},
]

GL_ENTRIES_S1 = [
    # 9 exact-match counterparts
    {"entry_id": "GL01", "date": "2025-06-02", "reference": "JE-2001", "amount": 5200.00, "description": "AR receipt Invoice 1041"},
    {"entry_id": "GL02", "date": "2025-06-04", "reference": "JE-2002", "amount": -3100.00, "description": "AP payment PO-8821"},
    {"entry_id": "GL03", "date": "2025-06-07", "reference": "JE-2003", "amount": 8750.00, "description": "AR receipt Invoice 1042"},
    {"entry_id": "GL04", "date": "2025-06-10", "reference": "JE-2004", "amount": -12400.00, "description": "Payroll June W1"},
    {"entry_id": "GL05", "date": "2025-06-12", "reference": "JE-2005", "amount": 4620.00, "description": "AR receipt Invoice 1043"},
    {"entry_id": "GL06", "date": "2025-06-14", "reference": "JE-2006", "amount": -3500.00, "description": "Rent June"},
    {"entry_id": "GL07", "date": "2025-06-18", "reference": "JE-2007", "amount": 6930.00, "description": "AR receipt Invoice 1044"},
    {"entry_id": "GL08", "date": "2025-06-21", "reference": "JE-2008", "amount": -820.00, "description": "Utilities June"},
    {"entry_id": "GL09", "date": "2025-06-25", "reference": "JE-2009", "amount": 2980.00, "description": "AR receipt Invoice 1045"},
    # Probable-match counterpart (GL date differs by 1 day from bank B12)
    {"entry_id": "GL10", "date": "2025-06-27", "reference": "JE-2010", "amount": -7680.00, "description": "AP payment PO-8830"},
    # GL accrual reversal — GL has it, bank does not
    {"entry_id": "GL11", "date": "2025-06-30", "reference": "JE-2011", "amount": -482.00, "description": "Accrual reversal – prepaid insurance"},
]

# ---------------------------------------------------------------------------
# Scenario 2 — Suspicious activity with potential fraud indicator
# ---------------------------------------------------------------------------

BANK_TXNS_S2 = [
    # 5 exact matches
    {"txn_id": "B21", "date": "2025-07-03", "description": "Customer payment – Invoice 2001", "debit": 0.0, "credit": 9400.00},
    {"txn_id": "B22", "date": "2025-07-07", "description": "Supplier payment – PO-9001", "debit": 4200.00, "credit": 0.0},
    {"txn_id": "B23", "date": "2025-07-10", "description": "Customer payment – Invoice 2002", "debit": 0.0, "credit": 5680.00},
    {"txn_id": "B24", "date": "2025-07-14", "description": "Payroll run July W2", "debit": 11300.00, "credit": 0.0},
    {"txn_id": "B25", "date": "2025-07-18", "description": "Customer payment – Invoice 2003", "debit": 0.0, "credit": 3150.00},
    # Fraud indicator — round-number withdrawal, no GL counterpart
    {"txn_id": "B26", "date": "2025-07-21", "description": "Wire transfer OUT – ref UNKNOWN", "debit": 10000.00, "credit": 0.0},
    # Duplicate credit — same amount and date as B23
    {"txn_id": "B27", "date": "2025-07-10", "description": "Customer payment – Invoice 2002 (DUPLICATE)", "debit": 0.0, "credit": 5680.00},
    # Bank charge
    {"txn_id": "B28", "date": "2025-07-31", "description": "Wire transfer fee", "debit": 25.00, "credit": 0.0},
]

GL_ENTRIES_S2 = [
    # 5 exact-match counterparts
    {"entry_id": "GL21", "date": "2025-07-03", "reference": "JE-3001", "amount": 9400.00, "description": "AR receipt Invoice 2001"},
    {"entry_id": "GL22", "date": "2025-07-07", "reference": "JE-3002", "amount": -4200.00, "description": "AP payment PO-9001"},
    {"entry_id": "GL23", "date": "2025-07-10", "reference": "JE-3003", "amount": 5680.00, "description": "AR receipt Invoice 2002"},
    {"entry_id": "GL24", "date": "2025-07-14", "reference": "JE-3004", "amount": -11300.00, "description": "Payroll July W2"},
    {"entry_id": "GL25", "date": "2025-07-18", "reference": "JE-3005", "amount": 3150.00, "description": "AR receipt Invoice 2003"},
    # Missing booking — GL entry booked but no bank counterpart
    {"entry_id": "GL26", "date": "2025-07-22", "reference": "JE-3006", "amount": -1875.00, "description": "Legal retainer payment"},
    # Two more GL entries that will not match anything
    {"entry_id": "GL27", "date": "2025-07-28", "reference": "JE-3007", "amount": 620.00, "description": "Miscellaneous credit correction"},
    {"entry_id": "GL28", "date": "2025-07-31", "reference": "JE-3008", "amount": -340.00, "description": "Subscription renewal"},
]


def print_summary(summary) -> None:
    """Print a formatted reconciliation summary to stdout."""
    print(f"\n{'=' * 60}")
    print(f"  BANK RECONCILIATION — {summary.period}")
    print(f"{'=' * 60}")
    print(f"  Bank closing balance : {summary.bank_closing_balance:>12,.2f}")
    print(f"  GL cash balance      : {summary.gl_cash_balance:>12,.2f}")

    exact = sum(1 for p in summary.matched_pairs if p.match_confidence == "exact")
    probable = sum(1 for p in summary.matched_pairs if p.match_confidence == "probable")
    fuzzy = sum(1 for p in summary.matched_pairs if p.match_confidence == "fuzzy")
    print(f"\n  Matched pairs        : {len(summary.matched_pairs)}")
    print(f"    Exact              : {exact}")
    print(f"    Probable           : {probable}")
    print(f"    Fuzzy              : {fuzzy}")
    print(f"  Reconciling value    : {summary.reconciling_items_value:>12,.2f}")

    if summary.unmatched_items:
        print(f"\n  Unmatched items ({len(summary.unmatched_items)}):")
        for item in summary.unmatched_items:
            print(
                f"    [{item.item_id}] source={item.source} "
                f"amount={item.amount:,.2f} "
                f"type={item.exception_type}"
            )
            print(f"      Action: {item.recommended_action}")

    status = "RECONCILED" if summary.is_reconciled else "NOT RECONCILED"
    print(f"\n  Status : {status}")
    print(f"  Note   : {summary.reconciliation_note}")
    print()


if __name__ == "__main__":
    print("\n>>> Scenario 1 — Standard June 2025 month-end close")
    summary_1 = run(
        bank_txns=BANK_TXNS_S1,
        gl_entries=GL_ENTRIES_S1,
        period="June 2025",
        bank_closing_balance=42350.00,
        gl_cash_balance=41100.00,
    )
    print_summary(summary_1)

    print("\n>>> Scenario 2 — Suspicious activity (July 2025)")
    summary_2 = run(
        bank_txns=BANK_TXNS_S2,
        gl_entries=GL_ENTRIES_S2,
        period="July 2025",
        bank_closing_balance=7905.00,
        gl_cash_balance=6265.00,
    )
    print_summary(summary_2)
