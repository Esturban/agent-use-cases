from typing import Literal

from pydantic import BaseModel, Field


class Milestone(BaseModel):
    name: str = Field(description="Milestone name.")
    due_date: str = Field(description="Target completion date, e.g. 2024-Q3.")
    status: Literal["on_track", "at_risk", "delayed", "complete"] = Field(
        description="Current milestone status."
    )


class Risk(BaseModel):
    description: str = Field(description="Plain-English risk description.")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="Estimated business impact if the risk materialises."
    )
    owner: str = Field(description="Person or team responsible for mitigation.")


class Blocker(BaseModel):
    description: str = Field(description="What is blocking progress.")
    raised_by: str = Field(description="Person or team who raised the blocker.")
    resolution_needed_from: str = Field(
        description="Who needs to act to resolve this blocker."
    )


class DeliverableOwner(BaseModel):
    deliverable: str = Field(description="Name of the deliverable.")
    owner: str = Field(description="Responsible person or team.")
    due_date: str = Field(description="Target date.")


class ProjectState(BaseModel):
    project_name: str = Field(description="Project or engagement name.")
    overall_status: Literal["green", "amber", "red"] = Field(
        description="RAG status: green = on track, amber = at risk, red = in trouble."
    )
    milestones: list[Milestone] = Field(description="Key milestones and their statuses.")
    risks: list[Risk] = Field(description="Active risks ranked by severity.")
    blockers: list[Blocker] = Field(description="Current blockers requiring resolution.")
    deliverable_owners: list[DeliverableOwner] = Field(
        description="RACI-style deliverable ownership list."
    )
    summary: str = Field(
        description="Two-to-three sentence plain-English summary of project health for an executive audience."
    )


class UpdateInput(BaseModel):
    source: str = Field(description="Who or what this update came from, e.g. 'weekly status call'.")
    content: str = Field(description="Raw unstructured update text.")
