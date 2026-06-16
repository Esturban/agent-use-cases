from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from .schema import LeadScore

ICP_RUBRIC = SystemMessage("""
You are a sales qualification assistant. Score inbound leads against this ICP rubric.

IDEAL CUSTOMER PROFILE (ICP):
  Industry:      SaaS, FinTech, or E-commerce
  Company size:  50–500 employees
  Pain point:    manual workflows, data silos, or compliance burden
  Buyer role:    VP Operations, CFO, or CTO
  Budget signal: existing software spend > $5k/month

SCORING:
  8–10 → hot   (3+ criteria met, strong pain + budget signal)
  5–7  → warm  (2 criteria met, or strong pain but budget unclear)
  1–4  → cold  (fewer than 2 criteria met)

Rules:
- Populate criteria_met and criteria_missed by naming the exact ICP criteria above.
- reasoning must explain the score in one or two sentences citing the criteria.
- Never invent data not present in the lead description.
""")


def create_workflow():
    """Return a runnable that scores a lead description against the ICP rubric."""
    llm = ChatOpenAI(model="gpt-4o-mini")
    return ICP_RUBRIC | llm.with_structured_output(LeadScore)
