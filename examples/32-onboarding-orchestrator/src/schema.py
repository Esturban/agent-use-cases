from pydantic import BaseModel, Field


class NewHire(BaseModel):
    name: str = Field(description="Full name of the new employee.")
    role: str = Field(description="Job title or role.")
    department: str = Field(description="Department the employee is joining.")
    start_date: str = Field(description="Start date in YYYY-MM-DD format.")
    location: str = Field(description="Office location or 'remote'.")


class SubAgentStatus(BaseModel):
    domain: str = Field(description="Domain handled by this sub-agent (IT, HR, or Facilities).")
    tasks: list[str] = Field(description="Full list of tasks for this domain.")
    completed: list[str] = Field(description="Tasks that can be completed before Day 1.")
    pending: list[str] = Field(description="Tasks that require Day 1 or later to complete.")
    notes: str = Field(description="Key notes or blockers specific to this domain.")


class OnboardingPlan(BaseModel):
    new_hire: NewHire = Field(description="New hire details.")
    it_status: SubAgentStatus = Field(description="IT provisioning status and task list.")
    hr_status: SubAgentStatus = Field(description="HR documentation status and task list.")
    facilities_status: SubAgentStatus = Field(description="Facilities setup status and task list.")
    day1_ready: bool = Field(description="True if all critical Day 1 tasks are completable before start.")
    blockers: list[str] = Field(description="Any blockers that prevent Day 1 readiness.")
    summary: str = Field(description="2-3 sentence narrative summary of the onboarding plan status.")
