"""Entry point — runs four business events through the JV posting agent."""

import os

from dotenv import load_dotenv

from src.schema import PostingRequest
from src.workflow import run

load_dotenv()


EVENTS = [
    PostingRequest(
        event_description="Received IT equipment invoice from Dell, capitalise as fixed asset",
        document_type="AA",
        amount=12500.00,
        cost_centre="CC5001",
        period="2025-06",
    ),
    PostingRequest(
        event_description=(
            "Accrue June salary expense for finance department, not yet paid"
        ),
        document_type="RE",
        amount=45000.00,
        cost_centre="CC2001",
        period="2025-06",
    ),
    PostingRequest(
        event_description=(
            "Customer payment received for outstanding invoice INV-2025-0441"
        ),
        document_type="ZP",
        amount=8750.00,
        cost_centre=None,
        period="2025-06",
    ),
    PostingRequest(
        event_description="Monthly depreciation run for vehicle fleet",
        document_type="AB",
        amount=1200.00,
        cost_centre="CC3001",
        period="2025-06",
    ),
]


def main():
    for req in EVENTS:
        result = run(req)
        print(f"\nEvent   : {req.event_description[:50]}")
        print(f"Status  : {result.posting_status.upper()}")
        print(f"Balanced: {result.is_balanced}")
        if result.rejection_reason:
            print(f"Reason  : {result.rejection_reason}")
        print(f"{'Side':<8} {'Code':<6} {'Account':<35} {'Amount':>10} {'CC'}")
        print("-" * 75)
        for line in result.lines:
            cc = line.cost_centre or ""
            print(
                f"{line.side:<8} {line.account_code:<6} {line.account_name:<35} "
                f"{line.amount:>10,.2f} {cc}"
            )
        print(f"\nTotal DR: ${result.total_debits:>10,.2f}")
        print(f"Total CR: ${result.total_credits:>10,.2f}")


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set — copy .env.example to .env")
    main()
