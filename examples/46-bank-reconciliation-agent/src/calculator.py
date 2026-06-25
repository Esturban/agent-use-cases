"""Deterministic pre-matcher for bank reconciliation.

Pass 1 — exact match: same absolute amount AND same date.
Pass 2 — probable match: same absolute amount AND date within 2 calendar days.

Items that survive both passes are returned as unmatched for LLM classification.
"""

from datetime import datetime
from typing import Dict, List, Tuple


def date_diff_days(d1: str, d2: str) -> int:
    """Return the absolute number of calendar days between two YYYY-MM-DD strings."""
    fmt = "%Y-%m-%d"
    return abs((datetime.strptime(d1, fmt) - datetime.strptime(d2, fmt)).days)


def amounts_match(a: float, b: float, tol: float = 0.01) -> bool:
    """Return True when two amounts are equal within the given tolerance."""
    return abs(abs(a) - abs(b)) <= tol


def find_matches(
    bank_txns: List[Dict],
    gl_entries: List[Dict],
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Match bank transactions against GL entries deterministically.

    Args:
        bank_txns: List of dicts with keys txn_id, date, description, debit, credit.
        gl_entries: List of dicts with keys entry_id, date, reference, amount, description.

    Returns:
        A tuple of (matched_raw, unmatched_bank, unmatched_gl) where:
        - matched_raw is a list of dicts with bank_txn_id, gl_entry_id, match_confidence.
        - unmatched_bank is the list of bank txns that found no GL counterpart.
        - unmatched_gl is the list of GL entries that found no bank counterpart.
    """
    matched_raw: List[Dict] = []
    used_bank: set = set()
    used_gl: set = set()

    def _bank_amount(txn: Dict) -> float:
        """Return the signed net amount for a bank transaction (credit - debit)."""
        return txn.get("credit", 0.0) - txn.get("debit", 0.0)

    # Pass 1 — exact match (same amount, same date)
    for bank in bank_txns:
        for gl in gl_entries:
            if bank["txn_id"] in used_bank or gl["entry_id"] in used_gl:
                continue
            if amounts_match(_bank_amount(bank), gl["amount"]) and bank["date"] == gl["date"]:
                matched_raw.append(
                    {
                        "bank_txn_id": bank["txn_id"],
                        "gl_entry_id": gl["entry_id"],
                        "match_confidence": "exact",
                    }
                )
                used_bank.add(bank["txn_id"])
                used_gl.add(gl["entry_id"])
                break

    # Pass 2 — probable match (same amount, within 2 days)
    for bank in bank_txns:
        if bank["txn_id"] in used_bank:
            continue
        for gl in gl_entries:
            if gl["entry_id"] in used_gl:
                continue
            if amounts_match(_bank_amount(bank), gl["amount"]) and date_diff_days(
                bank["date"], gl["date"]
            ) <= 2:
                matched_raw.append(
                    {
                        "bank_txn_id": bank["txn_id"],
                        "gl_entry_id": gl["entry_id"],
                        "match_confidence": "probable",
                    }
                )
                used_bank.add(bank["txn_id"])
                used_gl.add(gl["entry_id"])
                break

    unmatched_bank = [b for b in bank_txns if b["txn_id"] not in used_bank]
    unmatched_gl = [g for g in gl_entries if g["entry_id"] not in used_gl]

    return matched_raw, unmatched_bank, unmatched_gl
