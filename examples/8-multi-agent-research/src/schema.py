from typing import List

from pydantic import BaseModel, Field


class ResearchFindings(BaseModel):
    topic: str
    key_facts: List[str] = Field(description="3-5 concrete facts with data or citations where possible")
    trends: List[str] = Field(description="2-3 observed trends or emerging developments")
    gaps: List[str] = Field(description="Questions this research could not answer — limits and unknowns")


class WrittenBrief(BaseModel):
    title: str
    executive_summary: str = Field(description="2-3 sentence summary for a busy executive")
    body: str = Field(description="400-600 word brief in markdown format")
    key_takeaways: List[str] = Field(description="3 bullet points the reader should remember")
    further_reading: List[str] = Field(description="2-3 topic areas worth exploring next")
