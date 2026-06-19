# 3-invoice-extractor

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/3-invoice-extractor/invoice_extractor_workbook.ipynb)


An agent that reads raw invoice text and returns a **fully structured Invoice object** --
vendor, date, every line item, subtotal, tax, and total.

**What this teaches:** Pydantic schemas as contracts. The model must populate
every field correctly or the call retries. A `field_validator` on `total_amount`
ensures the agent can never return a zero or negative total -- validation is
part of the agent's output contract, not an afterthought.

**Keys:** `OPENAI_API_KEY`

```bash
python examples/3-invoice-extractor/main.py
```

### How it works

```
invoice text  →  LLM + Invoice schema  →  validated Invoice object
                                          (retries if validation fails)
```

## What you'll see

```
==================================================
  Standard SaaS invoice
==================================================
  Vendor:   CloudPeak Software Ltd
  Invoice#: INV-2024-0892
  Date:     2024-05-15
  Total:    $3,967.50
  Lines (3):
    - Annual SaaS License (5 seats): 1 x $2400.0 = $2400.0
    - Premium Support Package: 1 x $600.0 = $600.0
    - Onboarding & Setup: 3 x $150.0 = $450.0

==================================================
  Consulting services
==================================================
  Vendor:   Apex Cloud Consulting
  Invoice#: APC-2024-112
  Date:     2024-06-15
  Total:    $12,100.00
  Lines (3):
    - System Architecture Review: 1 x $3500.0 = $3500.0
    - Implementation Support: 3 x $2200.0 = $6600.0
    - Documentation: 1 x $900.0 = $900.0

==================================================
  Freelance / minimal
==================================================
  Vendor:   Maya Osei Design Studio
  Invoice#: 0047
  Date:     2024-09-03
  Total:    $5,100.00
  Lines (2):
    - Brand Identity Package: 1 x $4800.0 = $4800.0
    - Revision Round (2 hrs): 1 x $300.0 = $300.0
```

### Schema

```
Invoice
  vendor          str
  invoice_number  str
  date            str   (YYYY-MM-DD)
  subtotal        float
  tax             float
  total_amount    float  ← validator: must be > 0
  line_items      List[LineItem]
    description   str
    quantity      int
    unit_price    float
    total         float
```
