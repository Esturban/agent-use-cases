# 91 · Security Operations Supervisor

A hierarchical supervisor that conditionally dispatches domain specialists across a daily security signal digest and synthesises a board-ready posture brief.

**Business problem:** A security team's daily signal feed spans auth anomalies, dependency-scan deltas, IAM diffs, and open incidents -- each domain has its own analyst lens, but running every specialist on every signal every day is noisy and slow, and a single P0 finding buried in a wall of reports is easy to miss or, worse, act on without sign-off.

**How it works:** Each day's signal digest is checked domain by domain, and only the specialists with something to look at actually run (threat triage only if an auth event was flagged, access governance only if the IAM diff isn't empty, and so on) -- not all five, every day. Each specialist that runs comes back with a structured finding: a severity, a summary, and a recommended action. The single most urgent P0/P1 finding is held for a human to approve, edit, or reject before its recommendation counts as anything more than a suggestion -- reject or edit it and it never quietly goes through. A simple cross-check also looks for the same identity showing up in more than one specialist's findings -- in the busy-day example, the orphaned service account turns out to be the same identity behind a flagged off-hours login, and the brief calls that out as one incident instead of two unrelated ones.

**How to run:**
```
cp .env.example .env  # add OPENAI_API_KEY
python examples/91-security-operations-supervisor/main.py
```

**Prerequisite:** id 90 (approval-gate pattern) -- this example copies and adapts its `ProposedAction` / `ApprovalDecision` / `ActionResult` shape rather than importing across example folders, so each example stays independently deployable.
