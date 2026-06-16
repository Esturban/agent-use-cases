from dotenv import load_dotenv

from src.workflow import create_workflow

load_dotenv()

SAMPLE_INVOICE = """
INVOICE #INV-2024-0892
Vendor: CloudPeak Software Ltd
Date: 2024-05-15

Line Items:
  Annual SaaS License (5 seats)    x1   $2,400.00
  Premium Support Package           x1     $600.00
  Onboarding & Setup                x3     $150.00  =  $450.00

Subtotal:  $3,450.00
Tax (15%):   $517.50
TOTAL DUE: $3,967.50

Payment due within 30 days.
"""


def main():
    extractor = create_workflow()
    invoice = extractor.invoke(SAMPLE_INVOICE)

    print(f"Vendor:   {invoice.vendor}")
    print(f"Invoice#: {invoice.invoice_number}")
    print(f"Date:     {invoice.date}")
    print(f"Total:    ${invoice.total_amount:,.2f}")
    print(f"\nLine items ({len(invoice.line_items)}):")
    for item in invoice.line_items:
        print(f"  - {item.description}: {item.quantity} x ${item.unit_price} = ${item.total}")


if __name__ == "__main__":
    main()
