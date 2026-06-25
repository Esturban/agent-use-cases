"""AP invoice schemas for 3-way match pipeline."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class InvoiceLine(BaseModel):
    """A single line item on a vendor invoice."""

    description: str = Field(description="Line item description")
    quantity: float = Field(description="Quantity of units billed", gt=0)
    unit_price: float = Field(description="Price per unit in invoice currency", gt=0)
    line_total: float = Field(description="Total for this line (quantity * unit_price)", gt=0)


class ExtractedInvoice(BaseModel):
    """Structured invoice data extracted from free-text invoice content."""

    vendor_id: str = Field(description="Vendor identifier e.g. ACME-001")
    invoice_number: str = Field(description="Unique invoice number from the vendor")
    invoice_date: str = Field(description="Invoice date in YYYY-MM-DD format")
    po_reference: str = Field(description="Purchase order reference e.g. PO-2025-001")
    total_amount: float = Field(description="Total invoice amount in currency", gt=0)
    currency: str = Field(default="USD", description="ISO 4217 currency code e.g. USD")
    lines: List[InvoiceLine] = Field(description="Line items on the invoice")


class Discrepancy(BaseModel):
    """A single discrepancy found during 3-way match."""

    discrepancy_type: Literal[
        "quantity_short",
        "price_variance",
        "duplicate",
        "gr_missing",
        "po_not_found",
    ] = Field(description="Category of discrepancy detected")
    field: str = Field(description="The field or dimension where the discrepancy exists")
    invoice_value: str = Field(description="Value as stated on the invoice")
    expected_value: str = Field(description="Value from the PO or GR record")
    variance_pct: Optional[float] = Field(
        default=None,
        description="Percentage variance where applicable e.g. 5.3 means 5.3%",
    )
    severity: Literal["info", "warn", "block"] = Field(
        description="info=no action needed, warn=review required, block=do not pay"
    )


class MatchResult(BaseModel):
    """Output of the 3-way match evaluation for one invoice."""

    invoice_number: str = Field(description="Invoice number being evaluated")
    po_reference: str = Field(description="PO reference used in the match")
    match_status: Literal["clean", "discrepancy", "blocked"] = Field(
        description="clean=no issues, discrepancy=warn-level issues only, blocked=block-level issues present"
    )
    discrepancies: List[Discrepancy] = Field(
        default_factory=list,
        description="List of all discrepancies found; empty when match_status is clean",
    )
    approval_tier: Literal[
        "auto_approve",
        "line_manager",
        "finance_controller",
        "vp_finance",
    ] = Field(
        description=(
            "Approval routing: "
            "auto_approve=clean+total<10000, "
            "line_manager=warn+total<25000, "
            "finance_controller=warn+total>=25000 or block+total<50000, "
            "vp_finance=block+total>=50000"
        )
    )
    approval_rationale: str = Field(
        description="One-sentence explanation of why this approval tier was selected"
    )
