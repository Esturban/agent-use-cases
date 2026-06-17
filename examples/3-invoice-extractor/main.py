from dotenv import load_dotenv

from src.workflow import create_workflow

load_dotenv()

INVOICES = [
    (
        "Standard SaaS invoice",
        """INVOICE #INV-2024-0892
Vendor: CloudPeak Software Ltd
Date: 2024-05-15

Line Items:
  Annual SaaS License (5 seats)    x1   $2,400.00
  Premium Support Package           x1     $600.00
  Onboarding & Setup                x3     $150.00  =  $450.00

Subtotal:  $3,450.00
Tax (15%):   $517.50
TOTAL DUE: $3,967.50

Payment due within 30 days.""",
    ),
    (
        "Consulting services",
        """TAX INVOICE
From: Apex Cloud Consulting
Invoice No: APC-2024-112  |  Date: 15 June 2024

Services rendered:
  System Architecture Review    1 day    @ $3,500/day     $3,500
  Implementation Support        3 days   @ $2,200/day     $6,600
  Documentation                 0.5 day  @ $1,800/day       $900

Subtotal ........................ $11,000.00
GST (10%) ....................... $1,100.00
TOTAL ........................... $12,100.00""",
    ),
    (
        "Freelance / minimal",
        """Invoice
From: Maya Osei Design Studio
To: Bright Horizon Media

Invoice #: 0047
Date: 2024-09-03

1x Brand Identity Package      $4,800.00
1x Revision Round (2 hrs)        $300.00

Total: $5,100.00
Payment within 14 days via bank transfer.""",
    ),
]


def _print_invoice(label: str, invoice) -> None:
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    print(f"  Vendor:   {invoice.vendor}")
    print(f"  Invoice#: {invoice.invoice_number}")
    print(f"  Date:     {invoice.date}")
    print(f"  Total:    ${invoice.total_amount:,.2f}")
    print(f"  Lines ({len(invoice.line_items)}):")
    for item in invoice.line_items:
        print(f"    - {item.description}: {item.quantity} x ${item.unit_price} = ${item.total}")


def main():
    extractor = create_workflow()
    for label, text in INVOICES:
        invoice = extractor.invoke(text)
        _print_invoice(label, invoice)


if __name__ == "__main__":
    main()
