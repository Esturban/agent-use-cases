"""
AI PMO -- stateful project tracking.

Two structured LLM calls per update:
1. extract_update: parse the raw input into a ProjectState delta.
2. merge_state: merge the delta onto the current state and re-derive
   the RAG status and executive summary.

No LangGraph. No tool loop. Pure schema-in, schema-out.
"""
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from .schema import ProjectState, UpdateInput

_EXTRACT_SYSTEM = SystemMessage(
    """You are a project management analyst. Read the update text and extract
any changes to milestones, risks, blockers, or deliverable ownership.

Return a ProjectState reflecting ONLY what was mentioned in this update.
Leave all other fields as empty lists. Set overall_status to the status
implied by the update, or 'green' if not mentioned."""
)

_MERGE_SYSTEM = SystemMessage(
    """You are a senior PMO director. You have the current project state and a
delta extracted from the latest update.

Merge the delta into the current state:
- Add new milestones, risks, blockers, and deliverable owners.
- Update existing items if the new information supersedes the old (match by name/description).
- Remove blockers marked as resolved.
- Re-derive the overall RAG status based on the merged picture.
- Write a fresh two-to-three sentence executive summary.

Return the complete merged ProjectState."""
)


def init_state(project_name: str) -> ProjectState:
    """Return a blank project state for a new engagement."""
    return ProjectState(
        project_name=project_name,
        overall_status="green",
        milestones=[],
        risks=[],
        blockers=[],
        deliverable_owners=[],
        summary="Project initialised. No updates received yet.",
    )


def apply_update(current: ProjectState, update: UpdateInput) -> ProjectState:
    """Apply one unstructured update to the current project state."""
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    structured_llm = llm.with_structured_output(ProjectState)

    delta: ProjectState = structured_llm.invoke(
        [
            _EXTRACT_SYSTEM,
            {
                "role": "user",
                "content": (
                    f"Project: {current.project_name}\n"
                    f"Source: {update.source}\n"
                    f"Update:\n{update.content}"
                ),
            },
        ]
    )

    merged: ProjectState = structured_llm.invoke(
        [
            _MERGE_SYSTEM,
            {
                "role": "user",
                "content": (
                    f"Current state:\n{current.model_dump_json(indent=2)}\n\n"
                    f"Delta from update ({update.source}):\n{delta.model_dump_json(indent=2)}"
                ),
            },
        ]
    )
    return merged


def run(project_name: str, updates: list[UpdateInput]) -> list[ProjectState]:
    """Apply a sequence of updates and return the state after each one."""
    state = init_state(project_name)
    history = [state]
    for update in updates:
        state = apply_update(state, update)
        history.append(state)
    return history
