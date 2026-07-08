"""Deterministic period-close control checks -- no LLM calls.

Each check mirrors the harness lesson from its originating example: JV
balance validation (id 44) and bank-statement matching (id 46) are pure
arithmetic, not model judgment; fixed-asset math, fraud rule-scoring, and
SoD matrix lookups are the same kind of check applied to three domains that
didn't have a standalone example yet. The only LLM call in this example is
the audit-trail narrative synthesis in agents.py -- everything that can be
computed should be computed, not asked of a model.
"""

from .schema import (
    BankTransaction,
    ControlException,
    FixedAsset,
    GLCashEntry,
    JournalEntry,
    PaymentTransaction,
    SoDRoleGrant,
)

_TOXIC_SOD_PAIRS = [("AP-create", "AP-approve"), ("vendor-master-edit", "payment-release")]


def _requires_approval(exposure: float, materiality_threshold: float) -> bool:
    return exposure >= materiality_threshold


def check_jv_postings(
    entries: list[JournalEntry], materiality_threshold: float
) -> list[ControlException]:
    exceptions = []
    for entry in entries:
        debits = sum(line.amount for line in entry.lines if line.side == "debit")
        credits = sum(line.amount for line in entry.lines if line.side == "credit")
        imbalance = round(abs(debits - credits), 2)
        if imbalance > 0.01:
            preparers = sorted({line.prepared_by for line in entry.lines})
            exceptions.append(
                ControlException(
                    domain="jv_posting",
                    severity="critical" if imbalance >= materiality_threshold else "medium",
                    description=(
                        f"Entry {entry.entry_id} ({entry.description!r}) is imbalanced by "
                        f"${imbalance:,.2f}: debits ${debits:,.2f} vs credits ${credits:,.2f}."
                    ),
                    financial_exposure=imbalance,
                    entities_involved=preparers + [entry.counterparty],
                    recommended_action=f"Reverse or correct entry {entry.entry_id} before close.",
                    requires_approval=_requires_approval(imbalance, materiality_threshold),
                )
            )
    return exceptions


def check_bank_reconciliation(
    bank_txns: list[BankTransaction], gl_entries: list[GLCashEntry], materiality_threshold: float
) -> list[ControlException]:
    matched_gl_ids = set()
    for txn in bank_txns:
        for gl in gl_entries:
            if gl.entry_id in matched_gl_ids:
                continue
            # A bank outflow (negative) books as a credit to cash (also negative
            # here); a bank inflow (positive) books as a debit (also positive).
            # Same sign, same magnitude is a match -- not opposite signs.
            if abs(txn.amount - gl.amount) < 0.01:
                matched_gl_ids.add(gl.entry_id)
                break

    exceptions = []
    for txn in bank_txns:
        matched = any(
            abs(txn.amount - gl.amount) < 0.01 and gl.entry_id in matched_gl_ids
            for gl in gl_entries
        )
        if matched:
            continue
        exposure = abs(txn.amount)
        exceptions.append(
            ControlException(
                domain="bank_reconciliation",
                severity="high" if exposure >= materiality_threshold else "low",
                description=(
                    f"Bank transaction {txn.txn_id} (${txn.amount:,.2f}, {txn.counterparty}) "
                    "has no matching GL entry."
                ),
                financial_exposure=exposure,
                entities_involved=[txn.counterparty],
                recommended_action=f"Investigate unmatched bank transaction {txn.txn_id}.",
                requires_approval=_requires_approval(exposure, materiality_threshold),
            )
        )
    return exceptions


def check_fixed_assets(assets: list[FixedAsset]) -> list[ControlException]:
    exceptions = []
    for asset in assets:
        if asset.accumulated_depreciation > asset.cost:
            over = round(asset.accumulated_depreciation - asset.cost, 2)
            exceptions.append(
                ControlException(
                    domain="fixed_asset",
                    severity="medium",
                    description=(
                        f"Asset {asset.asset_id} is over-depreciated by ${over:,.2f} "
                        "(accumulated depreciation exceeds cost)."
                    ),
                    financial_exposure=over,
                    entities_involved=[asset.asset_id],
                    recommended_action=f"Correct the depreciation schedule for {asset.asset_id}.",
                    requires_approval=False,
                )
            )
        if asset.disposed and asset.disposal_proceeds is None:
            nbv = round(asset.cost - asset.accumulated_depreciation, 2)
            exceptions.append(
                ControlException(
                    domain="fixed_asset",
                    severity="medium",
                    description=(
                        f"Asset {asset.asset_id} is marked disposed with no disposal proceeds "
                        f"booked; net book value ${nbv:,.2f} may be unaccounted for."
                    ),
                    financial_exposure=nbv,
                    entities_involved=[asset.asset_id],
                    recommended_action=f"Book disposal proceeds for {asset.asset_id} or reverse the disposal flag.",
                    requires_approval=False,
                )
            )
    return exceptions


def check_fraud_signals(
    transactions: list[PaymentTransaction], materiality_threshold: float
) -> list[ControlException]:
    exceptions = []
    payee_counts: dict[str, int] = {}
    for txn in transactions:
        payee_counts[txn.payee] = payee_counts.get(txn.payee, 0) + 1

    for txn in transactions:
        reasons = []
        if payee_counts[txn.payee] >= 3:
            reasons.append(f"{payee_counts[txn.payee]} payments to the same payee in one batch (velocity)")
        if txn.amount % 1000 == 0 and txn.amount > 5000:
            reasons.append("round-number amount over $5,000")
        if txn.is_new_payee and txn.amount > materiality_threshold:
            reasons.append("new payee with a large first payment")

        if reasons:
            exceptions.append(
                ControlException(
                    domain="fraud_screening",
                    severity="critical" if txn.amount >= materiality_threshold else "high",
                    description=(
                        f"Payment {txn.txn_id} to {txn.payee} (${txn.amount:,.2f}) flagged: "
                        + "; ".join(reasons)
                        + "."
                    ),
                    financial_exposure=txn.amount,
                    entities_involved=[txn.payee],
                    recommended_action=f"Hold payment {txn.txn_id} pending fraud review.",
                    requires_approval=_requires_approval(txn.amount, materiality_threshold),
                )
            )
    return exceptions


def check_segregation_of_duties(
    entries: list[JournalEntry], role_grants: list[SoDRoleGrant]
) -> list[ControlException]:
    roles_by_identity: dict[str, set[str]] = {}
    for grant in role_grants:
        roles_by_identity.setdefault(grant.identity, set()).add(grant.role)

    exposure_by_identity: dict[str, float] = {}
    for entry in entries:
        for line in entry.lines:
            exposure_by_identity[line.prepared_by] = (
                exposure_by_identity.get(line.prepared_by, 0.0) + line.amount
            )

    exceptions = []
    for identity, roles in roles_by_identity.items():
        for role_a, role_b in _TOXIC_SOD_PAIRS:
            if role_a in roles and role_b in roles:
                exposure = round(exposure_by_identity.get(identity, 0.0), 2)
                exceptions.append(
                    ControlException(
                        domain="segregation_of_duties",
                        severity="critical",
                        description=(
                            f"Identity {identity!r} holds both {role_a!r} and {role_b!r} "
                            "-- a toxic combination."
                        ),
                        financial_exposure=exposure,
                        entities_involved=[identity],
                        recommended_action=f"Revoke one of {identity}'s conflicting roles.",
                        requires_approval=True,
                    )
                )
    return exceptions
