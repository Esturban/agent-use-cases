from pydantic import BaseModel, Field


class StrategicOpinion(BaseModel):
    model: str = Field(description="The model that produced this opinion (e.g. openai/gpt-4.1-nano).")
    recommendation: str = Field(
        description="The model's top strategic recommendation in one to two sentences."
    )
    key_risks: list[str] = Field(
        description="Up to three key risks the model identifies."
    )
    key_opportunities: list[str] = Field(
        description="Up to three key opportunities the model identifies."
    )
    confidence: str = Field(
        description="Model's self-assessed confidence: high, medium, or low."
    )


class ModelConsensus(BaseModel):
    topic: str = Field(description="The strategic topic or question posed.")
    opinions: list[StrategicOpinion] = Field(
        description="One opinion per model, in the order they were queried."
    )
    points_of_agreement: list[str] = Field(
        description="Themes where all or most models agree."
    )
    points_of_disagreement: list[str] = Field(
        description="Areas where models diverge significantly."
    )
    synthesised_recommendation: str = Field(
        description="A single consolidated recommendation that draws on the majority view across models."
    )
