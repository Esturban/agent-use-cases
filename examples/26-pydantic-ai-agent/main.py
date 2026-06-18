from dotenv import load_dotenv

from src.workflow import extract

load_dotenv()

INVOICES = [
    (
        "SaaS subscription",
        """INVOICE
Vendor: Acme Software Inc.
Invoice #: INV-2024-0891
Date: 2024-11-01
Due: 2024-11-30
Currency: USD

Line Items:
  - Professional Plan (monthly)   1 x $299.00   $299.00
  - Additional seats (5)          5 x $49.00    $245.00

Subtotal: $544.00
Tax (8%): $43.52
TOTAL DUE: $587.52""",
    ),
    (
        "Consulting services",
        """Invoice
From: Meridian Consulting Group
Invoice Number: MCG-2025-0042
Invoice Date: January 15, 2025
Payment Due: February 14, 2025
Currency: EUR

Services Rendered:
1. Strategy workshop facilitation  2 days  @ EUR 2,500/day  EUR 5,000.00
2. Market analysis report          1 item  @ EUR 3,200.00   EUR 3,200.00
3. Follow-up advisory calls        4 hrs   @ EUR 350/hr     EUR 1,400.00

Sub-total: EUR 9,600.00
VAT (20%): EUR 1,920.00
Total payable: EUR 11,520.00""",
    ),
]


def main() -> None:
    for label, text in INVOICES:
        print(f"=== {label} ===")
        invoice = extract(text)
        print(f"  Vendor:   {invoice.vendor}")
        print(f"  Invoice#: {invoice.invoice_number}")
        print(f"  Date:     {invoice.invoice_date}  Due: {invoice.due_date}")
        print(f"  Currency: {invoice.currency}")
        print(f"  Total:    {invoice.total_due} (subtotal {invoice.subtotal} + tax {invoice.tax})")
        print(f"  Lines ({len(invoice.line_items)}):")
        for item in invoice.line_items:
            print(f"    - {item.description}: {item.quantity} x {item.unit_price} = {item.total}")
        print()


if __name__ == "__main__":
    main()
