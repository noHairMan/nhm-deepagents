"""Models used by Fragile sessions."""

from uuid import UUID

from pydantic import BaseModel

from fragile.models.plan import PlanOutput


class ApprovedPlan(BaseModel):
    """A task and its explicitly approved structured plan."""

    task: str
    plan: PlanOutput


class SessionState(BaseModel):
    """Mutable state shared by interactive command handlers."""

    thread_id: UUID
    approved_plan: ApprovedPlan | None = None
