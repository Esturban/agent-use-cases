"""Workflow for the AR Collection Agent.

Implements an aging-bucket state machine:
  - _get_bucket: deterministic classification of days_overdue into an aging bucket
  - _priority_score: deterministic urgency score (1-10) from overdue days and amount
  - _credit_hold: deterministic hold recommendation from overdue threshold and exposure ratio
  - run: orchestrates all customers, invokes LLM per non-trivial tier, returns CollectionPlan

The bucket assignment and priority scoring are fully deterministic.
The LLM is invoked only for tiers that require a collection letter, with a
different SystemMessage per tier to calibrate tone.
"""

import os
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from .prompts import BUCKET_MAPPING, ESCALATION_PROMPTS
from .schema import ARCustomer, CollectionAction, CollectionPlan

load_dotenv()


# ---------------------------------------------------------------------------
# Deterministic helper functions
# ---------------------------------------------------------------------------


def _get_bucket(days_overdue: int) -> str:
    """Map days overdue to an aging bucket string.

    Args:
        days_overdue: Number of calendar days past the invoice due date.

    Returns:
        One of: 'current', '1_30', '31_60', '61_90', '90_plus'.
    """
    if days_overdue <= 0:
        return "current"
    if days_overdue <= 30:
        return "1_30"
    if days_overdue <= 60:
        return "31_60"
    if days_overdue <= 90:
        return "61_90"
    return "90_plus"


def _priority_score(customer: ARCustomer) -> int:
    """Calculate a priority score from 1 (low) to 10 (high).

    Score is derived from days_overdue and outstanding_amount:
      base = days_overdue / 10 + outstanding_amount / 5000

    Clamped to [1, 10].

    Args:
        customer: The AR customer record.

    Returns:
        Integer priority score between 1 and 10 inclusive.
    """
    raw = customer.days_overdue / 10 + customer.outstanding_amount / 5000
    return min(10, max(1, int(raw)))


def _credit_hold(customer: ARCustomer) -> Tuple[bool, Optional[str]]:
    """Determine whether a credit hold should be recommended.

    A hold is recommended when either condition is met:
      - days_overdue > 90 (severely delinquent)
      - total_exposure > 80% of credit_limit (high credit utilisation)

    Args:
        customer: The AR customer record.

    Returns:
        Tuple of (recommend_hold: bool, rationale: Optional[str]).
        rationale is None when hold is not recommended.
    """
    reasons: List[str] = []
    if customer.days_overdue > 90:
        reasons.append(f"account is {customer.days_overdue} days overdue (threshold: 90 days)")
    exposure_ratio = (
        customer.total_exposure / customer.credit_limit if customer.credit_limit > 0 else 0.0
    )
    if exposure_ratio > 0.8:
        pct = round(exposure_ratio * 100, 1)
        reasons.append(
            f"total exposure is {pct}% of credit limit "
            f"(${customer.total_exposure:,.2f} / ${customer.credit_limit:,.2f})"
        )
    if reasons:
        return True, "Credit hold recommended: " + "; ".join(reasons) + "."
    return False, None


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------


def run(
    customers: List[ARCustomer],
    as_of_date: str,
    model: str = "gpt-4.1-nano",
) -> CollectionPlan:
    """Run the AR collection agent over a list of customers.

    For each customer:
      1. Assigns an aging bucket deterministically from days_overdue.
      2. Maps the bucket to an escalation tier via BUCKET_MAPPING.
      3. For tiers with a collection letter, invokes the LLM with the
         corresponding ESCALATION_PROMPTS SystemMessage.
      4. Scores priority and evaluates credit hold eligibility.

    Returns a CollectionPlan sorted by priority_score descending.

    Args:
        customers: List of ARCustomer records to process.
        as_of_date: The run date string (YYYY-MM-DD) for the plan header.
        model: LangChain-compatible model identifier (default gpt-4.1-nano).

    Returns:
        A fully populated CollectionPlan.
    """
    llm = ChatOpenAI(
        model=model,
        temperature=0.3,
        api_key=os.environ["OPENAI_API_KEY"],
    )

    actions: List[CollectionAction] = []

    for customer in customers:
        bucket = _get_bucket(customer.days_overdue)
        tier = BUCKET_MAPPING[bucket]
        score = _priority_score(customer)
        hold, rationale = _credit_hold(customer)

        if tier == "no_action":
            letter = "No action required."
        else:
            system_msg = ESCALATION_PROMPTS[tier]
            user_content = (
                f"Customer: {customer.customer_name} (ID: {customer.customer_id})\n"
                f"Invoice: {customer.invoice_number}\n"
                f"Invoice date: {customer.invoice_date}\n"
                f"Due date: {customer.due_date}\n"
                f"Outstanding amount: {customer.currency} {customer.outstanding_amount:,.2f}\n"
                f"Days overdue: {customer.days_overdue}\n"
                f"Prior contact attempts: {customer.prior_contact_count}\n"
                f"Total exposure: {customer.currency} {customer.total_exposure:,.2f}\n"
                f"Credit limit: {customer.currency} {customer.credit_limit:,.2f}\n"
            )
            chain = system_msg | llm
            response = chain.invoke({"messages": [{"role": "user", "content": user_content}]})
            letter = response.content if hasattr(response, "content") else str(response)

        actions.append(
            CollectionAction(
                customer_id=customer.customer_id,
                aging_bucket=bucket,
                escalation_tier=tier,
                collection_letter=letter,
                credit_hold_recommended=hold,
                credit_hold_rationale=rationale,
                priority_score=score,
            )
        )

    actions.sort(key=lambda a: a.priority_score, reverse=True)

    total_ar = sum(c.outstanding_amount for c in customers)
    credit_hold_count = sum(1 for a in actions if a.credit_hold_recommended)
    legal_referral_count = sum(1 for a in actions if a.escalation_tier == "legal_referral")

    tier_counts: dict = {}
    for a in actions:
        tier_counts[a.escalation_tier] = tier_counts.get(a.escalation_tier, 0) + 1

    tier_summary = ", ".join(
        f"{count} {tier.replace('_', ' ')}"
        for tier, count in sorted(tier_counts.items())
    )
    summary = (
        f"AR collection plan as of {as_of_date}. "
        f"Total outstanding: {customers[0].currency if customers else 'USD'} {total_ar:,.2f} "
        f"across {len(customers)} accounts. "
        f"Tier breakdown: {tier_summary}. "
        f"Credit holds recommended: {credit_hold_count}. "
        f"Legal referrals: {legal_referral_count}. "
        f"Prioritise accounts with scores 8-10 for immediate follow-up."
    )

    return CollectionPlan(
        as_of_date=as_of_date,
        total_ar_outstanding=total_ar,
        actions=actions,
        credit_hold_count=credit_hold_count,
        legal_referral_count=legal_referral_count,
        collection_summary=summary,
    )
