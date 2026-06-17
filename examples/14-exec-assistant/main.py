import os

from dotenv import load_dotenv

from src.workflow import run

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("Set OPENAI_API_KEY in .env")

SAMPLE_EMAIL_THREAD = """
From: Sarah Connor <s.connor@techcorp.com>
To: James Reed <j.reed@techcorp.com>; CEO <ceo@techcorp.com>
Cc: Legal <legal@techcorp.com>
Subject: RE: API Integration Deadline -- URGENT
Date: Monday 16 June 2025, 09:14

James / David,

Following up on the API integration with Vendor X. The original contractual
deadline was 1 June 2025. We are now 15 days past that date with no delivery.

As PM I have escalated twice internally but the engineering team says the
integration was deprioritised in the last sprint planning. We have a hard SLA
clause with Vendor X (5% monthly fee rebate per week of delay). Legal need to
advise on our exposure.

I need a decision on whether to escalate to the board or negotiate a revised
timeline with Vendor X directly.

-- Sarah

---

From: James Reed <j.reed@techcorp.com>
To: Sarah Connor <s.connor@techcorp.com>; CEO <ceo@techcorp.com>
Subject: RE: API Integration Deadline -- URGENT
Date: Monday 16 June 2025, 10:02

Sarah,

Acknowledged. The integration was moved out of the sprint because of the security
audit we were required to complete. I accept that communication was poor.

I can commit to restarting the integration work by Wednesday 18 June. We would
need 3 weeks from then -- revised delivery by 9 July 2025.

I suggest we set up a call with Vendor X this week to align on the new date
before any formal notification.

James (CTO)

---

From: David Okafor <ceo@techcorp.com>
To: James Reed <j.reed@techcorp.com>; Sarah Connor <s.connor@techcorp.com>
Cc: Legal <legal@techcorp.com>
Subject: RE: API Integration Deadline -- URGENT
Date: Monday 16 June 2025, 11:30

James and Sarah,

I need an update call with both of you this week -- Wednesday works for me.
Legal please advise on SLA exposure by EOD Tuesday.

David
"""

if __name__ == "__main__":
    result = run(SAMPLE_EMAIL_THREAD)

    print("=" * 65)
    print(f"EXEC ASSISTANT OUTPUT | Type: {result.input_type}")
    print("=" * 65)

    if result.subject_line:
        print(f"\nSubject: {result.subject_line}")

    print("\nDRAFT REPLY:")
    print(result.draft_reply)

    print(f"\nACTION ITEMS ({len(result.action_items)}):")
    for i, a in enumerate(result.action_items, 1):
        owner = a.owner or "TBC"
        due = a.due_date or "TBC"
        print(f"  {i}. [{a.priority.upper()}] {a.description}")
        print(f"     Owner: {owner} | Due: {due}")

    print(f"\nFOLLOW-UP TRACKER ({len(result.follow_up_tracker)}):")
    for f in result.follow_up_tracker:
        waiting = f.waiting_on or "TBC"
        check = f.check_in_by or "TBC"
        print(f"  - {f.topic}")
        print(f"    Waiting on: {waiting} | Check in by: {check}")
        print(f"    Notes: {f.notes}")
