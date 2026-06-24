"""Mock purchase order and goods receipt data for 3-way match lookups."""

from typing import Optional

PURCHASE_ORDERS: dict = {
    "PO-2025-001": {
        "po_number": "PO-2025-001",
        "vendor_id": "ACME-001",
        "description": "Cloud server hardware (4 units)",
        "quantity": 4,
        "unit_price": 2100.00,
        "total_value": 8400.00,
        "currency": "USD",
    },
    "PO-2025-002": {
        "po_number": "PO-2025-002",
        "vendor_id": "BETA-002",
        "description": "Office furniture (100 units)",
        "quantity": 100,
        "unit_price": 150.00,
        "total_value": 15000.00,
        "currency": "USD",
    },
    "PO-2025-003": {
        "po_number": "PO-2025-003",
        "vendor_id": "GAMMA-003",
        "description": "Management consulting (75 hours)",
        "quantity": 75,
        "unit_price": 375.00,
        "total_value": 28125.00,
        "currency": "USD",
    },
    "PO-2025-004": {
        "po_number": "PO-2025-004",
        "vendor_id": "DELTA-004",
        "description": "Enterprise software licences (50 seats)",
        "quantity": 50,
        "unit_price": 440.00,
        "total_value": 22000.00,
        "currency": "USD",
    },
}

GOODS_RECEIPTS: dict = {
    "PO-2025-001": {
        "po_number": "PO-2025-001",
        "qty_received": 4,
        "receipt_date": "2025-06-10",
        "notes": "All units received and inspected",
    },
    "PO-2025-002": {
        "po_number": "PO-2025-002",
        "qty_received": 85,
        "receipt_date": "2025-06-12",
        "notes": "15 units on back-order, expected 2025-07-01",
    },
    # PO-2025-003 intentionally absent — no GR recorded for consulting
    "PO-2025-004": {
        "po_number": "PO-2025-004",
        "qty_received": 50,
        "receipt_date": "2025-06-14",
        "notes": "Licence keys delivered electronically",
    },
}


def lookup_po(po_number: str) -> Optional[dict]:
    """Return the purchase order record for po_number, or None if not found."""
    return PURCHASE_ORDERS.get(po_number)


def lookup_gr(po_number: str) -> Optional[dict]:
    """Return the goods receipt record for po_number, or None if not found."""
    return GOODS_RECEIPTS.get(po_number)
