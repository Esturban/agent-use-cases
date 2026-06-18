from pydantic import BaseModel, Field


class AddArgs(BaseModel):
    a: float = Field(description="First number to add.")
    b: float = Field(description="Second number to add.")


class MultiplyArgs(BaseModel):
    a: float = Field(description="First number to multiply.")
    b: float = Field(description="Second number to multiply.")


class AgentStep(BaseModel):
    step: int = Field(description="Step index in the ReAct loop (1-based).")
    action: str = Field(description="Tool name called, or 'final' for the last answer.")
    input: str = Field(description="Arguments passed to the tool (JSON string) or the final answer text.")
    observation: str = Field(description="Tool result, or empty string for final answer step.")
