# Adoption Curriculum

A staged rollout plan for an organization introducing agentic AI, built entirely from
examples already in this repo. `CATALOG.md` answers "which example should I look at."
`GUIDELINES.md` answers "how do I read and adapt one example." This document answers a
different question: **in what order should an organization actually adopt this stuff**,
so each stage is a small, safe, demonstrable step instead of a big-bang rollout.

Each module below has a business capability it unlocks, the examples that teach it,
and a graduation criterion — a concrete thing the org should be able to point to before
moving to the next module. Skipping ahead is possible but not recommended: later modules
assume the habits (typed outputs, deterministic validation, citation grounding) that
earlier modules build.

**Who this is for:** whoever owns the AI rollout — an engineering lead, an ops/automation
lead, or a small cross-functional working group. Modules 0–3 are things one engineer can
ship alone. Modules 4–6 need a product owner in the loop. Modules 7–8 need sign-off from
whoever owns risk (compliance, controller, security) because that's the point where an
agent's output can trigger something irreversible.

---

## Module 0 — The one agent virtually everyone needs

**Capability unlocked:** replace a manual triage/classification task with a schema-constrained
LLM call. No tools, no state, no multi-step reasoning — just input in, typed output out.

| # | Example | Status |
|---|---------|--------|
| 2 | [Email Triage](./examples/2-email-triage/README.md) | done |
| 24 | [OpenRouter Structured Output](./examples/24-openrouter-structured-output/README.md) | done |

**Why this is first:** smallest possible blast radius. If the model gets it wrong, a human
was going to review the queue anyway. This is the pattern every other module builds on:
never let free text leave the model when a typed field will do.

**Graduation:** one schema-constrained classifier running against real inputs (not sample
data), with a human still reviewing every output before anything downstream happens.

---

## Module 1 — Reliable extraction (validation + retry)

**Capability unlocked:** the model's output is trustworthy enough to feed a downstream
system without a human re-typing it.

| # | Example | Status |
|---|---------|--------|
| 3 | [Invoice Extractor](./examples/3-invoice-extractor/README.md) | done |
| 4 | [Lead Qualifier](./examples/4-lead-qualifier/README.md) | done |
| 6 | [Resume Screener](./examples/6-resume-screener/README.md) | done |

**Why this is next:** Module 0 proved the pattern works on one document type. This module
adds the two things that make it production-safe: automatic retry when the output doesn't
match the schema, and a scoring rubric the model must cite (not just assert).

**Graduation:** the same extract-and-validate pattern is running against 3+ different
document types without redesigning the pipeline each time.

---

## Module 2 — Deterministic tools (don't trust the model with arithmetic)

**Capability unlocked:** separating judgment (the model) from computation (code) — the
model decides *what*, a Python function decides *how much*.

| # | Example | Status |
|---|---------|--------|
| 1 | [Basic ReAct Agent](./examples/1-basic-react-agent/README.md) | done |
| 19 | [Financial Modeller](./examples/19-financial-modeller/README.md) | done |
| 44 | [JV Posting Agent](./examples/44-jv-posting-agent/README.md) | done |

**Why this is next:** every prior module was a single LLM call. This is the first module
where the model calls a tool and reads the result back. The lesson that matters most:
example 44's debit=credit check is Python, not the model doing arithmetic in its head.
Anywhere money, dates, or counts get computed, compute them in code.

**Graduation:** at least one agent in production where a deterministic function — not the
model — decides pass/fail on a numeric check.

---

## Module 3 — Guardrails and rejection paths

**Capability unlocked:** an agent that can say no. Routes exceptions to a human queue
instead of producing a confident answer every time.

| # | Example | Status |
|---|---------|--------|
| 45 | [AP Invoice Processor](./examples/45-ap-invoice-processor/README.md) | done |
| 47 | [Expense Audit Agent](./examples/47-expense-audit-agent/README.md) | done |
| 13 | [M&A Screener](./examples/13-ma-screener/README.md) | done |
| 17 | [Corporate Finance](./examples/17-corporate-finance/README.md) | done |

**Why this is next:** this is where "agent" starts meaning something more than "smart
autocomplete." A 3-way match that routes discrepancies, or a threshold gate where any
one failing dimension blocks the whole verdict, is qualitatively different from Modules
0–2 — the agent's job now includes knowing when *not* to proceed.

**Graduation:** an agent in production that routes at least one class of exception to a
human queue instead of auto-approving it.

---

## Module 4 — Grounded synthesis (citations, not assertions)

**Capability unlocked:** every claim the agent makes is traceable to a source a human can
check in under a minute. This is the difference between a demo and something legal,
compliance, or finance will actually rely on.

| # | Example | Status |
|---|---------|--------|
| 9 | [Contract Reviewer](./examples/9-contract-reviewer/README.md) | done |
| 15 | [Regulatory Researcher](./examples/15-regulatory-researcher/README.md) | done |
| 23 | [Knowledge Management](./examples/23-knowledge-mgmt/README.md) | done |

**Graduation:** an agent whose output includes a citation (clause number, source article,
document ID) for every substantive claim, and someone outside engineering has spot-checked
those citations and trusts them.

---

## Module 5 — Multi-agent fan-out

**Capability unlocked:** splitting one job across independent specialist calls and merging
typed results, instead of one giant prompt trying to do everything.

| # | Example | Status |
|---|---------|--------|
| 32 | [Onboarding Orchestrator](./examples/32-onboarding-orchestrator/README.md) | done |
| 10 | [Due Diligence](./examples/10-due-diligence/README.md) | done |
| 8 | [Multi-Agent Research](./examples/8-multi-agent-research/README.md) | done |
| 27 | [Multi-Provider Fan-Out](./examples/27-multi-provider-fan-out/README.md) | done |

**Why this is next:** everything so far has been one agent, one job. This module is the
first time multiple agent calls run for a single request and their typed outputs get
merged into one report — the shape every later supervisor pattern builds on.

**Graduation:** one workflow in production where 2+ independent agent calls run and are
merged into a single output a human reads once, not three times.

---

## Module 6 — Hierarchical supervisors (conditional dispatch)

**Capability unlocked:** a supervisor whose real job is deciding what *not* to run, not
just fanning out to every specialist every time.

| # | Example | Status |
|---|---------|--------|
| 91 | [Security Operations Supervisor](./examples/91-security-operations-supervisor/README.md) | done |
| 57 | Manufacturing Intelligence Supervisor | pending |

**Why this is next:** fan-out (Module 5) always runs every specialist. A real supervisor
inspects the day's signal first and only dispatches the domains that have something to
say — running all five specialists every day regardless is a fixed pipeline with extra
steps, not orchestration.

**Graduation:** a supervisor that visibly skips at least one specialist on a normal-signal
day, proving the conditional logic is real and not just a label.

---

## Module 7 — Human-in-the-loop as a real execution gate

**Capability unlocked:** an agent-recommended irreversible action that cannot fire without
a logged human decision — not a routing label, an actual pause.

| # | Example | Status |
|---|---------|--------|
| 90 | [Approval Gate Pattern](./examples/90-approval-gate-pattern/README.md) | done |

**Why this is the hinge point:** every module before this produced *advice*. This is where
an agent's output can trigger something real — revoking access, sending a customer notice,
posting money — and the org needs a genuine pause, not a field that says `approval_tier:
"manager"` that nothing actually enforces. This is also the first module that needs
sign-off from whoever owns risk, not just engineering.

**Graduation:** one agent-recommended action in production that is provably unreachable
without a human approve/edit/reject decision, and every decision — including approvals —
is logged with a rationale.

---

## Module 8 — Governed multi-agent orgs (controls, not just correctness)

**Capability unlocked:** turning a set of individually-correct agents into an actual
control an auditor would accept — consolidated, materiality-ranked, and sign-off-gated.

| # | Example | Status |
|---|---------|--------|
| 91 | [Security Operations Supervisor](./examples/91-security-operations-supervisor/README.md) | done |
| 97 | [Ledger Integrity Supervisor](./examples/97-ledger-integrity-supervisor/README.md) | scaffolded |
| 98 | Segregation-of-Duties Checker | pending |
| 99 | Audit-Trail Synthesizer | pending |

**Why this is last:** a pile of correct point-tools is not a control. Example 97 is the
concrete version of this lesson — it doesn't rebuild the finance agents from Modules 1–3,
it composes the already-shipped ones (44, 46, 50, 55) into one governed close cycle,
consolidates every exception into a single register ranked by financial exposure, and
requires human sign-off (Module 7's gate) before the cycle can be marked complete.

**Graduation:** the org can hand an auditor one ranked exception register where every
high-materiality item has a citable human-approval record attached.

---

## Suggested pacing

This is a shape, not a schedule — actual pace depends on how much of the org's real data
is already in a usable form.

| Phase | Modules | Typical owner |
|-------|---------|---------------|
| Prove it works | 0–2 | One engineer, one afternoon per module |
| Make it production-safe | 3–4 | Engineer + the process owner whose task is being automated |
| Scale it | 5–6 | Engineer + a product/ops owner coordinating multiple domains |
| Make it governable | 7–8 | Engineer + compliance/controller/security sign-off |

Most orgs can clear Modules 0–3 inside a month using this repo's synthetic data as-is.
Modules 4–6 are where the org's *own* documents and data start replacing the samples.
Modules 7–8 should not start until the org has real production experience from earlier
modules and an actual appetite for letting an agent's recommendation trigger something
irreversible.

## How to use this alongside CATALOG.md and GUIDELINES.md

- **This file** answers "what order should we adopt these capabilities in."
- **[CATALOG.md](./CATALOG.md)** answers "which specific example matches my problem," sorted
  by difficulty and department.
- **[GUIDELINES.md](./GUIDELINES.md)** answers "how do I read, run, and adapt one example
  once I've picked it."

Read commit history for whichever example you're on — every one is built in the same
phased sequence (scaffold → schema → workflow → main+README → workbook), so the git log
is itself part of the lesson.
