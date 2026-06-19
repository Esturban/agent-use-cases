# 43 — Customer Lifecycle Orchestrator

Lifecycle-stage state machine: routes a customer account through lead → onboarding → healthy → at-risk → renewal stages, dispatching a different specialist agent at each stage while accumulating updates in a single typed CustomerRecord.

**Prerequisites:** [4-lead-qualifier](../4-lead-qualifier), [5-support-ticket-router](../5-support-ticket-router), [32-onboarding-orchestrator](../32-onboarding-orchestrator), [33-churn-signal-router](../33-churn-signal-router)

## What it does

Takes a `CustomerRecord` and an incoming `CustomerSignal`, determines which stage the account is in, runs only the specialist agent for that stage, then checks whether a transition to a new stage is warranted.

Five specialist agents — one per stage:

1. **Lead (Qualify)** — ICP scoring and next-step recommendation for inbound leads
2. **Onboarding** — day-1 readiness assessment: completed tasks, pending tasks, blockers
3. **Healthy (Health Check)** — composite health score with risk factors and positive signals
4. **At-Risk (Churn Response)** — segment (escalate / retain / neutral) + personalised follow-up draft
5. **Renewal** — renewal probability, negotiation levers, and outreach draft

A sixth **Transition Agent** decides after each stage run whether to advance the account (e.g. lead → onboarding, healthy → at\_risk) based on the specialist output and the account context.

## Architecture

```
main.py
└── src/workflow.py           # run(record, signal) → OrchestratorResult
    ├── _run_stage_agent()    # dispatches to the ONE specialist for current stage
    ├── _check_transition()   # calls transition agent; returns (bool, next_stage)
    ├── _update_record()      # applies health_score, stage, note back to record
    ├── src/prompts.py        # QUALIFY_SYSTEM, ONBOARD_SYSTEM, HEALTH_SYSTEM,
    │                         # CHURN_SYSTEM, RENEWAL_SYSTEM, TRANSITION_SYSTEM
    └── src/schema.py         # CustomerRecord, CustomerSignal, QualificationResult,
                              # OnboardingStatus, HealthAssessment, ChurnResponse,
                              # RenewalPackage, StageOutput, OrchestratorResult
```

### State machine

```
                +--------+
    form_submit |        |  qualified=true
   ------------>|  lead  |--------------> onboarding
                |        |
                +--------+
                              login / tickets resolve
                              day1_ready=true
                          +------------+ -----------> healthy
                          | onboarding |
                          +------------+ tickets>3 / inactive
                                         -----------> at_risk

                        health_score<0.5       contract_expiry
                +--------+ <-----------  healthy -----------> renewal
                | at_risk |
                +--------+
                   |  retain + health>=0.6     renewal_prob>=0.7
                   +-----------------------> renewal ----------> healthy
```

**Harness focus:** lifecycle-stage state machine — a stateful `CustomerRecord` holds stage, health score, signals, and notes; the orchestrator dispatches to a different specialist agent per stage rather than running all agents on every signal.

**Framework:** openai-sdk (direct `OpenAI` client, `response_format` structured output for specialist agents, `json_object` for the transition decision)

**Comparable patterns:** LangGraph state graphs with conditional edges, LangChain router + ConversationBufferMemory, CrewAI conditional crews with shared state

## Setup

```bash
pip install openai pydantic python-dotenv
```

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_key
```

## Usage

```bash
python main.py
```

## Output

```
============================================================
  Customer A -- Lead Qualification
============================================================
  Customer : CUS-001
  Stage    : lead  ->  onboarding
  Transition: True

  Stage output (summary):
    qualified: True
    icp_score: 0.82
    reasoning: Flowstate Analytics meets ICP on pain point (manual compliance reporting)...
    recommended_next_step: Schedule discovery call with CFO within 24 hours.

============================================================
  Customer B -- At-Risk Churn Response
============================================================
  Customer : CUS-002
  Stage    : at_risk  ->  at_risk (no change)
  Transition: False

  Stage output (summary):
    segment: escalate
    follow_up_draft: Hi [Name], I'm reaching out personally as head of Customer Success...
    urgency: immediate

============================================================
  Customer C -- Renewal Package
============================================================
  Customer : CUS-003
  Stage    : renewal  ->  renewal (no change)
  Transition: False

  Stage output (summary):
    renewal_probability: 0.81
    negotiation_levers: ['Multi-year pricing at 8% discount', 'Executive QBR with new COO', ...]
    outreach_draft: Hi [Name], with Vantage Capital's contract renewing on July 19...
    recommended_discount_pct: 0.0
```

## Workbook

Open `customer_lifecycle_orchestrator_workbook.ipynb` for an interactive walkthrough.
