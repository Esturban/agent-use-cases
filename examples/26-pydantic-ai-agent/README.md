# 26 — Invoice Extraction with PydanticAI

Accounts payable teams receive invoices in dozens of formats. This example shows how to pull structured data — vendor, dates, line items, totals — out of free-form invoice text automatically, using a typed agent that enforces the output shape before the result ever reaches your code.

---

## What it does

Plain invoice text goes in. The agent reads the document and returns a fully typed `Invoice` object containing the vendor name, invoice number, issue and due dates, currency, subtotal, tax, total due, and every line item with its quantity, unit price, and total. Two real-world invoice formats are included: a SaaS subscription and a consulting services invoice. The extracted data is ready to hand off to a database, an ERP system, or a spreadsheet — no parsing required.

---

## How it works

The agent is configured with an `Invoice` output type defined entirely in Pydantic. When the agent runs, it injects the schema into the model call, collects the response, validates every field against the type definitions, and retries automatically if the model returns something malformed. Nested models work without any extra wiring — `LineItem` objects inside `Invoice` are validated the same way. The caller receives a plain Python object with guaranteed field types, not a raw string or dict to parse.

---

## What you'll see

```
=== SaaS subscription ===
  Vendor:   Acme Software Inc.
  Invoice#: INV-2024-0891
  Date:     2024-11-01  Due: 2024-11-30
  Currency: USD
  Total:    587.52 (subtotal 544.0 + tax 43.52)
  Lines (2):
    - Professional Plan (monthly): 1.0 x 299.0 = 299.0
    - Additional seats (5): 5.0 x 49.0 = 245.0

=== Consulting services ===
  Vendor:   Meridian Consulting Group
  Invoice#: MCG-2025-0042
  Date:     2025-01-15  Due: 2025-02-14
  Currency: EUR
  Total:    11520.0 (subtotal 9600.0 + tax 1920.0)
  Lines (3):
    - Strategy workshop facilitation: 2.0 x 2500.0 = 5000.0
    - Market analysis report: 1.0 x 3200.0 = 3200.0
    - Follow-up advisory calls: 4.0 x 350.0 = 1400.0
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/26-pydantic-ai-agent/main.py
```

---

## Files

```
26-pydantic-ai-agent/
  src/schema.py      # Invoice and LineItem Pydantic models with field descriptions
  src/workflow.py    # PydanticAI Agent configured to return a typed Invoice
  main.py            # Runs two invoice samples (SaaS + consulting) and prints results
  README.md
```
