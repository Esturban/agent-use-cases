# 23 — Knowledge Management

Ask it a question about past work. It searches a corpus of engagement documents, pulls the most relevant precedents, and drafts a grounded brief that cites them explicitly — no hallucinated references.

---

## What it does

You pass in a natural-language query and get back:

- The 2–4 most relevant documents from the corpus, with relevance explanations
- A synthesis that directly addresses the query and cites documents by name
- A list of gaps where no prior work covers the question

---

## How it works

Two structured LLM calls — no vector database required:

1. **Retrieve**: the LLM reads the corpus index and selects relevant documents
2. **Synthesise**: a second call drafts the `KnowledgeBrief`, citing only retrieved precedents

The in-memory corpus here has 5 documents. Swap it out for a vector store, a SharePoint search, or a Notion API call and the schema and synthesis step stay identical.

---

## What you'll see

```
============================================================
Query: We're pitching a SaaS company on EMEA market expansion. What does our prior work say about go-to-market strategy in Europe?
============================================================

Precedents retrieved (3):
  [doc-004] Nordics SaaS Scale-Up — GTM Playbook (2023)
    Relevance: Directly addresses EMEA partner-led expansion for a B2B SaaS firm, including channel strategy and localisation decisions.
  [doc-001] Global Payments Platform — European Regulatory Entry
    Relevance: Covers regulatory sequencing and entity setup in Germany and France, which will surface in the pitch conversation.
  [doc-007] Series B FinTech — UK to EU Market Expansion
    Relevance: Documents the trade-offs between direct sales and reseller models across three EMEA territories.

Synthesis:
Based on three prior engagements, the strongest predictor of EMEA SaaS success is choosing a single anchor market
rather than launching across multiple countries simultaneously (doc-004, doc-007). The Nordics playbook recommends
Germany or the Netherlands as a first landing zone due to English-language sales motion and faster procurement cycles.
Regulatory complexity — particularly around data residency — should be addressed before commercial launch, not after
(doc-001). A partner-led channel motion has outperformed direct sales in two of the three cases reviewed.

Gaps (1):
  - No precedent covers pricing localisation strategy (e.g. EUR vs USD invoicing, purchasing-power adjustment).
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/23-knowledge-mgmt/main.py
```

---

## Files

```
23-knowledge-mgmt/
  src/schema.py      # Precedent, KnowledgeBrief
  src/workflow.py    # LLM-as-retriever + citation-grounded synthesis
  main.py            # 2 queries: EMEA SaaS GTM, IoT pilot lessons
  README.md
```
