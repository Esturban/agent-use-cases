from dotenv import load_dotenv

from src.workflow import create_workflow

load_dotenv()

SAMPLE_EMAIL = """
Subject: URGENT - Invoice #4821 overdue 30 days, account suspended
From: accounts@acme-corp.com

Hi team, our account has been suspended due to unpaid invoice #4821 ($4,200).
Payment was due May 1st -- now 30 days overdue.
We need this resolved immediately or we lose access to production systems.
Please escalate ASAP.
"""


def main():
    classifier = create_workflow()
    result = classifier.invoke(SAMPLE_EMAIL)
    print(f"Urgency:  {result.urgency}")
    print(f"Category: {result.category}")
    print(f"Summary:  {result.summary}")
    print(f"Action:   {result.recommended_action}")


if __name__ == "__main__":
    main()
