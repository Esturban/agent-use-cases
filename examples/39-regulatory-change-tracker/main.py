"""Regulatory change tracker — two end-to-end demo scenarios."""

from dotenv import load_dotenv

load_dotenv()

from src.schema import (  # noqa: E402
    ComplianceState,
    Obligation,
    ObligationRegister,
    RegulatoryUpdate,
)
from src.workflow import run  # noqa: E402

# ---------------------------------------------------------------------------
# Scenario A — GDPR Amendment: new data retention cap obligation
# Existing register already tracks consent + right-to-erasure.
# The amendment adds a net-new 24-month retention cap; one contract is exposed.
# ---------------------------------------------------------------------------

SCENARIO_A_UPDATE = RegulatoryUpdate(
    update_id="GDPR-AMD-2025-01",
    title="GDPR Amendment — Article 5 Data Retention Cap (24 months)",
    effective_date="2025-07-01",
    jurisdiction="EU",
    raw_text=(
        "Amendment to Regulation (EU) 2016/679 (GDPR) — Article 5 Data Quality Principles\n\n"
        "Article 5(1)(e) is amended as follows:\n\n"
        "Personal data shall be kept in a form which permits identification of data subjects "
        "for no longer than is necessary for the purposes for which the personal data are "
        "processed ('storage limitation'). With effect from 1 July 2025, controllers must "
        "implement a maximum retention period of 24 months for all personal data processed "
        "under a legitimate interest basis, unless a longer period is mandated by Union or "
        "Member State law. Controllers must document the retention schedule and make it "
        "available to supervisory authorities on request.\n\n"
        "Article 13(2)(a) is amended to require that privacy notices explicitly state "
        "the 24-month maximum retention period where applicable.\n\n"
        "No changes are made to Articles 6 (lawful basis), 7 (consent conditions), or "
        "17 (right to erasure) by this amendment."
    ),
    summary=(
        "Introduces a hard 24-month maximum retention period for personal data processed "
        "under legitimate interest. Controllers must document retention schedules and update "
        "privacy notices to reflect the cap."
    ),
)

SCENARIO_A_REGISTER = ObligationRegister(
    jurisdiction="EU",
    obligations=[
        Obligation(
            id="OBL-001",
            text=(
                "Controllers must obtain freely given, specific, informed and unambiguous "
                "consent before processing personal data where consent is the lawful basis."
            ),
            source_article="Article 7(1) GDPR",
            category="consent-management",
            effective_date="2018-05-25",
            status="active",
        ),
        Obligation(
            id="OBL-002",
            text=(
                "Controllers must erase personal data without undue delay where the data "
                "subject withdraws consent or objects to processing, and no other lawful "
                "basis applies."
            ),
            source_article="Article 17(1) GDPR",
            category="data-erasure",
            effective_date="2018-05-25",
            status="active",
        ),
    ],
)

SCENARIO_A_CONTRACTS = [
    {
        "contract_name": "DataSync SaaS Agreement v3.2",
        "excerpt": (
            "Clause 8.1 — Data Retention: The Processor shall retain Customer Personal Data "
            "for the duration of the contract term and for a period of 36 months thereafter, "
            "unless otherwise instructed by the Controller in writing. "
            "Clause 8.2 — Upon termination, the Processor shall delete or return all "
            "Customer Personal Data within 30 days of written request."
        ),
    },
    {
        "contract_name": "AnalyticsPro Licence Agreement v1.0",
        "excerpt": (
            "Section 5 — Privacy: The parties agree to comply with applicable data protection "
            "legislation. The Licensee is responsible for obtaining appropriate consents from "
            "end users prior to processing their personal data through the AnalyticsPro platform. "
            "Data processed under this licence shall be subject to the Licensee's privacy policy."
        ),
    },
]

SCENARIO_A_STATE = ComplianceState(
    version=3,
    last_updated="2024-11-15",
    jurisdiction="EU",
    obligations=SCENARIO_A_REGISTER.obligations,
    pending_actions=[
        "Review consent capture flows against Article 7(1) requirements before Q1 audit.",
    ],
    last_update_summary=(
        "Processed GDPR-GUIDE-2024-11: no net-new obligations identified. "
        "Guidance update on right-to-erasure timelines — existing OBL-002 remains adequate."
    ),
)

# ---------------------------------------------------------------------------
# Scenario B — MiFID II Amendment: new best-execution reporting obligation
# Existing register already captures transaction reporting + client categorisation.
# The amendment adds a net-new quarterly best-execution report; both contracts
# have generic compliance clauses that mostly satisfy the new requirement.
# ---------------------------------------------------------------------------

SCENARIO_B_UPDATE = RegulatoryUpdate(
    update_id="MIFID-AMD-2025-03",
    title="MiFID II Delegated Regulation — Quarterly Best-Execution Report (RTS 28 Revision)",
    effective_date="2025-10-01",
    jurisdiction="EU-MiFID",
    raw_text=(
        "Commission Delegated Regulation amending RTS 28 under MiFID II\n\n"
        "Article 3 — Quarterly Best-Execution Report\n"
        "Investment firms shall publish, on a quarterly basis and no later than 15 business "
        "days after the end of each calendar quarter, a report summarising the top five "
        "execution venues used for each class of financial instrument, together with "
        "information on the quality of execution obtained. The report must be published "
        "in machine-readable format on the firm's public website and submitted to the "
        "competent authority via the designated reporting portal.\n\n"
        "Article 5 — Transaction Reporting (unchanged)\n"
        "No changes are made to Article 26 MiFID II transaction reporting obligations. "
        "Existing transaction reporting schedules and formats remain in effect.\n\n"
        "Article 7 — Client Categorisation (unchanged)\n"
        "Client categorisation requirements under Articles 4(1)(10-12) MiFID II are "
        "not affected by this amendment."
    ),
    summary=(
        "Revises RTS 28 to require a quarterly best-execution report published within "
        "15 business days of each quarter end, in machine-readable format. "
        "Transaction reporting and client categorisation obligations are unchanged."
    ),
)

SCENARIO_B_REGISTER = ObligationRegister(
    jurisdiction="EU-MiFID",
    obligations=[
        Obligation(
            id="OBL-001",
            text=(
                "Investment firms must submit transaction reports to the competent authority "
                "by the close of business on the working day following execution of a "
                "reportable transaction."
            ),
            source_article="Article 26 MiFID II",
            category="transaction-reporting",
            effective_date="2018-01-03",
            status="active",
        ),
        Obligation(
            id="OBL-002",
            text=(
                "Investment firms must categorise each client as a retail client, "
                "professional client, or eligible counterparty and maintain records of "
                "the categorisation and the basis on which it was made."
            ),
            source_article="Article 4(1)(10-12) MiFID II",
            category="client-categorisation",
            effective_date="2018-01-03",
            status="active",
        ),
    ],
)

SCENARIO_B_CONTRACTS = [
    {
        "contract_name": "Prime Brokerage Services Agreement v2.1",
        "excerpt": (
            "Schedule 3 — Regulatory Compliance: Each party agrees to maintain policies "
            "and procedures reasonably designed to comply with applicable MiFID II requirements "
            "as amended from time to time. The Broker shall publish best-execution policies "
            "annually and make them available to the Client on request. "
            "Clause 12.4: The Broker maintains an order execution policy reviewed at least "
            "annually and updated to reflect material changes in regulatory requirements."
        ),
    },
    {
        "contract_name": "Algorithmic Trading Platform Agreement v1.5",
        "excerpt": (
            "Section 9 — Reporting Obligations: The Platform Provider will assist the Client "
            "in meeting its regulatory reporting obligations, including transaction reporting "
            "under Article 26 MiFID II. The Provider maintains connectivity to approved "
            "reporting mechanisms (ARMs) and will submit reports on the Client's behalf. "
            "Section 9.3: Best-execution data is available via the Provider's API in "
            "CSV and JSON formats for Client's own reporting requirements."
        ),
    },
]

SCENARIO_B_STATE = ComplianceState(
    version=5,
    last_updated="2025-01-20",
    jurisdiction="EU-MiFID",
    obligations=SCENARIO_B_REGISTER.obligations,
    pending_actions=[
        "Schedule annual review of order execution policy before December 2025.",
    ],
    last_update_summary=(
        "Processed MIFID-GUIDE-2025-01: no net-new obligations from ESMA Q4 guidance. "
        "Existing transaction reporting and categorisation obligations confirmed adequate."
    ),
)


def _print_result(label: str, result) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    print(f"Update ID      : {result.update_id}")
    print(f"Net-new count  : {result.net_new_count}")
    print(f"\nSummary:\n  {result.summary}")

    if result.impact_assessments:
        print("\nImpact Assessments:")
        for i, assessment in enumerate(result.impact_assessments, 1):
            obl = assessment.obligation
            print(f"\n  [{i}] {obl.source_article} — {obl.category.upper()}")
            print(f"      Obligation : {obl.text[:120]}{'...' if len(obl.text) > 120 else ''}")
            print(f"      Overall    : {assessment.overall_impact.upper()}")
            print(f"      Action     : {assessment.action_item}")
            for exposure in assessment.contract_exposures:
                if exposure.impact != "none":
                    print(f"      Contract   : {exposure.contract_name} -> {exposure.impact}")
    else:
        print("\nNo net-new obligations identified — register is current.")

    state = result.updated_state
    print(f"\nUpdated Compliance State (v{state.version}):")
    print(f"  Last updated   : {state.last_updated}")
    print(f"  Obligations    : {len(state.obligations)} total")
    print(f"  Pending actions: {len(state.pending_actions)}")
    for action in state.pending_actions:
        print(f"    - {action[:100]}{'...' if len(action) > 100 else ''}")


if __name__ == "__main__":
    print("Regulatory Change Tracker — Demo Run")

    print("\nRunning Scenario A: GDPR Amendment — Data Retention Cap")
    result_a = run(
        SCENARIO_A_UPDATE, SCENARIO_A_REGISTER, SCENARIO_A_CONTRACTS, SCENARIO_A_STATE
    )
    _print_result("Scenario A: GDPR Amendment", result_a)

    print("\n\nRunning Scenario B: MiFID II Amendment — Best-Execution Reporting")
    result_b = run(
        SCENARIO_B_UPDATE, SCENARIO_B_REGISTER, SCENARIO_B_CONTRACTS, SCENARIO_B_STATE
    )
    _print_result("Scenario B: MiFID II Amendment", result_b)
