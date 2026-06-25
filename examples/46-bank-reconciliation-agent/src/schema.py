"""Schema definitions for the Bank Reconciliation Agent."""

from typing import List, Literal

from pydantic import BaseModel, Field


class BankTransaction(BaseModel):
    """A single transaction from the bank statement."""

    txn_id: str = Field(description="Unique identifier for the bank transaction")
    date: str = Field(description="Transaction date in YYYY-MM-DD format")
    description: str = Field(description="Narrative text from the bank statement")
    debit: float = Field(default=0.0, description="Amount debited from the account (outflow)")
    credit: float = Field(default=0.0, description="Amount credited to the account (inflow)")


class GLEntry(BaseModel):
    """A single entry in the General Ledger cash account."""

    entry_id: str = Field(description="Unique identifier for the GL entry")
    date: str = Field(description="Posting date in YYYY-MM-DD format")
    reference: str = Field(description="Journal reference or voucher number")
    amount: float = Field(
        description="Signed amount: positive = debit to cash, negative = credit to cash"
    )
    description: str = Field(description="GL narrative or journal memo")


class MatchedPair(BaseModel):
    """A confirmed match between a bank transaction and a GL entry."""

    bank_txn_id: str = Field(description="ID of the matched bank transaction")
    gl_entry_id: str = Field(description="ID of the matched GL entry")
    match_confidence: Literal["exact", "probable", "fuzzy"] = Field(
        description=(
            "Confidence level: exact=same amount+date, "
            "probable=same amount within 2 days, "
            "fuzzy=LLM-assisted match"
        )
    )


class UnmatchedItem(BaseModel):
    """An item that could not be matched, requiring human review."""

    item_id: str = Field(description="ID of the unmatched transaction or GL entry")
    source: Literal["bank", "gl"] = Field(
        description="Origin of the unmatched item: bank statement or GL"
    )
    amount: float = Field(description="Absolute value of the unmatched amount")
    description: str = Field(description="Narrative from the source record")
    exception_type: Literal[
        "timing_difference",
        "bank_charge",
        "duplicate",
        "missing_booking",
        "fraud_indicator",
    ] = Field(
        description=(
            "Classification: timing_difference=deposit in transit or outstanding cheque, "
            "bank_charge=bank fee with no GL counterpart, "
            "duplicate=same amount+date appearing twice, "
            "missing_booking=bank entry has no GL counterpart, "
            "fraud_indicator=unusual item with no business explanation"
        )
    )
    recommended_action: str = Field(
        description="Specific action the accountant should take to resolve this item"
    )


class BankReconciliationSummary(BaseModel):
    """Full reconciliation output for a given period."""

    period: str = Field(description="Accounting period being reconciled, e.g. June 2025")
    bank_closing_balance: float = Field(
        description="Closing balance per the bank statement"
    )
    gl_cash_balance: float = Field(
        description="Cash account balance per the General Ledger"
    )
    matched_pairs: List[MatchedPair] = Field(
        description="All matched bank-GL pairs found by the reconciliation engine"
    )
    unmatched_items: List[UnmatchedItem] = Field(
        description="Items that could not be matched and require review or adjustment"
    )
    reconciling_items_value: float = Field(
        description=(
            "Net value of timing differences that explain the gap between "
            "bank balance and GL balance"
        )
    )
    is_reconciled: bool = Field(
        description=(
            "True when bank_closing_balance minus reconciling_items_value "
            "equals gl_cash_balance within 0.01 tolerance"
        )
    )
    reconciliation_note: str = Field(
        description="Summary narrative describing the reconciliation outcome"
    )
