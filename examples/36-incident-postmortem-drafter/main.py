from dotenv import load_dotenv

load_dotenv()

from src.workflow import run  # noqa: E402

RAW_LOG = """
INCIDENT: INC-2026-042
Title: Database Connection Pool Exhaustion — API Timeouts

2026-06-18T14:30:00Z [INFO] Automated alert: p99 API latency crossed 2000ms threshold (orders-service)
2026-06-18T14:33:00Z [WARNING] orders-service reporting DB connection wait times > 5s; pool utilization 98%
2026-06-18T14:37:00Z [CRITICAL] orders-service returning 503 errors to 60% of checkout requests; DB pool fully exhausted
2026-06-18T14:40:00Z [INFO] On-call engineer paged; investigation started
2026-06-18T14:52:00Z [WARNING] payments-service also degraded — shares same RDS instance read replica
2026-06-18T15:05:00Z [INFO] Root cause identified: batch analytics job deployed at 14:15 consuming 200+ concurrent DB connections with no connection limit configured
2026-06-18T15:10:00Z [INFO] Analytics job terminated; connections released; orders-service error rate dropping
2026-06-18T15:22:00Z [INFO] API latency returned to baseline; payments-service fully recovered
2026-06-18T15:45:00Z [INFO] Post-incident monitoring: all services stable, no further anomalies
2026-06-18T16:15:00Z [INFO] Incident resolved; mitigation documented

Affected services: orders-service, payments-service, rds-primary, rds-read-replica
"""

if __name__ == "__main__":
    print("Parsing incident log and drafting postmortem...\n")
    postmortem = run(RAW_LOG)

    print(f"Incident: {postmortem.incident_id} — {postmortem.title}")
    print(f"\nRoot Cause: {postmortem.root_cause}")
    print(f"\nImpact: {postmortem.impact_summary}")

    print("\n--- Contributing Factors ---")
    for factor in postmortem.contributing_factors:
        print(f"  * {factor}")

    print("\n--- Action Items ---")
    for item in postmortem.action_items:
        print(f"  [ ] {item}")

    print("\n--- Detection Improvements ---")
    for improvement in postmortem.detection_improvements:
        print(f"  + {improvement}")

    print("\n--- Executive Summary ---")
    print(postmortem.executive_summary)
