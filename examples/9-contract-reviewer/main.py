from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

SERVICES_AGREEMENT = """
PROFESSIONAL SERVICES AGREEMENT

This Professional Services Agreement ("Agreement") is entered into as of January 1, 2025,
between Acme Corp ("Client") and Vendor Ltd ("Service Provider").

Section 1. Services
Service Provider shall perform consulting services as directed by Client from time to time.
Client may modify the scope of services at any time without notice.

Section 2. Payment
Client shall pay Service Provider within 90 days of invoice receipt. Late payments shall
not accrue interest. Client may withhold payment for any reason it deems appropriate.

Section 3. Intellectual Property
All work product, inventions, and developments created by Service Provider under this
Agreement, whether or not patentable, shall be the sole property of the Client.
Service Provider hereby assigns all right, title, and interest in such work product to Client.
This assignment includes all pre-existing tools and methodologies used in the delivery.

Section 4. Confidentiality
Service Provider agrees to keep all Client information confidential for a period of 1 year
following termination of this Agreement.

Section 5. Liability
In no event shall Client be liable to Service Provider for any damages, whether direct,
indirect, incidental, special, or consequential, regardless of the cause. Service Provider's
liability to Client shall be unlimited.

Section 6. Termination
Client may terminate this Agreement immediately and without cause at any time.
Service Provider may not terminate this Agreement without 180 days written notice.

Section 7. Governing Law
This Agreement shall be governed by the laws of the State of Delaware.
"""

NDA = """
NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement is entered into between DisclosedCo and RecipientCo.

1. Confidential Information
"Confidential Information" means all information disclosed by Disclosing Party that is
marked as confidential or that a reasonable person would understand to be confidential.

2. Obligations
Recipient shall hold Confidential Information in strict confidence and shall not disclose
it to any third party. Recipient may share Confidential Information with employees who
need to know it for the Purpose.

3. Term
This Agreement shall remain in effect for 5 years from the Effective Date. Obligations
with respect to trade secrets shall survive indefinitely.

4. Return of Information
Upon request, Recipient shall destroy or return all Confidential Information.

5. Governing Law
This Agreement shall be governed by English law.
"""


def _print_review(review, label):
    SEV_ICON = {"critical": "[CRIT]", "high": "[HIGH]", "medium": "[MED]", "low": "[LOW]"}
    PRI_ICON = {"must_have": "[!!!]", "should_have": "[!!]", "nice_to_have": "[!]"}

    print(f"\n{'='*65}")
    print(f"CONTRACT: {label}")
    print("=" * 65)
    print(f"Type:         {review.contract_type}")
    print(f"Counterparty: {review.counterparty or 'not identified'}")
    print(f"Governing law:{review.governing_law or 'not stated'}")
    print(f"Overall risk: {review.overall_risk.upper()}")
    print(f"\nEXECUTIVE SUMMARY\n{review.executive_summary}")

    print(f"\nRISK FINDINGS ({len(review.risk_findings)})")
    for f in review.risk_findings:
        print(f"\n  {SEV_ICON[f.severity]} [{f.clause_reference}] {f.issue}")
        print(f"     Impact:   {f.implication}")
        print(f"     Redline:  {f.recommended_redline}")

    print(f"\nMISSING PROTECTIONS ({len(review.missing_protections)})")
    for p in review.missing_protections:
        print(f"\n  - {p.protection}")
        print(f"    Why:      {p.why_needed}")
        print(f"    Add:      {p.suggested_clause}")

    print(f"\nNEGOTIATION POINTS ({len(review.negotiation_points)})")
    for n in review.negotiation_points:
        print(f"\n  {PRI_ICON[n.priority]} {n.topic}")
        print(f"    Current:  {n.current_position}")
        print(f"    Target:   {n.target_position}")


def main():
    for contract_text, label in [
        (SERVICES_AGREEMENT, "Professional Services Agreement"),
        (NDA, "Non-Disclosure Agreement"),
    ]:
        review = run(contract_text)
        _print_review(review, label)


if __name__ == "__main__":
    main()
