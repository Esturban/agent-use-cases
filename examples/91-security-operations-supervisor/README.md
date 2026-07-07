# 91 · Security Operations Supervisor

A hierarchical supervisor that conditionally dispatches domain specialists across a daily security signal digest and synthesises a board-ready posture brief.

**Business problem:** A security team's daily signal feed spans auth anomalies, dependency-scan deltas, IAM diffs, and open incidents -- each domain has its own analyst lens, but running every specialist on every signal every day is noisy and slow, and a single P0 finding buried in a wall of reports is easy to miss or, worse, act on without sign-off.

**Harness focus:** hierarchical signal triage + conditional subagent dispatch + materiality-gated escalation. The supervisor inspects the daily `SecuritySignalDigest` and dispatches *only* the domain subagents whose slice of the digest has active signal (threat-triage only if an auth event is flagged, access-governance only if the IAM diff is non-empty, and so on) -- not all five, every time. Every dispatched subagent returns a typed `SecurityFindingReport`. Any finding at P0/P1 severity is escalated through the human-approval gate copied from the approval-gate pattern (id 90) before its recommendation is treated as actionable rather than merely advisory; reject or edit and the recommendation never silently executes. A deterministic (non-LLM) correlation check cross-references identities across domains -- in the busy-day scenario, the orphaned service account is the same identity behind a flagged off-hours login, and the supervisor surfaces that as one incident, not two.

**How to run:**
```
cp .env.example .env  # add OPENAI_API_KEY
python examples/91-security-operations-supervisor/main.py
```

**Prerequisite:** id 90 (approval-gate pattern) -- this example copies and adapts its `ProposedAction` / `ApprovalDecision` / `ActionResult` shape rather than importing across example folders, so each example stays independently deployable.
