from dotenv import load_dotenv

from src.workflow import create_workflow

load_dotenv()

EMAILS = [
    (
        "Overdue invoice",
        """Subject: URGENT - Invoice #4821 overdue 30 days, account suspended
From: accounts@acme-corp.com

Hi team, our account has been suspended due to unpaid invoice #4821 ($4,200).
Payment was due May 1st -- now 30 days overdue.
We need this resolved immediately or we lose access to production systems.
Please escalate ASAP.""",
    ),
    (
        "Production outage",
        """Subject: ALERT: Production database unreachable - all services down
From: monitoring@internal.co

Our monitoring system detected that db-prod-01 is not responding.
All customer-facing services are returning 503 errors.
Engineering has been paged. Estimated impact: 2,000 active sessions.""",
    ),
    (
        "Compliance notice",
        """Subject: GDPR data subject access request - 30-day deadline
From: legal@regulator.eu

We have received a formal data subject access request under GDPR Article 15.
You are required to provide the requested data within 30 days of this notice.
Failure to comply may result in regulatory enforcement action.""",
    ),
    (
        "Feature request",
        """Subject: Idea - dark mode for the dashboard
From: alex.chen@customer.com

Hey, love the product! One thing that would really help is a dark mode option
for the main dashboard. A lot of us use it late at night and the bright white
is pretty hard on the eyes. No rush, just a thought.""",
    ),
    (
        "Marketing spam",
        """Subject: EXCLUSIVE OFFER - 80% off enterprise plan, TODAY ONLY!!!
From: deals@saas-blaster.io

Don't miss out on our BIGGEST SALE EVER. Upgrade now and save thousands.
Limited spots available. Click here to claim your discount before midnight.
Unsubscribe | Terms | Privacy""",
    ),
]


def main():
    classifier = create_workflow()
    print(f"{'LABEL':<22} {'URGENCY':<10} {'CATEGORY':<14} SUMMARY")
    print("-" * 90)
    for label, email in EMAILS:
        result = classifier.invoke(email)
        print(
            f"{label:<22} {result.urgency:<10} {result.category:<14}"
            f" {result.summary[:40]}"
        )


if __name__ == "__main__":
    main()
