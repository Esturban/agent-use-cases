"""Entry point -- runs two daily digests through the security operations supervisor.

Scenario 1 is a busy day with a deliberate cross-domain correlation (the
orphaned service account is the same identity behind a flagged off-hours
login) and a P0 finding, so it exercises the full path: conditional dispatch
-> human_review interrupt -> resume -> synthesized brief.

Scenario 2 is a quiet day with a single low-severity CVE and nothing else,
so only vulnerability_remediation + compliance_evidence dispatch and the
gate never fires -- showing that "conditional" is not just a label.
"""

import os

from dotenv import load_dotenv

from src.schema import (
    ApprovalDecision,
    AuthEvent,
    CVEDelta,
    IAMChange,
    IncidentTicket,
    SecuritySignalDigest,
)
from src.workflow import propose, resume

load_dotenv()


def _busy_day_digest() -> SecuritySignalDigest:
    flagged_events = [
        AuthEvent(
            identity="svc-batch-07",
            event_type="off_hours_login",
            detail="03:14 UTC from 41.223.10.9, unrecognised ASN",
            flagged=True,
        ),
        AuthEvent(
            identity="jdoe",
            event_type="impossible_travel",
            detail="Login from Toronto 09:02 UTC, then Singapore 09:41 UTC",
            flagged=True,
        ),
        AuthEvent(
            identity="asmith",
            event_type="admin_login",
            detail="02:50 UTC admin console login, outside normal hours",
            flagged=True,
        ),
        AuthEvent(
            identity="ctr-4471",
            event_type="impossible_travel",
            detail="Login from Vancouver 14:10 UTC, then Bucharest 14:33 UTC",
            flagged=True,
        ),
        AuthEvent(
            identity="svc-deploy-03",
            event_type="admin_login",
            detail="04:02 UTC unattended admin login, no matching change ticket",
            flagged=True,
        ),
    ]
    benign_events = [
        AuthEvent(
            identity=f"user-{i:03d}",
            event_type="standard_login",
            detail=f"09:{i:02d} local time, corporate VPN range",
            flagged=False,
        )
        for i in range(1, 12)
    ]
    return SecuritySignalDigest(
        auth_events=flagged_events + benign_events,
        cve_deltas=[
            CVEDelta(
                package="libxml2",
                cve_id="CVE-2026-11042",
                severity="critical",
                actively_exploited=True,
            ),
            CVEDelta(
                package="openssl",
                cve_id="CVE-2026-10877",
                severity="high",
                actively_exploited=False,
            ),
            CVEDelta(
                package="requests",
                cve_id="CVE-2026-10021",
                severity="medium",
                actively_exploited=False,
            ),
        ],
        iam_changes=[
            IAMChange(
                identity="asmith",
                change_type="new_admin_grant",
                role="prod-admin",
                detail="no change-ticket reference on file",
            ),
            IAMChange(
                identity="ctr-4471",
                change_type="new_admin_grant",
                role="billing-admin",
                detail="change ticket CHG-8821 on file",
            ),
            IAMChange(
                identity="svc-batch-07",
                change_type="orphaned_account",
                role="prod-write",
                detail="96 days since last legitimate scheduled run",
            ),
        ],
        open_incident=IncidentTicket(
            ticket_id="SEC-2201",
            description="Suspicious outbound traffic detected from the finance VLAN overnight",
            severity="high",
            status="open",
        ),
    )


def _quiet_day_digest() -> SecuritySignalDigest:
    return SecuritySignalDigest(
        auth_events=[
            AuthEvent(
                identity="user-042",
                event_type="standard_login",
                detail="09:15 local time, corporate VPN range",
                flagged=False,
            )
        ],
        cve_deltas=[
            CVEDelta(
                package="pillow",
                cve_id="CVE-2026-10555",
                severity="medium",
                actively_exploited=False,
            )
        ],
        iam_changes=[],
        open_incident=None,
    )


def main():
    scenarios = [
        ("BUSY DAY -- correlated P0 incident", _busy_day_digest()),
        ("QUIET DAY -- single low-severity CVE", _quiet_day_digest()),
    ]

    for label, digest in scenarios:
        print(f"\n{'=' * 70}\nScenario: {label}\n{'=' * 70}")
        result = propose(digest)

        if result["status"] == "paused":
            proposed = result["proposed_action"]
            finding = result["finding"]
            print("\n-- paused at human_review --")
            print(f"Gated finding domain : {finding.domain}")
            print(f"Severity             : {finding.severity}")
            print(f"Summary              : {finding.summary}")
            print(f"Proposed action_type : {proposed.action_type}")
            print(f"Proposed payload     : {proposed.payload}")

            decision = ApprovalDecision(
                decision="approve",
                rationale="Cross-checked against ticket SEC-2201; revoking immediately.",
            )
            resumed = resume(result["thread_id"], decision)
            print("\n-- resumed with human decision --")
            print(f"Decision   : {decision.decision}")
            print(f"Executed   : {resumed['gate_result'].executed}")
            print(f"Audit log  : {resumed['gate_result'].decision_log}")
            brief = resumed["brief"]
        else:
            brief = result["brief"]

        print("\n-- SecurityPostureBrief --")
        print(f"Dispatched domains : {brief.dispatched_domains}")
        print(f"Overall posture    : {brief.overall_posture}")
        print(f"Correlations       : {brief.cross_domain_correlations}")
        for finding in brief.findings:
            print(f"  [{finding.severity}] {finding.domain}: {finding.summary}")


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set -- copy .env.example to .env")
    main()
