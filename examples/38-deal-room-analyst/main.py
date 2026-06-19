from dotenv import load_dotenv

load_dotenv()

from src.schema import DealInput  # noqa: E402
from src.workflow import run  # noqa: E402

ACME_DEAL = DealInput(
    company_name="Acme Logistics Ltd",
    contract_text=(
        "Share Purchase Agreement dated 1 June 2026. Seller: Acme Holdings plc. Buyer: Meridian Capital. "
        "Purchase price: £24m. Completion accounts mechanism. Warranties: standard business warranties, "
        "capped at 30% of purchase price, 18-month tail. No IP assignment clause. No non-compete. "
        "Indemnity for known tax liability of £1.2m. Material adverse change clause included. "
        "Governing law: England & Wales."
    ),
    diligence_documents=[
        "FY2025 management accounts: Revenue £8.2m, EBITDA £1.4m, Net debt £2.1m. "
        "Three top customers represent 71% of revenue. Two customer contracts expire Dec 2026 without renewal options.",
        "CEO joined 18 months ago; CFO vacancy unfilled for 4 months. "
        "Key operations manager handed notice 2 weeks ago.",
        "HMRC enquiry open since March 2025 re: R&D tax credit claim of £340k. "
        "No provision taken in accounts. Legal counsel rates resolution probability at 60%.",
    ],
    financial_summary=(
        "Revenue £8.2m growing at ~12% p.a. EBITDA margin 17%, improving from 14% two years ago. "
        "Net debt £2.1m. Capex requirements low (asset-light model). No audited accounts — management accounts only."
    ),
)

CLEAN_DEAL = DealInput(
    company_name="NovaTech Software Inc",
    contract_text=(
        "Asset Purchase Agreement. Seller: NovaTech Software Inc. Buyer: Vertex Partners LLC. "
        "Purchase price: $18m. IP fully assigned to buyer. Non-compete 3 years, 50-mile radius. "
        "Representations and warranties standard SaaS; cap at 100% of purchase price, 24-month tail. "
        "Escrow: 10% held 12 months. Indemnification for pre-closing liabilities. "
        "MAC clause. Governing law: Delaware."
    ),
    diligence_documents=[
        "Audited FY2025 financials: ARR $6.1m, Net Revenue Retention 118%, churn 4% annual. "
        "Top customer 14% of ARR. No customer concentration risk.",
        "Management team stable 3+ years. CTO and VP Sales both have retention packages tied to deal close.",
        "No open litigation. IP fully owned; no third-party licenses embedded in product. "
        "SOC 2 Type II certified. GDPR compliant.",
    ],
    financial_summary=(
        "ARR $6.1m, growing 28% YoY. EBITDA positive at $1.2m. Zero debt. "
        "Full audited financials available for past 3 years. Strong cash conversion."
    ),
)

if __name__ == "__main__":
    for deal in [ACME_DEAL, CLEAN_DEAL]:
        print(f"\n{'='*60}")
        print(f"DEAL ROOM ANALYSIS: {deal.company_name}")
        print("=" * 60)
        result = run(deal)

        if not result.completed:
            print(f"PIPELINE HALTED at stage: {result.escalation.stage}")
            print(f"Confidence: {result.escalation.confidence:.2f} (threshold: {result.escalation.threshold})")
            print(f"Reason: {result.escalation.reason}")
        else:
            print(f"RECOMMENDATION: {result.board_memo.recommended_position.upper()}")
            print(f"\nVerdict: {result.board_memo.one_sentence_verdict}")
            print("\nKey Risks:")
            for risk in result.board_memo.key_risks:
                print(f"  • {risk}")
            if result.board_memo.conditions_to_proceed:
                print("\nConditions to Proceed:")
                for cond in result.board_memo.conditions_to_proceed:
                    print(f"  • {cond}")
            print(f"\nPipeline Confidence: {result.board_memo.confidence:.2f}")
            print(f"\nExecutive Summary:\n{result.board_memo.executive_summary}")
