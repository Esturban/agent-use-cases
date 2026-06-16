from typing import List

from pydantic import BaseModel, field_validator


class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float


class Invoice(BaseModel):
    vendor: str
    invoice_number: str
    date: str          # ISO format: YYYY-MM-DD
    subtotal: float
    tax: float
    total_amount: float
    line_items: List[LineItem]

    @field_validator("total_amount")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("total_amount must be positive")
        return v
