from typing import Literal

from pydantic import BaseModel, Field


class CompetitorProfile(BaseModel):
    name: str = Field(description="Competitor company name.")
    estimated_market_share_pct: float = Field(
        description="Estimated market share as a percentage (0-100)."
    )
    strengths: list[str] = Field(description="Key competitive advantages.")
    weaknesses: list[str] = Field(description="Notable gaps or vulnerabilities.")


class OpportunityRisk(BaseModel):
    description: str = Field(description="Plain-English description of the opportunity or risk.")
    score: int = Field(description="Severity or attractiveness on a 1-10 scale.", ge=1, le=10)
    category: Literal["opportunity", "risk"] = Field(
        description="Whether this is an opportunity or a risk."
    )


class MarketAnalysis(BaseModel):
    market: str = Field(description="The market or geography being analysed.")
    market_size_usd_bn: float = Field(description="Estimated total addressable market in USD billions.")
    growth_rate_pct: float = Field(description="Annual market growth rate as a percentage.")
    competitors: list[CompetitorProfile] = Field(
        description="Top 3-5 competitors with profile summaries."
    )
    opportunities_and_risks: list[OpportunityRisk] = Field(
        description="Ranked opportunities and risks, highest score first."
    )
    entry_recommendation: Literal["enter", "monitor", "avoid"] = Field(
        description="High-level market entry verdict."
    )
    rationale: str = Field(
        description="Two-to-three sentence plain-English rationale for the entry recommendation."
    )
