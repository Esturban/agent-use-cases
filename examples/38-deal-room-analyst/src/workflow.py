import json
import os

from openai import OpenAI

from .prompts import BOARD_SYSTEM, CONTRACT_SYSTEM, DILIGENCE_SYSTEM, FINANCIAL_SYSTEM
from .schema import (
    BoardMemo,
    ContractReview,
    DealInput,
    DealRoomResult,
    DueDiligenceReport,
    EscalationFlag,
    FinancialModel,
)

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
_MODEL = "gpt-4o-mini"
_CONFIDENCE_THRESHOLD = 0.6


def _call(system: str, user: str, schema_name: str, schema: dict) -> str:
    resp = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        },
    )
    return resp.choices[0].message.content


def _review_contract(deal: DealInput) -> ContractReview:
    raw = _call(
        CONTRACT_SYSTEM,
        deal.contract_text,
        "ContractReview",
        ContractReview.model_json_schema(),
    )
    return ContractReview.model_validate_json(raw)


def _run_due_diligence(deal: DealInput) -> DueDiligenceReport:
    raw = _call(
        DILIGENCE_SYSTEM,
        json.dumps({"company": deal.company_name, "documents": deal.diligence_documents}),
        "DueDiligenceReport",
        DueDiligenceReport.model_json_schema(),
    )
    return DueDiligenceReport.model_validate_json(raw)


def _build_financial_model(deal: DealInput) -> FinancialModel:
    raw = _call(
        FINANCIAL_SYSTEM,
        json.dumps({"company": deal.company_name, "financial_summary": deal.financial_summary}),
        "FinancialModel",
        FinancialModel.model_json_schema(),
    )
    return FinancialModel.model_validate_json(raw)


def _write_board_memo(
    deal: DealInput,
    contract: ContractReview,
    diligence: DueDiligenceReport,
    financials: FinancialModel,
) -> BoardMemo:
    payload = {
        "company": deal.company_name,
        "contract_review": contract.model_dump(),
        "due_diligence": diligence.model_dump(),
        "financial_model": financials.model_dump(),
    }
    raw = _call(BOARD_SYSTEM, json.dumps(payload), "BoardMemo", BoardMemo.model_json_schema())
    return BoardMemo.model_validate_json(raw)


def run(deal: DealInput, threshold: float = _CONFIDENCE_THRESHOLD) -> DealRoomResult:
    contract = _review_contract(deal)
    if contract.confidence < threshold:
        return DealRoomResult(
            company_name=deal.company_name,
            completed=False,
            escalation=EscalationFlag(
                stage="contract_review",
                confidence=contract.confidence,
                threshold=threshold,
                reason=f"Contract confidence {contract.confidence:.2f} below threshold {threshold}. "
                "Insufficient contract text to proceed.",
            ),
            contract_review=contract,
        )

    diligence = _run_due_diligence(deal)
    if diligence.confidence < threshold:
        return DealRoomResult(
            company_name=deal.company_name,
            completed=False,
            escalation=EscalationFlag(
                stage="due_diligence",
                confidence=diligence.confidence,
                threshold=threshold,
                reason=f"Due diligence confidence {diligence.confidence:.2f} below threshold {threshold}. "
                "Document coverage insufficient.",
            ),
            contract_review=contract,
            due_diligence=diligence,
        )

    financials = _build_financial_model(deal)
    if financials.confidence < threshold:
        return DealRoomResult(
            company_name=deal.company_name,
            completed=False,
            escalation=EscalationFlag(
                stage="financial_model",
                confidence=financials.confidence,
                threshold=threshold,
                reason=f"Financial model confidence {financials.confidence:.2f} below threshold {threshold}. "
                "Insufficient financial data.",
            ),
            contract_review=contract,
            due_diligence=diligence,
            financial_model=financials,
        )

    memo = _write_board_memo(deal, contract, diligence, financials)
    return DealRoomResult(
        company_name=deal.company_name,
        completed=True,
        contract_review=contract,
        due_diligence=diligence,
        financial_model=financials,
        board_memo=memo,
    )
