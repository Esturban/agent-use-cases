# 44 · JV Posting Agent

Converts business event descriptions into balanced, GL-coded double-entry journal entry payloads.

**Business problem:** Finance teams construct journal entries manually from business events, introducing miscoding and imbalance errors across thousands of postings per period.

**Harness focus:** double-entry validation gate — the LLM assigns accounts from a chart of accounts; `calculator.py` enforces the balance constraint deterministically. LLM arithmetic is never trusted for financial correctness. Any imbalanced posting returns `posting_status=rejected`.

**How to run:**
```
cp .env.example .env  # add OPENAI_API_KEY
python examples/44-jv-posting-agent/main.py
```

**Colab workbook:** `jv_posting_workbook.ipynb`
**Gradio demo:** `python examples/44-jv-posting-agent/demo.py`
