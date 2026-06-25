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

## Enterprise domain coverage (examples 44–89)

The queue adds 46 pending examples across six enterprise domains. Each is a self-contained,
production-realistic demo — **no knowledge of the client data model required** because every
example ships its own synthetic dataset and/or pulls from a free public API.

### Domain clusters and supervisor patterns

Five of the six domains use a **supervisor + subagents** pattern. The supervisor dispatches
only the subagents relevant to the current alert conditions, aggregates their typed outputs,
and synthesises an executive brief. Standalone Finance & Accounting agents (44–56) do not use
a supervisor.

| Domain cluster | Supervisor | Subagents | IDs |
|---|---|---|---|
| Finance & Accounting | — (standalone) | — | 44–56 |
| Manufacturing & Cost Intelligence | 57 | 9 | 58–66 |
| Inventory & Warehouse | 67 | 6 | 68–73 |
| Procurement Intelligence | 74 | 6 | 75–80 |
| Logistics Intelligence | 81 | 5 | 82–86 |
| Executive Intelligence | 87 | 2 | 88–89 |

Queue entries carry `group`, `role`, `supervisor_id`, and `subagents` fields to make the
relationships explicit. A subagent can be built and tested independently before the supervisor
is wired up.

### Synthetic data strategy

Each pending entry has a `synthetic_data` field describing the exact dataset to generate
for demos and testing. The strategy per domain:

- **Finance/Accounting** — Faker-generated GAAP chart-of-accounts (1xxx–8xxx), cost centres
  CC1001–CC9999, deliberate imbalances/miscodes injected at 12–15% rate.
- **Manufacturing** — Realistic OEE ranges (world-class 85%+, poor <60%), Poisson-distributed
  scrap, MTBF/MTTR values, and SPC measurement data with injected rule violations.
- **Inventory/Warehouse** — UNSPSC 8-digit product codes, Poisson demand distribution, ABC
  segmentation, and 5–15% SLOB items deliberately embedded.
- **Procurement** — 80/20 spend distribution, UNSPSC commodity taxonomy, 15–20% maverick spend.
- **Logistics** — Real US city lat/lng pairs for OSRM routing calls, OTIF baseline 85% with
  deliberate failure clusters per carrier or lane.
- **Executive** — 13-week KPI time series with threshold breaches and trend reversals designed
  to exercise the alerting and escalation logic.

### Free public APIs in use

Six APIs appear in enterprise examples. All are free-tier or no-key:

| API | Used for | Key? |
|---|---|---|
| ECB FX Rate API | Multi-currency treasury (51) | No |
| EIA Open Data | Electricity/diesel prices (60, 86) | Yes (free, instant) |
| USASpending.gov | Vendor contract history (79) | No |
| BLS PPI API | PPV market-price validation (77) | No |
| OSRM public router | Real routing distances (83) | No |
| EPA eGRID factors | Scope 2 emissions (89) | No (static table) |

World Bank and OSV.dev APIs (established in examples 28, 30) are also reused in 79.

### Gradio / Hugging Face Spaces deployment

Examples marked `"gradio_ready": true` are suitable for a public Spaces demo. When building:

- Rate-limit external API calls (`time.sleep(0.5)` between requests).
- Cache responses with `functools.lru_cache` or `shelve` for repeat demo inputs.
- Keep demo input sets small (≤10 records, ≤3 suppliers, ≤5 transactions).
- Use `gr.Progress()` for multi-step pipelines and `gr.Error()` for clean failure handling.
- Use **OpenRouter** as the model backend (openrouter.ai) — store the key in HF Secrets,
  never in app code.
- Demos not marked `gradio_ready` have output too large or too sensitive for a public UI.

## Releases

Versioned via GitHub Releases — date tags `vYYYY.MM.DD.N` with auto-generated notes. A merge
to `main` cuts a release automatically (`.github/workflows/release.yml`); CI (`ci.yml`) gates
it and `auto-pr.yml` opens PRs for feature branches. See [`CHANGELOG.md`](./CHANGELOG.md) for
notable changes per release.
