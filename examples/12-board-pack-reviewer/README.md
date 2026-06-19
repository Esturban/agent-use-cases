# 12 — Board Pack Reviewer

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Esturban/agent-use-cases/blob/main/examples/12-board-pack-reviewer/board_pack_workbook.ipynb)

Non-executive directors often receive board packs hours before a meeting with no independent analysis. This agent reads the full pack and produces a pre-meeting briefing that ranks risks, names information gaps, and drafts probing questions — so a NED walks in prepared rather than reliant on management's framing.

---

## What it does

A board pack (CEO update, financials, acquisition proposals, audit committee reports) is passed to the agent as plain text. The agent reads it as a sceptical non-executive director would: looking for what the pack does not say as much as what it does. It returns a structured briefing with ranked risks by severity and area, explicit gaps where material information is absent, a list of decisions the board is being asked to approve, and suggested questions a director should put to management.

---

## How it works

The agent is instructed to reason like a NED — not to summarise management's narrative, but to independently assess governance risk. Each risk finding must cite which section of the pack it comes from, so the director can verify it during the meeting. Information gaps are surfaced as a separate output field rather than buried in prose, because a gap in disclosure is itself a governance concern. Decisions requiring board approval are isolated with the single most important consideration a director must weigh before voting.

---

## What you'll see

```
=================================================================
DIRECTOR BRIEFING | Pack quality: WEAK
=================================================================

This pack presents serious governance concerns that the board must
address before approving any of the items on the agenda. Leverage
sits at 3.5x EBITDA with interest cover at 2.1x against a 2.0x
covenant — a margin of error of 0.1x. KPMG has flagged a going
concern emphasis of matter and yet management proposes a GBP 95m
acquisition and a maintained dividend with no funding plan provided.
The whistleblower investigation into procurement is unresolved and
underdisclosed. The board should not approve the acquisition today.

TOP RISKS (5):

  [1] [CRIT] [FINANCIAL] Going concern risk with covenant breach exposure
      Source: Item 3 — Financial Performance
      Interest cover of 2.1x sits 0.1x above the 2.0x minimum covenant.
      KPMG has flagged a going concern paragraph in the draft audit opinion.
      Q: What headroom assumptions underpin KPMG's going concern assessment
         and what triggers a covenant breach?

  [2] [CRIT] [STRATEGIC] Acquisition approval without integration or funding plan
      Source: Item 4 — Proposed Acquisition
      GBP 95m at 45x EV/EBITDA with no synergy case, no integration plan,
      and no confirmed financing — on a balance sheet at 3.5x leverage.
      Q: How does management intend to fund this acquisition and what
         is the pro-forma leverage position post-close?

  [3] [HIGH] [REGULATORY] ICO investigation following 180,000-record data breach
      Source: Item 5 — Audit & Risk Committee Report
      Customer payment data was exposed in November 2024. Regulatory outcome
      is pending with maximum GDPR exposure of up to 4% of global turnover.
      Q: What is the realistic range of ICO penalty and has external counsel
         assessed the likelihood of enforcement action?

INFORMATION GAPS (3):

  [Item 4] No integration plan or synergy case for FreshLocal acquisition
  Why it matters: The board cannot approve a GBP 95m deal without knowing
  how or whether value will be created post-close.

  [Item 3] No Q1 gross margin data provided
  Why it matters: Margin trajectory determines whether FY2025 covenant
  headroom is improving or deteriorating.

  [Item 5] Whistleblower investigation status undisclosed
  Why it matters: Procurement irregularities could affect financial
  statements already flagged as unaudited.

DECISIONS REQUIRED (2):

  DECISION: Approve FreshLocal Ltd acquisition in principle
  Context: GBP 95m consideration at 45x EV/EBITDA; unaudited financials
  Management recommends: Approval subject to due diligence and financing
  Key consideration: The board has no funding plan and no integration case.

  DECISION: Approve full-year dividend of 12p per share
  Context: Proposed while leverage is 3.5x and going concern is flagged
  Key consideration: Paying a dividend while auditors flag going concern
  risk may be difficult to defend to shareholders.

SUGGESTED QUESTIONS FOR MANAGEMENT:
  1. What is the precise covenant headroom and what scenario triggers a breach?
  2. Why is the board being asked to approve an acquisition without a funding plan?
  3. What is the current status of the KPMG going concern discussion?
  4. Can the whistleblower investigation be summarised before the board votes?
```

---

## How to run

```bash
# Requires OPENAI_API_KEY in .env
python examples/12-board-pack-reviewer/main.py
```

---

## Files

```
12-board-pack-reviewer/
  src/schema.py      # DirectorBriefing, TopRisk, InformationGap, DecisionRequired Pydantic models
  src/workflow.py    # NED-framed system prompt and structured extraction call
  main.py            # Synthetic Nexus Retail Group PLC board pack and formatted output
  README.md
```
