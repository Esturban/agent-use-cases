from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = Field(description="Description of the goods or service.")
    quantity: float = Field(description="Number of units.")
    unit_price: float = Field(description="Price per unit in the invoice currency.")
    total: float = Field(description="Line total (quantity × unit_price).")


class Invoice(BaseModel):
    vendor: str = Field(description="Name of the company or individual issuing the invoice.")
    invoice_number: str = Field(description="Invoice reference number or ID.")
    invoice_date: str = Field(description="Date the invoice was issued (YYYY-MM-DD if parseable, else raw string).")
    due_date: str = Field(description="Payment due date (YYYY-MM-DD if parseable, else raw string).")
    currency: str = Field(description="Three-letter ISO currency code (e.g. USD, EUR, GBP).")
    subtotal: float = Field(description="Sum of all line item totals before tax.")
    tax: float = Field(description="Total tax amount. Use 0.0 if not stated.")
    total_due: float = Field(description="Total amount due including tax.")
    line_items: list[LineItem] = Field(description="List of individual line items on the invoice.")
