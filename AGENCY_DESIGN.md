# Agency Design — Personas, Per-Step Risk, and Framework Fit

`CURRICULUM.md` sequences *what* to adopt and in what order. This document is about
*whose* job each agent replaces or assists, *how much risk* each step actually carries
(assessed fresh at every step, not decided once), and *which framework* fits the team
that will own it. Read it after picking a module in `CURRICULUM.md`, before you start
personalizing that module's example for your org.

---

## 1. The agency model — subagents map to roles, not to code

Every supervisor cluster in this repo (`91-security-operations-supervisor` today;
`97-ledger-integrity-supervisor` and the manufacturing/procurement/inventory/logistics
clusters queued) is structured the way a real org staffs a function: a supervisor that
triages and dispatches, and named specialists that each own one lens. This wasn't
arbitrary — the security-ops and governance-controls clusters (ids 91–99) were built
using `github.com/msitarzewski/agency-agents` as role-taxonomy inspiration: a library of
persona prompts (not runnable code) organized into a `security/` division (AppSec
Engineer, Security Architect, Incident Responder, Penetration Tester, SecOps, Threat
Detection/Intel, plus Blockchain/Cloud/Compliance specialists) and a `specialized/`
division (CFO, Automation Governance Architect, Data Privacy Officer, Identity Graph
Operator, Accounts Payable Agent).

That same persona library ships in this environment's own agent roster. Use it as a
**role catalogue** when personalizing an example: instead of writing a subagent's system
prompt from scratch, start from the nearest existing persona's framing and narrow it to
the one task your pipeline actually needs.

| Example cluster | Subagent | Nearest persona to borrow framing from | Build status |
|---|---|---|---|
| 91 — Security Operations | `threat_triage_agent` | Threat Detection Engineer | done |
| 91 | `access_governance_agent` | Identity Graph Operator / Agentic Identity & Trust Architect | done |
| 91 | `vulnerability_remediation_agent` | Application Security Engineer | done |
| 91 | `incident_commander_agent` | Incident Responder | done |
| 91 | `compliance_evidence_agent` | Compliance Auditor | done |
| 97 — Ledger Integrity | JV posting (44) | Bookkeeper & Controller | done (standalone) |
| 97 | Bank reconciliation (46) | Bookkeeper & Controller | done (standalone) |
| 97 | Fixed-asset rollforward (50) | Financial Analyst / FP&A Analyst | pending |
| 97 | Fraud/SAR screening (55) | Senior SecOps Engineer (fraud lens) | pending |
| 97 | Segregation-of-duties checker (98) | Compliance Auditor | pending |
| 97 | Audit-trail synthesizer (99) | Compliance Auditor | pending |
| 97 — supervisor itself | — | Chief Financial Officer / Automation Governance Architect | scaffolded |

**The point of the mapping isn't naming — it's ownership.** When you personalize an
example for your org, the "nearest persona" column tells you *which human role should
review this subagent's prompt and output* before it goes anywhere near production. A
threat-triage subagent's prompt should be reviewed by whoever would do that job
manually, not by whoever happened to write the Python.

---

## 2. Risk assessment at every step — not one HITL module

`CURRICULUM.md`'s Module 7 introduces the human-approval gate (id 90) as its own stage,
which is correct for *learning* it — but treating HITL as something you "turn on" once
you reach Module 7 is the wrong mental model for *operating* it. The right question at
every module, every time, is the same: **what's the blast radius if this step is wrong,
and is it reversible?** Below is that assessment run against all nine modules.

| Module | What could go wrong | Reversible? | Recommended HITL treatment |
|---|---|---|---|
| 0 — Classification | Wrong triage label | Yes, human re-sorts | Sample-check a % of outputs, not every one |
| 1 — Extraction | Wrong field pulled from a document | Yes, human corrects before use | Spot-check on schema-validation failures only |
| 2 — Deterministic tools | Wrong number reaches a report | Usually yes, before it's acted on | None needed *if* the check is genuinely deterministic — verify it actually is (example 91's own build found a field the model was supposed to set reliably that it didn't; don't assume, check) |
| 3 — Guardrails/rejection | A real exception gets auto-approved | Depends on the action | Required on every reject/escalate path — the whole point of this module is that some outputs must not proceed unchecked |
| 4 — Grounded synthesis | An uncited or miscited claim reaches a reader | Reputational, sometimes not reversible | Required spot-check of citations before the first production use; ongoing sampling after |
| 5 — Multi-agent fan-out | One specialist's error corrupts the merged report | Yes, if caught before distribution | Review the *merge* step, not each specialist individually — that's where errors compound |
| 6 — Supervisors | Wrong domain skipped, or wrong domain escalated | Depends on what's downstream | Required whenever a supervisor's dispatch decision itself has consequences (e.g., skipping a domain that actually had signal) |
| 7 — Approval gate | An irreversible action fires without real review | **No** — by definition | **Mandatory**, logged, citable — this is the floor, not a special case |
| 8 — Governed orgs | A high-materiality exception ships without sign-off | No | **Mandatory** at the consolidation step, regardless of how each subagent scored |

Two things follow from this table:

- **The same interrupt/resume mechanism from id 90 should be reused at every row marked
  "required," not just once.** Example 91 already does this — it doesn't gate every
  finding, only the ones that cross a severity threshold, and it reuses the exact
  `ProposedAction`/`ApprovalDecision`/`ActionResult` shape from id 90 to do it. Seeing
  that pattern repeat across modules 3, 6, 7, and 8 is not redundancy; it's the same
  control applied wherever the actual risk crosses the same threshold. A pattern that
  looks repetitive across different business contexts is doing its job.
- **Modules 0–2 explicitly do NOT need per-item HITL.** Over-gating early, low-risk
  steps is its own failure mode — it teaches the org that agents are only ever advisory,
  which makes Module 7's real gate (where a pause is genuinely load-bearing) look like
  more of the same instead of a meaningfully different commitment.

---

## 3. Framework personalization

This repo defaults to LangGraph for stateful/multi-step examples and the raw OpenAI SDK
for single-call ones, but a team's own stack should decide what they actually build with.
Ids 100–102 exist specifically to make this comparable: they port example 1's tool-calling
ReAct loop verbatim into CrewAI, LangChain-LCEL, and AutoGen so the same lesson can be
diffed across four frameworks.

| Team profile | Framework | Why |
|---|---|---|
| Needs genuine pause/resume (Module 7+) | LangGraph | `interrupt()`/`Command(resume=...)` is a first-class primitive here — this repo's approval-gate pattern depends on it |
| Wants the smallest possible abstraction | Raw OpenAI SDK | No framework lock-in; `response_format`/structured outputs only |
| Type-driven, schema-first team | PydanticAI | Output contract defined before any logic, per example 26 |
| Already standardized on CrewAI / AutoGen | Ids 100–102 | Same lesson, native to the team's existing tooling |
| Multi-provider requirement (cost/latency/compliance) | OpenRouter + `openai` SDK | One variable (the model string) changes, nothing else — examples 24, 27 |

**Personalization rule of thumb:** before adopting Module 3+ patterns, port whichever
Module 0–2 example matches your first real use case into your team's actual framework
first. If the lesson survives the port unchanged, the framework choice was safe. If it
doesn't, that's a sign the chosen framework is missing a primitive (state, interrupt,
structured output) the later modules will need.

---

## 4. Personalized agent spec — the template

Fill this in per agent before it touches production data. It's the bridge between a
generic repo example and something your org actually owns.

```
AGENT SPEC — <name>
Module (CURRICULUM.md):      <0-8>
Based on example:             <#, slug>
Persona / human owner:        <role — see §1 mapping, or your own org chart>
Business trigger:             <what event starts this agent>
Risk tier (see §2):           <low | medium | high>
HITL requirement here:        <none | sample-check | required-on-exception | mandatory>
Framework (see §3):           <langgraph | openai-sdk | pydantic-ai | crewai | ...>
Reused patterns/subagents:    <cite example IDs being composed, not rebuilt>
Escalation path:               <who is the human in the gate, what gets logged>
Production data swap:         <per CATALOG.md's "Production swap" column>
```

**Worked example**, personalizing id 45 (AP Invoice Processor) for a mid-size company:

```
AGENT SPEC — 3-Way Match Discrepancy Router
Module:                        3 (Guardrails and rejection paths)
Based on example:              45, AP Invoice Processor
Persona / human owner:         AP Manager (nearest catalogue persona: Accounts Payable Agent
                                — but the human reviewer, not an autonomous replacement)
Business trigger:              New vendor invoice received via email or AP portal
Risk tier:                     Medium — misrouted invoice delays payment or misapproves spend
HITL requirement here:         Required on every discrepancy above the tier-1 auto-approve
                                threshold; sample-check 5% of tier-1 auto-approvals weekly
Framework:                     OpenAI SDK direct (matches example 45; no state needed)
Reused patterns/subagents:     None yet — standalone. If this org later builds a close-cycle
                                supervisor (id 97 pattern), this becomes a reused subagent,
                                not rebuilt.
Escalation path:                AP Manager queue; decision + rationale logged per invoice
Production data swap:          Point at the real AP portal / email intake instead of sample
                                invoice text (per CATALOG.md)
```

---

## How this fits with the other docs

- **[CURRICULUM.md](./CURRICULUM.md)** — sequencing: what order to adopt capabilities in.
- **This file** — depth: whose role each agent maps to, how much oversight each specific
  step actually needs, and which framework fits the team that owns it.
- **[CATALOG.md](./CATALOG.md)** — lookup: which specific example matches a given problem.
- **[GUIDELINES.md](./GUIDELINES.md)** — mechanics: how to read, run, and adapt one example.
