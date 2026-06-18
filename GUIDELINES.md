# Teaching Guidelines

`agent-use-cases` is two things at once: a **course** you read as git history, and a
**library** you fork and adapt. 27 worked examples of real agent applications, beginner →
advanced. Each one teaches a single harness attribute applied to a real business problem.

## How to learn

1. **Pick an example** in [`CATALOG.md`](./CATALOG.md) by difficulty — `1` = a single LLM
   call with a schema, `5` = multi-agent with tool loops and stateful merging.
2. **Read its `README.md`** — business problem · harness focus · how to run.
3. **Run it:** `python examples/N-slug/main.py` (keys from `.env`), or open the Colab workbook.
4. **Do the workbook exercise** — each has a starter exercise + answer key.

Read the commits, not just the final files: every example is built in phased commits
(scaffold → schema → workflow → main+README → workbook), so the history itself is the lesson.

## How to adapt a use case

Every example in `CATALOG.md` lists a **Production swap** — the one thing to change to use it
for real. The pattern:

1. Copy `examples/N-slug/` into your project.
2. Swap the **schema** (`src/schema.py`) for your data shape.
3. Swap the **inputs** in `main.py` for your real source (API, webhook, files).
4. Keep the **workflow** (`src/workflow.py`) — that's the reusable agent pattern.

Provider-agnostic: examples default to `gpt-4o-mini` via `langchain-openai`; the OpenRouter
examples (24, 25, 27) use the `openai` SDK pointed at any provider/model.

## How examples are built (contributor protocol)

One example at a time, phased commits, each commit its own reviewable unit:

| Phase | Commit |
|-------|--------|
| scaffold | `chore(examples/N-slug): scaffold` |
| schema | `feat(examples/N-slug): add schema` |
| workflow | `feat(examples/N-slug): add workflow` |
| entry | `feat(examples/N-slug): add main and README` |
| workbook | `feat(examples/N-slug): add Colab workbook` |

Lint clean before every commit: `ruff check examples/ --select E,F,W --ignore E501`.
Keys from `.env` only — never hardcode. Reuse packages already in `requirements.txt`.

## Releases

Versioned via GitHub Releases — date tags `vYYYY.MM.DD.N` with auto-generated notes. A merge
to `main` cuts a release automatically (`.github/workflows/release.yml`); CI (`ci.yml`) gates
it and `auto-pr.yml` opens PRs for feature branches. See [`CHANGELOG.md`](./CHANGELOG.md) for
notable changes per release.
