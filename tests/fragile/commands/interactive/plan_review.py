from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from fragile.commands.interactive.plan_review import review_plan
from fragile.commands.plan import PlanOutput


class TestPlanReview:
    @pytest.mark.asyncio
    async def test_navigation_full_view_and_confirmation(self, capsys) -> None:
        plan = PlanOutput(requirements=["goal"], steps=["deliver"])
        prompt_session = SimpleNamespace(prompt_async=AsyncMock(side_effect=["n", "p", "v", "c"]))

        with patch("fragile.commands.interactive.plan_review._generate_plan", new=AsyncMock(return_value=plan)):
            result = await review_plan("task", prompt_session)

        assert result == plan
        assert prompt_session.prompt_async.await_count == 4
        output = capsys.readouterr().out
        assert "## 需求" in output
        assert "## 交付步骤" in output
        assert "## 需求\n- goal\n## 交付步骤\n1. deliver" in output

    @pytest.mark.asyncio
    async def test_revision_regenerates_and_returns_updated_structure(self) -> None:
        first = PlanOutput(steps=["initial"])
        revised = PlanOutput(testing=["verify"])
        prompt_session = SimpleNamespace(prompt_async=AsyncMock(side_effect=["m", "add tests", "c"]))
        generate = AsyncMock(side_effect=[first, revised])

        with patch("fragile.commands.interactive.plan_review._generate_plan", new=generate):
            result = await review_plan("task", prompt_session)

        assert result == revised
        generate.assert_awaited_with("task", "add tests", "## 交付步骤\n1. initial")

    @pytest.mark.asyncio
    async def test_save_uses_user_path_and_writes_markdown(self, tmp_path: Path) -> None:
        output = tmp_path / "plan.md"
        prompt_session = SimpleNamespace(prompt_async=AsyncMock(side_effect=["s", str(output), "c"]))
        plan = PlanOutput(steps=["deliver"])

        with patch("fragile.commands.interactive.plan_review._generate_plan", new=AsyncMock(return_value=plan)):
            assert await review_plan("task", prompt_session) == plan

        assert output.read_text(encoding="utf-8") == "## 交付步骤\n1. deliver\n"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("action", ["x", "cancel"])
    async def test_cancel_does_not_approve(self, action: str) -> None:
        prompt_session = SimpleNamespace(prompt_async=AsyncMock(return_value=action))
        with patch(
            "fragile.commands.interactive.plan_review._generate_plan",
            new=AsyncMock(return_value=PlanOutput(steps=["deliver"])),
        ):
            assert await review_plan("task", prompt_session) is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("error", [EOFError, KeyboardInterrupt])
    async def test_interrupt_does_not_approve(self, error: type[BaseException]) -> None:
        prompt_session = SimpleNamespace(prompt_async=AsyncMock(side_effect=error))
        with patch(
            "fragile.commands.interactive.plan_review._generate_plan",
            new=AsyncMock(return_value=PlanOutput(steps=["deliver"])),
        ):
            assert await review_plan("task", prompt_session) is None

    @pytest.mark.asyncio
    async def test_empty_feedback_path_and_unknown_action_reprompt(self) -> None:
        prompt_session = SimpleNamespace(prompt_async=AsyncMock(side_effect=["other", "m", " ", "s", " ", "c"]))
        plan = PlanOutput(steps=["deliver"])
        with patch("fragile.commands.interactive.plan_review._generate_plan", new=AsyncMock(return_value=plan)):
            assert await review_plan("task", prompt_session) == plan

    @pytest.mark.asyncio
    @pytest.mark.parametrize("first_action", ["m", "s"])
    async def test_interrupt_during_revision_or_save_prompt_cancels(self, first_action: str) -> None:
        prompt_session = SimpleNamespace(prompt_async=AsyncMock(side_effect=[first_action, EOFError]))
        with patch(
            "fragile.commands.interactive.plan_review._generate_plan",
            new=AsyncMock(return_value=PlanOutput(steps=["deliver"])),
        ):
            assert await review_plan("task", prompt_session) is None

    @pytest.mark.asyncio
    async def test_unwritable_save_reports_error_and_review_continues(self, monkeypatch, capsys) -> None:
        prompt_session = SimpleNamespace(prompt_async=AsyncMock(side_effect=["s", "plan.md", "c"]))
        plan = PlanOutput(steps=["deliver"])
        monkeypatch.setattr(Path, "write_text", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("denied")))
        with patch("fragile.commands.interactive.plan_review._generate_plan", new=AsyncMock(return_value=plan)):
            assert await review_plan("task", prompt_session) == plan
        assert "无法保存计划：denied" in capsys.readouterr().out
