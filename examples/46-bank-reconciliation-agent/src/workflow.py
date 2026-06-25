"""Workflow entrypoint for the Bank Reconciliation Agent.

Uses the raw OpenAI SDK (no LangGraph).  Deterministic pre-matching handles
exact and probable pairs; the LLM classifies only genuinely unmatched items.
"""

import json
import os
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from .calculator import find_matches
from .prompts import RECON_SYSTEM
from .schema import BankReconciliationSummary, MatchedPair, UnmatchedItem

load_dotenv()


class _UnmatchedClassification(BaseModel):
    """Internal structured-output container for the LLM response."""

    items: List[UnmatchedItem]


def run(
    bank_txns: List[Dict],
    gl_entries: List[Dict],
    period: str,
    bank_closing_balance: float,
    gl_cash_balance: float,
    model: str = "gpt-4.1-nano",
) -> BankReconciliationSummary:
    """Run the full bank reconciliation and return a summary.

    Args:
        bank_txns: Raw bank transactions as dicts (txn_id, date, description, debit, credit).
        gl_entries: Raw GL entries as dicts (entry_id, date, reference, amount, description).
        period: Human-readable accounting period label, e.g. "June 2025".
        bank_closing_balance: Closing balance from the bank statement.
        gl_cash_balance: Cash account balance from the General Ledger.
        model: OpenAI model identifier to use for exception classification.

    Returns:
        A completed BankReconciliationSummary.
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # Step 1 — deterministic pre-matching
    matched_raw, unmatched_bank, unmatched_gl = find_matches(bank_txns, gl_entries)

    # Step 2 — build matched pairs
    matched_pairs = [MatchedPair(**m) for m in matched_raw]

    # Step 3 — classify unmatched items via LLM (only if there are any)
    unmatched_items: List[UnmatchedItem] = []
    if unmatched_bank or unmatched_gl:
        context_payload = {
            "unmatched_bank_transactions": unmatched_bank,
            "unmatched_gl_entries": unmatched_gl,
        }
        user_message = (
            f"Period: {period}\n"
            f"Bank closing balance: {bank_closing_balance}\n"
            f"GL cash balance: {gl_cash_balance}\n\n"
            f"Unmatched items to classify:\n"
            f"{json.dumps(context_payload, indent=2)}"
        )

        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": RECON_SYSTEM},
                {"role": "user", "content": user_message},
            ],
            response_format=_UnmatchedClassification,
        )
        classification = response.choices[0].message.parsed
        if classification is not None:
            unmatched_items = classification.items

    # Step 4 — compute reconciling items value (timing differences only)
    reconciling_items_value = sum(
        item.amount if item.source == "bank" else -item.amount
        for item in unmatched_items
        if item.exception_type == "timing_difference"
    )

    # Step 5 — determine reconciliation status
    gap = abs(bank_closing_balance - gl_cash_balance - reconciling_items_value)
    is_reconciled = gap <= 0.01

    if is_reconciled:
        note = (
            f"Reconciliation complete for {period}. "
            f"Bank balance {bank_closing_balance:,.2f} reconciles to GL balance "
            f"{gl_cash_balance:,.2f} after {len(unmatched_items)} exception item(s)."
        )
    else:
        note = (
            f"Reconciliation INCOMPLETE for {period}. "
            f"Unexplained difference of {gap:,.2f} remains after classifying exceptions. "
            f"Review unmatched items and adjust GL entries as required."
        )

    return BankReconciliationSummary(
        period=period,
        bank_closing_balance=bank_closing_balance,
        gl_cash_balance=gl_cash_balance,
        matched_pairs=matched_pairs,
        unmatched_items=unmatched_items,
        reconciling_items_value=reconciling_items_value,
        is_reconciled=is_reconciled,
        reconciliation_note=note,
    )
