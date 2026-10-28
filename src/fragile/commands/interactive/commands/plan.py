"""Plan review command for interactive sessions."""

from fragile.commands.interactive.commands.base import Command
from fragile.commands.interactive.plan_review import PlanInput, review_plan
from fragile.models import ApprovedPlan, SessionState
from fragile.models.constants import CommandResult


class PlanCommand(Command):
    """Review a task plan and request explicit approval before execution."""

    name = "plan"
    clears_output_after_handling = True

    def __init__(self) -> None:
        self.prompt_session: PlanInput | None = None

    async def handle(self, prompt: str | None, state: SessionState) -> CommandResult:
        state.approved_plan = None
        if not prompt or not prompt.strip():
            return CommandResult.CONTINUE
        if self.prompt_session is None:
            return CommandResult.CONTINUE
        task = prompt.strip()
        plan = await review_plan(task, self.prompt_session)
        if plan is None:
            return CommandResult.CONTINUE
        state.approved_plan = ApprovedPlan(task=task, plan=plan)
        return CommandResult.PLAN_APPROVED
