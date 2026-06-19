from typing import Literal

from pydantic import BaseModel, Field


class DealInput(BaseModel):
    company_name: str = Field(description="Target company name")
    contract_text: str = Field(description="Full text of the commercial agreement or term sheet")
    diligence_documents: list[str] = Field(
        description="List of due diligence document excerpts (financials, management bio, etc.)"
    )
    financial_summary: str = Field(
        description="Plain-text summary of financials: revenue, EBITDA, debt, key assumptions"
    )


class RiskFinding(BaseModel):
    clause: str = Field(description="Clause or section the risk was found in")
    severity: Literal["low", "medium", "high", "critical"] = Field(description="Risk severity")
    description: str = Field(description="Plain-language description of the risk")
    mitigation: str = Field(description="Suggested mitigation or negotiation point")


class ContractReview(BaseModel):
    company_name: str = Field(description="Target company name")
    risk_findings: list[RiskFinding] = Field(description="Ranked list of risk findings")
    missing_protections: list[str] = Field(description="Standard protections absent from the contract")
    recommended_redlines: list[str] = Field(description="Top redline changes to negotiate")
    confidence: float = Field(description="Analyst confidence score 0.0–1.0 based on completeness of contract text")
    summary: str = Field(description="Two-sentence plain-language summary of overall contract risk")


class DiligenceRisk(BaseModel):
    area: str = Field(description="Risk area: financial, legal, operational, management, regulatory")
    severity: Literal["low", "medium", "high", "critical"] = Field(description="Risk severity")
    likelihood: Literal["low", "medium", "high"] = Field(description="Probability of materialising")
    description: str = Field(description="Plain-language description of the risk")
    mitigation: str = Field(description="Recommended mitigation action")


class DueDiligenceReport(BaseModel):
    company_name: str = Field(description="Target company name")
    risks: list[DiligenceRisk] = Field(description="Unified risk register ranked by severity")
    deal_breakers: list[str] = Field(description="Risks severe enough to halt the deal")
    confidence: float = Field(description="Analyst confidence score 0.0–1.0 based on document completeness")
    summary: str = Field(description="Two-sentence summary of overall due diligence findings")


class FinancialModel(BaseModel):
    company_name: str = Field(description="Target company name")
    revenue_year1: float = Field(description="Year 1 projected revenue in USD")
    revenue_year2: float = Field(description="Year 2 projected revenue in USD")
    revenue_year3: float = Field(description="Year 3 projected revenue in USD")
    ebitda_year3: float = Field(description="Year 3 projected EBITDA in USD")
    implied_valuation: float = Field(description="Implied enterprise value at entry multiple in USD")
    key_assumptions: list[str] = Field(description="Top 3-5 assumptions driving the model")
    confidence: float = Field(description="Model confidence score 0.0–1.0 based on data quality")
    commentary: str = Field(description="Two-sentence commentary on the financial outlook")


class BoardMemo(BaseModel):
    company_name: str = Field(description="Target company name")
    recommended_position: Literal["proceed", "pause", "reject"] = Field(
        description="Board recommendation based on all stage findings"
    )
    executive_summary: str = Field(description="2-3 paragraph summary for board directors")
    key_risks: list[str] = Field(description="Top 3-5 risks distilled from all stages")
    conditions_to_proceed: list[str] = Field(
        description="Conditions that must be met before proceeding; empty if rejecting"
    )
    one_sentence_verdict: str = Field(description="Single sentence board-ready verdict")
    confidence: float = Field(description="Overall pipeline confidence score 0.0–1.0")


class EscalationFlag(BaseModel):
    stage: str = Field(description="Stage that triggered the halt: contract_review, due_diligence, financial_model")
    confidence: float = Field(description="Confidence score that fell below threshold")
    threshold: float = Field(description="Threshold that was not met")
    reason: str = Field(description="Plain-language reason the stage was flagged for escalation")


class DealRoomResult(BaseModel):
    company_name: str = Field(description="Target company name")
    completed: bool = Field(description="True if all stages passed confidence gates; False if halted")
    escalation: EscalationFlag | None = Field(
        default=None, description="Set when the pipeline halted before reaching the board memo"
    )
    contract_review: ContractReview | None = Field(default=None)
    due_diligence: DueDiligenceReport | None = Field(default=None)
    financial_model: FinancialModel | None = Field(default=None)
    board_memo: BoardMemo | None = Field(default=None)
