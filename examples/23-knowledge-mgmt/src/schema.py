from pydantic import BaseModel, Field


class Precedent(BaseModel):
    title: str = Field(description="Document title or engagement name.")
    excerpt: str = Field(description="Relevant extract or summary from the document.")
    relevance_reason: str = Field(
        description="Why this precedent is relevant to the current query."
    )
    source_id: str = Field(description="Identifier linking back to the source document.")


class KnowledgeBrief(BaseModel):
    query: str = Field(description="The original user query or drafting task.")
    precedents: list[Precedent] = Field(
        description="Retrieved precedents most relevant to the query, ranked by relevance."
    )
    synthesis: str = Field(
        description=(
            "A structured synthesis that draws on the precedents to address the query. "
            "Must explicitly cite precedents by title when drawing on them."
        )
    )
    gaps: list[str] = Field(
        description="Any gaps where no precedent covers the query and original work is needed."
    )
