"""Plan review command for interactive sessions."""

from fragile.commands.interactive.commands.base import Command
from fragile.commands.plan import review_plan
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class PlanCommand(Command):
    """Review a task plan and request explicit approval before execution."""

    name = "plan"
    clears_output_after_handling = True

    async def handle(self, prompt: str | None, state: SessionState) -> CommandResult:
        state.approved_task = None
        state.approved_plan = None
        if not prompt or not prompt.strip():
            return CommandResult.CONTINUE
        task = prompt.strip()
        plan = await review_plan(task)
        if plan is None:
            return CommandResult.CONTINUE
        state.approved_task = task
        state.approved_plan = plan
        return CommandResult.PLAN_APPROVED
