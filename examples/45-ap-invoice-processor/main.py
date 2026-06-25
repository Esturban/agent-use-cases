"""AP Invoice Processor — runnable entry point with 4 invoice scenarios."""

from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

# Scenario 1: Clean match — ACME-001 cloud servers
INVOICE_1 = """
ACME Tech Supplies
Vendor ID: ACME-001
Invoice Number: INV-ACME-2025-0892
Invoice Date: 2025-06-15
PO Reference: PO-2025-001

Line Items:
  1. Cloud Server Model X500 — Qty: 4 — Unit Price: $2,100.00 — Total: $8,400.00

Invoice Total: $8,400.00 USD
"""

# Scenario 2: Quantity short — BETA-002 office furniture (GR shows 85 of 100 received)
INVOICE_2 = """
Beta Office Solutions
Vendor ID: BETA-002
Invoice Number: INV-BETA-2025-0441
Invoice Date: 2025-06-18
PO Reference: PO-2025-002

Line Items:
  1. Ergonomic Office Chair — Qty: 100 — Unit Price: $150.00 — Total: $15,000.00

Invoice Total: $15,000.00 USD
"""

# Scenario 3: Price variance — GAMMA-003 consulting (invoiced $421.25/hr vs PO $375/hr)
INVOICE_3 = """
Gamma Advisory Group
Vendor ID: GAMMA-003
Invoice Number: INV-GAMMA-2025-0318
Invoice Date: 2025-06-20
PO Reference: PO-2025-003

Line Items:
  1. Management Consulting Services — Qty: 75 hours — Unit Price: $421.25 — Total: $31,593.75

Invoice Total: $31,593.75 USD
"""

# Scenario 4: Missing goods receipt — DELTA-004 software licences (no GR on record)
INVOICE_4 = """
Delta Software Ltd
Vendor ID: DELTA-004
Invoice Number: INV-DELTA-2025-0157
Invoice Date: 2025-06-22
PO Reference: PO-2025-004

Line Items:
  1. Enterprise Software Licence (annual seat) — Qty: 50 — Unit Price: $440.00 — Total: $22,000.00

Invoice Total: $22,000.00 USD
"""

SCENARIOS = [
    ("Clean match — auto approve", INVOICE_1),
    ("Quantity short — line manager review", INVOICE_2),
    ("Price variance — finance controller", INVOICE_3),
    ("Missing GR — finance controller", INVOICE_4),
]


def print_result(label: str, result: dict) -> None:
    """Pretty-print a match result to stdout."""
    inv = result["invoice"]
    mr = result["match_result"]
    print(f"\n{'=' * 60}")
    print(f"Scenario : {label}")
    print(f"Vendor   : {inv.vendor_id}")
    print(f"Invoice# : {inv.invoice_number}")
    print(f"Total    : {inv.currency} {inv.total_amount:,.2f}")
    print(f"Status   : {mr.match_status.upper()}")
    if mr.discrepancies:
        print("Discrepancies:")
        for d in mr.discrepancies:
            variance = f"  ({d.variance_pct:.1f}%)" if d.variance_pct is not None else ""
            print(
                f"  [{d.severity.upper()}] {d.discrepancy_type} | {d.field} | "
                f"invoice={d.invoice_value} expected={d.expected_value}{variance}"
            )
    print(f"Approval : {mr.approval_tier.upper()}")
    print(f"Rationale: {mr.approval_rationale}")


def main() -> None:
    """Run all 4 invoice scenarios through the 3-way match pipeline."""
    for label, invoice_text in SCENARIOS:
        result = run(invoice_text)
        print_result(label, result)


if __name__ == "__main__":
    main()
