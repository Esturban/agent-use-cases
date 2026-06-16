from dotenv import load_dotenv

from src.workflow import run

load_dotenv()


SAMPLE_TICKETS = [
    {
        "subject": "Charged twice this month - invoice #4821",
        "body": (
            "Hi, I noticed my credit card was charged $99 twice on June 1st. "
            "Invoice #4821 shows a duplicate charge. Please refund the extra charge ASAP. "
            "This is really frustrating."
        ),
        "customer_name": "Sarah Chen",
        "customer_email": "schen@example.com",
    },
    {
        "subject": "Dashboard not loading - production down",
        "body": (
            "Our entire team cannot access the dashboard since 9 AM EST. "
            "We're getting a 502 error. This is blocking all our work. "
            "We're on the Enterprise plan."
        ),
        "customer_name": "Marcus Torres",
        "customer_email": "m.torres@bigcorp.com",
    },
    {
        "subject": "How do I add team members?",
        "body": "Hi, I'm trying to invite my colleagues to our workspace but I can't find where to do it. Can you help?",
        "customer_name": "Priya Patel",
        "customer_email": "priya@startup.io",
    },
]


def main():
    for ticket in SAMPLE_TICKETS:
        print(f"\n{'='*60}")
        print(f"TICKET: {ticket['subject']}")
        print(f"FROM:   {ticket['customer_name']}")
        print("=" * 60)

        result = run(ticket)
        clf = result["classification"]
        draft = result["draft"]

        print("\n[CLASSIFICATION]")
        print(f"  Type:       {clf['ticket_type']}")
        print(f"  Urgency:    {clf['urgency']}")
        print(f"  Team:       {clf['team']}")
        print(f"  Confidence: {clf['confidence']:.0%}")
        print(f"  Reasoning:  {clf['reasoning']}")

        print("\n[DRAFT REPLY]")
        print(f"  Subject:   {draft['subject']}")
        print(f"  Escalate:  {'YES' if draft['escalate'] else 'No'}")
        print("  Body:\n")
        for line in draft["body"].split("\n"):
            print(f"    {line}")
        print(f"\n  [Internal note]: {draft['internal_note']}")


if __name__ == "__main__":
    main()
