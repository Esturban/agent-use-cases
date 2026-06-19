from pydantic import BaseModel, Field


class ESGDisclosure(BaseModel):
    category: str = Field(
        description=(
            "CSRD reporting category this disclosure maps to. One of: "
            "Climate Change, Pollution, Water & Marine Resources, Biodiversity & Ecosystems, "
            "Resource Use & Circular Economy, Own Workforce, Workers in Value Chain, "
            "Affected Communities, Consumers & End-users, Business Conduct, or Governance."
        )
    )
    topic: str = Field(description="Specific topic within the category, e.g. 'GHG Emissions' or 'Board Diversity'.")
    disclosure_text: str = Field(description="Verbatim or close-paraphrase of the relevant text from the filing.")
    source_section: str = Field(
        description="Section of the 10-K where this disclosure appears, e.g. 'Item 1A. Risk Factors' or 'Item 7. MD&A'."
    )
    completeness: str = Field(
        description=(
            "Assessment of how complete this disclosure is relative to CSRD expectations: "
            "FULL, PARTIAL, or MINIMAL."
        )
    )
    gaps: list[str] = Field(
        description="Specific information missing that CSRD would require for this topic. Empty list if completeness is FULL."
    )


class ESGReport(BaseModel):
    company: str = Field(description="Company name.")
    ticker: str = Field(description="Stock ticker symbol.")
    filing_year: int = Field(description="Fiscal year of the 10-K filing.")
    disclosures: list[ESGDisclosure] = Field(
        description="All ESG disclosures found, one entry per distinct topic identified."
    )
    csrd_coverage_score: int = Field(
        description=(
            "Estimated percentage (0-100) of CSRD reporting requirements addressed by this filing, "
            "based on breadth and completeness of disclosures found."
        )
    )
    strongest_areas: list[str] = Field(
        description="Up to 3 ESG categories where the filing provides the most complete disclosure."
    )
    critical_gaps: list[str] = Field(
        description="Up to 3 CSRD categories with no or minimal disclosure — highest priority for improvement."
    )
    analyst_note: str = Field(
        description=(
            "2-3 sentence plain-English assessment: overall ESG disclosure maturity, "
            "what the company does well, and the single most important gap to address."
        )
    )
