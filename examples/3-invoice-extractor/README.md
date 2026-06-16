# 3-invoice-extractor

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
