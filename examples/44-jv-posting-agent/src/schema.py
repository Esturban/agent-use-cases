"""Journal entry schemas."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class JournalLine(BaseModel):
    side: Literal["debit", "credit"] = Field(description="Debit or credit side")
    account_code: str = Field(description="4-digit GL account code e.g. '2100'")
    account_name: str = Field(description="Human-readable GL account name")
    amount: float = Field(description="Positive posting amount", gt=0)
    cost_centre: Optional[str] = Field(
        default=None, description="Cost centre e.g. CC1001"
    )


class PostingRequest(BaseModel):
    event_description: str
    document_type: Literal["SA", "KR", "DR", "ZP", "AB", "AA", "RE"] = Field(
        description=(
            "SA=GL adj, KR=vendor invoice, DR=customer invoice, "
            "ZP=payment, AB=depreciation, AA=asset, RE=accrual"
        )
    )
    amount: float = Field(gt=0)
    cost_centre: Optional[str] = None
    period: str = Field(description="Period YYYY-MM")


class PostingResult(BaseModel):
    lines: List[JournalLine]
    is_balanced: bool
    total_debits: float
    total_credits: float
    posting_status: Literal["approved", "rejected", "needs_review"]
    rejection_reason: Optional[str] = None
