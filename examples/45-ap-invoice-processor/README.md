# 45 · AP Invoice Processor

## Business Problem

Accounts-payable teams receive vendor invoices as unstructured documents and must
verify them against purchase orders and goods receipts before authorising payment.
Manual 3-way matching is slow, error-prone, and bottlenecks finance operations —
especially at month-end when invoice volumes spike.

## How It Works

A 3-stage pipeline handles each invoice:

1. **LLM Extraction** (`gpt-4.1-nano`) — parses free-text invoice content into a
   structured `ExtractedInvoice` (vendor, invoice number, PO reference, line items,
   total amount).

2. **Deterministic Lookup** — `lookup_po()` and `lookup_gr()` retrieve the matching
   purchase order and goods receipt from mock data with no LLM involvement.

3. **LLM Match Classification** (`gpt-4.1-nano`) — compares invoice vs PO vs GR,
   classifies any discrepancies (`quantity_short`, `price_variance`, `gr_missing`,
   `po_not_found`, `duplicate`), assigns severity (`info`, `warn`, `block`), and
   determines the approval tier deterministically from the severity and total amount.

Approval routing is fully deterministic from the LLM output:

| Condition | Approval Tier |
|-----------|---------------|
| Clean + total < $10,000 | `auto_approve` |
| Warn + total < $25,000 | `line_manager` |
| Warn + total ≥ $25,000 | `finance_controller` |
| Block + total < $50,000 | `finance_controller` |
| Block + total ≥ $50,000 | `vp_finance` |

## How to Run

```bash
# From the repo root
cp .env.example .env        # add your OPENAI_API_KEY
pip install -r requirements.txt
python examples/45-ap-invoice-processor/main.py
```

The demo covers four scenarios:

1. **Clean match** — 4 cloud servers, $8,400, auto-approved
2. **Quantity short** — 100 chairs billed, only 85 received, line manager review
3. **Price variance** — consulting rate $421.25 vs PO $375.00, finance controller
4. **Missing GR** — software licences, no goods receipt on record, finance controller
