from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest

from fragile.commands.interactive.commands.plan import PlanCommand
from fragile.commands.plan import PlanGenerationError, PlanOutput
from fragile.models import ApprovedPlan, SessionState
from fragile.models.constants import CommandResult


class TestPlanCommand:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("prompt", [None, "", "   "])
    async def test_empty_prompt_clears_approval_without_review(self, prompt: str | None) -> None:
        state = SessionState(
            thread_id=UUID(int=1),
            approved_plan=ApprovedPlan(task="old task", plan=PlanOutput(steps=["old plan"])),
        )

        command = PlanCommand()
        command.prompt_session = object()
        with patch("fragile.commands.interactive.commands.plan.review_plan", new_callable=AsyncMock) as review:
            result = await command.handle(prompt, state)

        assert result is CommandResult.CONTINUE
        assert state.approved_plan is None
        review.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_cancel_clears_old_approval(self) -> None:
        state = SessionState(
            thread_id=UUID(int=1),
            approved_plan=ApprovedPlan(task="old task", plan=PlanOutput(steps=["old plan"])),
        )
        review = AsyncMock(return_value=None)
        command = PlanCommand()
        command.prompt_session = object()

        with patch("fragile.commands.interactive.commands.plan.review_plan", new=review):
            result = await command.handle("  new task  ", state)

        assert result is CommandResult.CONTINUE
        assert state.approved_plan is None
        review.assert_awaited_once_with("new task", command.prompt_session)

    @pytest.mark.asyncio
    async def test_generation_failure_leaves_no_approval(self) -> None:
        state = SessionState(
            thread_id=UUID(int=1),
            approved_plan=ApprovedPlan(task="old task", plan=PlanOutput(steps=["old plan"])),
        )
        review = AsyncMock(side_effect=PlanGenerationError("generation failed"))
        command = PlanCommand()
        command.prompt_session = object()

        with (
            patch("fragile.commands.interactive.commands.plan.review_plan", new=review),
            pytest.raises(PlanGenerationError, match="generation failed"),
        ):
            await command.handle("new task", state)

        assert state.approved_plan is None
        review.assert_awaited_once_with("new task", command.prompt_session)

    @pytest.mark.asyncio
    async def test_missing_prompt_session_does_not_start_review(self) -> None:
        state = SessionState(thread_id=UUID(int=1))
        command = PlanCommand()

        with patch("fragile.commands.interactive.commands.plan.review_plan", new_callable=AsyncMock) as review:
            result = await command.handle("task", state)

        assert result is CommandResult.CONTINUE
        review.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_approved_plan_saves_task_and_plan(self) -> None:
        state = SessionState(
            thread_id=UUID(int=1),
            approved_plan=ApprovedPlan(task="old task", plan=PlanOutput(steps=["old plan"])),
        )

        async def approve(task: str, prompt_session: object) -> PlanOutput:
            assert task == "new task"
            assert prompt_session is command.prompt_session
            assert state.approved_plan is None
            return PlanOutput(steps=["confirmed plan"])

        command = PlanCommand()
        command.prompt_session = object()
        with patch("fragile.commands.interactive.commands.plan.review_plan", new=AsyncMock(side_effect=approve)):
            result = await command.handle("  new task  ", state)

        assert result is CommandResult.PLAN_APPROVED
        assert state.approved_plan == ApprovedPlan(task="new task", plan=PlanOutput(steps=["confirmed plan"]))
