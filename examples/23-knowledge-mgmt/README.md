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
