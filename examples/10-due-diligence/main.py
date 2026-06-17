from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

DOCUMENTS = {
    "Management Accounts (FY2024)": """
ACME TECHNOLOGIES LTD -- MANAGEMENT ACCOUNTS FY2024 (UNAUDITED)

Revenue: GBP 4.2m (FY2023: GBP 3.1m, +35%)
Gross margin: 61% (FY2023: 58%)
EBITDA: GBP 0.3m (FY2023: GBP -0.4m)
Net cash position: GBP 0.1m
Monthly burn rate: GBP 180k

Revenue breakdown:
- Customer A (RetailCo): GBP 2.1m (50% of total revenue)
- Customer B (LogisCorp): GBP 0.8m (19%)
- All other customers: GBP 1.3m (31%)

Recurring revenue (SaaS subscriptions): 68% of total
Professional services: 32% of total

Headcount: 34 FTE. Engineering: 18. Sales: 4. Support: 6. Management: 6.
Three senior engineers resigned in Q4 2024. Replacement hiring in progress.

Outstanding debtor days: 87 (industry benchmark: 45)
Two invoices to RetailCo totalling GBP 310k overdue by more than 90 days.
""",
    "Key Customer Contract (RetailCo)": """
MASTER SERVICES AGREEMENT -- ACME TECHNOLOGIES LTD AND RETAILCO PLC

Term: 24 months commencing 1 March 2023, expiring 28 February 2025.
No auto-renewal clause. Renewal subject to negotiation.
Annual contract value: GBP 2.1m.

Section 4. Termination for Convenience
RetailCo may terminate this Agreement with 30 days written notice for any reason.
No termination fee applies.

Section 7. IP and Data
All custom development performed under this Agreement becomes the property of RetailCo.
This includes any modifications to Acme's core platform made specifically for RetailCo.

Section 9. Service Level Agreement
Acme guarantees 99.5% monthly uptime. Three consecutive months of SLA breach entitles
RetailCo to terminate without penalty.

Section 11. Benchmarking
RetailCo may benchmark Acme's pricing against market alternatives annually and request
renegotiation if pricing exceeds market rates by more than 15%.
""",
    "CEO Biography": """
JAMES WHITFIELD -- CO-FOUNDER AND CEO

James co-founded Acme Technologies in 2019. He holds a BSc in Computer Science.
James owns 45% of Acme Technologies. Co-founder Sarah Chen (CTO) owns 40%.
Remaining 15% held by early angel investors.

Prior venture: James co-founded DataFlow Ltd in 2014, which entered administration in
2017 following a failed Series A. Creditors received 12p in the pound.

James is relocating to Singapore in Q3 2025 for personal reasons. Remote working
arrangement agreed with the board for a period of 12 months.
""",
    "ICO Enforcement Notice": """
INFORMATION COMMISSIONER'S OFFICE -- ENFORCEMENT NOTICE
Date: 14 November 2024 | Reference: ENF/2024/AC-0847

Acme Technologies Ltd has been found to be in breach of Article 32 of the UK GDPR
following a personal data incident in August 2024 in which customer records of
approximately 12,000 RetailCo end-users were exposed due to a misconfigured database.

Acme is required to implement a comprehensive information security programme by 31 March
2025, submit a remediation report to the ICO by 30 April 2025, and appoint a qualified
Data Protection Officer by 28 February 2025.

Failure to comply may result in a financial penalty of up to GBP 17.5m or 4% of
annual global turnover, whichever is greater.
""",
}


def main():
    report = run(DOCUMENTS)

    SEV = {"critical": "CRIT", "high": "HIGH", "medium": "MED ", "low": "LOW "}
    LIK = {"high": "H", "medium": "M", "low": "L"}

    print("\n" + "=" * 65)
    print("COMMERCIAL DUE DILIGENCE REPORT")
    print("=" * 65)
    print(f"Target:     {report.target_company or 'Acme Technologies Ltd'}")
    print(f"Assessment: {report.overall_assessment.upper()}")
    print(f"\nEXECUTIVE SUMMARY\n{report.executive_summary}")

    print(f"\nRISK REGISTER ({len(report.risk_items)} items)")
    print(f"  {'SEV':<6} {'LIK':<4} {'AREA':<14} TITLE")
    print("  " + "-" * 55)
    for r in report.risk_items:
        print(f"  [{SEV[r.severity]}] [{LIK[r.likelihood]}]  {r.area:<14} {r.title}")
        print(f"         Source: {r.source_document}")

    if report.key_conditions:
        print(f"\nKEY CONDITIONS ({len(report.key_conditions)})")
        for c in report.key_conditions:
            print(f"  * {c}")

    if report.further_investigation:
        print(f"\nFURTHER INVESTIGATION ({len(report.further_investigation)})")
        for i in report.further_investigation:
            print(f"  ? {i}")


if __name__ == "__main__":
    main()
