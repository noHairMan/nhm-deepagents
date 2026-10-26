from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest

from fragile.commands.interactive.commands.plan import PlanCommand
from fragile.commands.plan import PlanGenerationError
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class TestPlanCommand:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("prompt", [None, "", "   "])
    async def test_empty_prompt_clears_approval_without_review(self, prompt: str | None) -> None:
        state = SessionState(thread_id=UUID(int=1), approved_task="old task", approved_plan="old plan")

        with patch("fragile.commands.interactive.commands.plan.review_plan", new_callable=AsyncMock) as review:
            result = await PlanCommand().handle(prompt, state)

        assert result is CommandResult.CONTINUE
        assert state.approved_task is None
        assert state.approved_plan is None
        review.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_cancel_clears_old_approval(self) -> None:
        state = SessionState(thread_id=UUID(int=1), approved_task="old task", approved_plan="old plan")
        review = AsyncMock(return_value=None)

        with patch("fragile.commands.interactive.commands.plan.review_plan", new=review):
            result = await PlanCommand().handle("  new task  ", state)

        assert result is CommandResult.CONTINUE
        assert state.approved_task is None
        assert state.approved_plan is None
        review.assert_awaited_once_with("new task")

    @pytest.mark.asyncio
    async def test_generation_failure_leaves_no_approval(self) -> None:
        state = SessionState(thread_id=UUID(int=1), approved_task="old task", approved_plan="old plan")
        review = AsyncMock(side_effect=PlanGenerationError("generation failed"))

        with (
            patch("fragile.commands.interactive.commands.plan.review_plan", new=review),
            pytest.raises(PlanGenerationError, match="generation failed"),
        ):
            await PlanCommand().handle("new task", state)

        assert state.approved_task is None
        assert state.approved_plan is None
        review.assert_awaited_once_with("new task")

    @pytest.mark.asyncio
    async def test_approved_plan_saves_task_and_plan(self) -> None:
        state = SessionState(thread_id=UUID(int=1), approved_task="old task", approved_plan="old plan")

        async def approve(task: str) -> str:
            assert task == "new task"
            assert state.approved_task is None
            assert state.approved_plan is None
            return "confirmed plan"

        with patch("fragile.commands.interactive.commands.plan.review_plan", new=AsyncMock(side_effect=approve)):
            result = await PlanCommand().handle("  new task  ", state)

        assert result is CommandResult.PLAN_APPROVED
        assert state.approved_task == "new task"
        assert state.approved_plan == "confirmed plan"
