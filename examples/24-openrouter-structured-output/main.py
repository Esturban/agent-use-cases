from dotenv import load_dotenv

from src.workflow import classify

load_dotenv()

EMAILS = [
    (
        "Overdue invoice",
        """Subject: URGENT - Invoice #4821 overdue 30 days, account suspended
From: accounts@acme-corp.com

Our account has been suspended due to unpaid invoice #4821 ($4,200).
Payment was due May 1st -- now 30 days overdue.
We need this resolved immediately or we lose access to production systems.""",
    ),
    (
        "Feature request",
        """Subject: Idea - dark mode for the dashboard
From: alex.chen@customer.com

Hey, love the product! One thing that would really help is a dark mode option
for the main dashboard. A lot of us use it late at night and the bright white
is hard on the eyes. No rush, just a thought.""",
    ),
    (
        "Security alert",
        """Subject: Unusual login detected on your account
From: security@platform.io

We detected a login from an unrecognised IP address (185.220.101.47, Romania).
If this was not you, please reset your password and enable 2FA immediately.
Your account may be compromised.""",
    ),
    (
        "Vendor newsletter",
        """Subject: Our Q3 product updates and what's coming next quarter
From: news@saas-vendor.com

Hi there! We've shipped 12 improvements this quarter including faster exports,
new integrations, and an overhauled onboarding flow. Read the full changelog
on our blog. See you next quarter!""",
    ),
]


def main() -> None:
    print(f"{'LABEL':<22} {'URGENCY':<10} {'CATEGORY':<14} SUMMARY")
    print("-" * 90)
    for label, email in EMAILS:
        result = classify(email)
        print(
            f"{label:<22} {result.urgency:<10} {result.category:<14}"
            f" {result.summary[:40]}"
        )
        print(f"{'':>46} Action: {result.recommended_action[:40]}")
        print()


if __name__ == "__main__":
    main()
