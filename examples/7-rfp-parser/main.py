from dotenv import load_dotenv

from src.workflow import parse

load_dotenv()

SAMPLE_RFP = """
REQUEST FOR PROPOSALS
City of Riverside — Information Technology Division

RFP NUMBER: IT-2026-041
TITLE: Enterprise Cloud Migration and Managed Services

ISSUING AGENCY: City of Riverside, Office of Information Technology
CONTRACT DURATION: 3 years with two 1-year renewal options

BUDGET: The City anticipates a contract ceiling not to exceed $750,000 for the initial
three-year term, inclusive of all services, licenses, and travel costs.

IMPORTANT DATES:
- RFP Release: 2026-06-01 (informational only)
- Pre-proposal Conference (mandatory): 2026-06-20, 10:00 AM PST
- Questions Due: 2026-07-01 by 5:00 PM PST
- Proposal Submission Deadline: 2026-07-15 by 2:00 PM PST (HARD DEADLINE)
- Award Notification: 2026-08-01 (estimated)

SCOPE OF WORK:
The City of Riverside seeks a qualified vendor to migrate its on-premises server
infrastructure to a FedRAMP-authorized cloud platform and provide ongoing managed
services for a period of three years.

MANDATORY REQUIREMENTS:
REQ-01 (Technical): Vendor must be a certified partner of at least one FedRAMP-authorized
cloud provider (AWS GovCloud, Azure Government, or Google Cloud for Government).
REQ-02 (Legal): Vendor must be registered to do business in the State of California.
REQ-03 (Administrative): Vendor must carry minimum $2M general liability insurance.
REQ-04 (Technical): All data must remain within US jurisdiction at all times.
REQ-05 (Financial): Vendor must provide audited financial statements for the past two years.
REQ-06 (Technical): Vendor must maintain 99.9% uptime SLA for all hosted services.

PREFERRED QUALIFICATIONS:
REQ-07 (Technical): Experience with municipal government IT modernization projects preferred.
REQ-08 (Technical): ISO 27001 certification preferred.

EVALUATION CRITERIA:
1. Technical Approach and Methodology — 35%
   Evaluators will assess the vendor's migration plan, risk mitigation strategy,
   and alignment with the City's existing Active Directory and Office 365 environment.

2. Relevant Experience and References — 25%
   Minimum three references from government or public sector clients with similar scope.
   At least one reference must be from a municipality with 50,000+ residents.

3. Cost and Value — 30%
   Total cost of ownership over 3 years including migration, licensing, and managed services.
   Value-added services not included in the base price should be listed separately.

4. Staff Qualifications — 10%
   Project manager must hold PMP certification. Lead cloud architect must hold a
   current certification from the proposed cloud provider.

Proposals must be submitted electronically via the City's vendor portal.
Late submissions will not be considered under any circumstances.
"""


def main():
    result = parse(SAMPLE_RFP)

    print(f"Title:             {result.title}")
    print(f"Agency:            {result.issuing_agency}")
    print(f"Budget ceiling:    {result.budget_ceiling or 'Not stated'}")
    print(f"Contract duration: {result.contract_duration or 'Not stated'}")
    print(f"\nSummary: {result.summary}")

    print(f"\nDEADLINES ({len(result.deadlines)})")
    for d in result.deadlines:
        flag = " [HARD]" if d.is_hard else ""
        print(f"  {d.date:12} {d.label}{flag}")

    print(f"\nREQUIREMENTS ({len(result.requirements)})")
    for r in result.requirements:
        flag = " [mandatory]" if r.mandatory else " [preferred]"
        print(f"  {r.id}  [{r.category:14}]{flag}")
        print(f"         {r.text[:80]}...")

    print(f"\nSCORING CRITERIA ({len(result.scoring_criteria)})")
    for c in result.scoring_criteria:
        weight = f"{c.weight_percent}%" if c.weight_percent is not None else "N/A"
        print(f"  {weight:5}  {c.criterion}")


if __name__ == "__main__":
    main()
