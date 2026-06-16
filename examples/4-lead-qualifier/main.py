from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.workflow import create_workflow

load_dotenv()

SAMPLE_LEAD = """
Company:  Meridian Payments
Industry: FinTech
Size:     120 employees
Contact:  Sarah Chen, VP of Operations

Notes:
Sarah mentioned their team is reconciling invoices manually across three
spreadsheets and it's costing them ~15 hours a week. They currently pay
around $8k/month across various SaaS tools and are looking to consolidate
before Q3. Budget for the right solution is $2k–4k/month.
"""


def main():
    qualifier = create_workflow()
    result = qualifier.invoke(HumanMessage(SAMPLE_LEAD))

    print(f"Company:  {result.company}")
    print(f"Score:    {result.score}/10  →  {result.tier.upper()}")
    print(f"Action:   {result.recommended_action}")
    print(f"\nCriteria met:    {', '.join(result.criteria_met)}")
    print(f"Criteria missed: {', '.join(result.criteria_missed) or 'none'}")
    print(f"\nReasoning: {result.reasoning}")


if __name__ == "__main__":
    main()
