from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import asyncclick as click
import pytest

from fragile.commands.plan import (
    PLAN_SYSTEM_PROMPT,
    PlanGenerationError,
    PlanOutput,
    _format_todos,
    _generate_plan,
    review_plan,
)


class TestPlanReview:
    @pytest.mark.parametrize(
        ("state", "expected"),
        [
            (
                {"structured_response": PlanOutput(steps=[" first ", "second"])},
                "1. first\n2. second",
            ),
            ({"structured_response": PlanOutput(steps=[" ", "valid"])}, "1. valid"),
            ({}, ""),
            ({"structured_response": None}, ""),
            ({"structured_response": PlanOutput(steps=[])}, ""),
            ({"structured_response": {"steps": ["not validated"]}}, ""),
            (None, ""),
        ],
    )
    def test_format_todos_extracts_only_valid_tasks(self, state: object, expected: str) -> None:
        assert _format_todos(state) == expected

    @pytest.mark.asyncio
    async def test_generate_plan_uses_structured_output_agent(self) -> None:
        state = {"structured_response": PlanOutput(steps=["first", "second"])}
        planner = SimpleNamespace(ainvoke=AsyncMock(return_value=state))
        model = object()
        with (
            patch("fragile.commands.plan.get_model", return_value=model),
            patch("fragile.commands.plan.create_deep_agent", return_value=planner) as create_agent,
        ):
            assert await _generate_plan("original task") == "1. first\n2. second"

        create_agent.assert_called_once()
        assert create_agent.call_args.kwargs["model"] is model
        assert create_agent.call_args.kwargs["tools"] == []
        assert create_agent.call_args.kwargs["system_prompt"] == PLAN_SYSTEM_PROMPT
        assert create_agent.call_args.kwargs["response_format"] is PlanOutput
        assert "middleware" not in create_agent.call_args.kwargs
        planner.ainvoke.assert_awaited_once_with(
            {"messages": [{"role": "user", "content": "用户任务：\noriginal task"}]}
        )

    @pytest.mark.asyncio
    async def test_feedback_regenerates_plan_and_confirmation_returns_final_plan(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        planner = SimpleNamespace(
            ainvoke=AsyncMock(
                side_effect=[
                    {"structured_response": PlanOutput(steps=["first plan"])},
                    {"structured_response": PlanOutput(steps=["revised plan"])},
                ]
            )
        )

        with (
            patch("fragile.commands.plan.get_model"),
            patch("fragile.commands.plan.create_deep_agent", return_value=planner),
            patch(
                "fragile.commands.plan.click.prompt", new_callable=AsyncMock, side_effect=["m", "include tests", "c"]
            ),
        ):
            assert await review_plan("original task") == "1. revised plan"

        assert planner.ainvoke.await_count == 2
        revised_request = planner.ainvoke.await_args_list[1].args[0]["messages"][0]["content"]
        assert "original task" in revised_request
        assert "first plan" in revised_request
        assert "include tests" in revised_request
        assert "original task" in planner.ainvoke.await_args_list[0].args[0]["messages"][0]["content"]
        output = capsys.readouterr().out
        assert "first plan" in output
        assert "revised plan" in output

    @pytest.mark.asyncio
    async def test_cancel_returns_none_and_does_not_regenerate(self) -> None:
        planner = SimpleNamespace(ainvoke=AsyncMock(return_value={"structured_response": PlanOutput(steps=["plan"])}))

        with (
            patch("fragile.commands.plan.get_model"),
            patch("fragile.commands.plan.create_deep_agent", return_value=planner),
            patch("fragile.commands.plan.click.prompt", new_callable=AsyncMock, return_value="x"),
        ):
            assert await review_plan("task") is None
        planner.ainvoke.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_empty_feedback_and_unknown_action_reprompt(self) -> None:
        planner = SimpleNamespace(ainvoke=AsyncMock(return_value={"structured_response": PlanOutput(steps=["plan"])}))

        prompt_mock = AsyncMock(side_effect=["m", " ", "other", "x"])
        with (
            patch("fragile.commands.plan.get_model"),
            patch("fragile.commands.plan.create_deep_agent", return_value=planner),
            patch("fragile.commands.plan.click.prompt", new=prompt_mock),
        ):
            assert await review_plan("task") is None
        assert prompt_mock.await_count == 4
        planner.ainvoke.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exit_error", [EOFError, KeyboardInterrupt, click.Abort()])
    async def test_exit_during_review_returns_none(self, exit_error: BaseException) -> None:
        planner = SimpleNamespace(ainvoke=AsyncMock(return_value={"structured_response": PlanOutput(steps=["plan"])}))

        with (
            patch("fragile.commands.plan.get_model"),
            patch("fragile.commands.plan.create_deep_agent", return_value=planner),
            patch("fragile.commands.plan.click.prompt", new_callable=AsyncMock, side_effect=exit_error),
        ):
            assert await review_plan("task") is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "state",
        [
            {},
            {"structured_response": PlanOutput(steps=[])},
            {"structured_response": PlanOutput(steps=[" "])},
            {"structured_response": None},
        ],
    )
    async def test_empty_plan_is_rejected_before_prompt(self, state: object) -> None:
        planner = SimpleNamespace(ainvoke=AsyncMock(return_value=state))

        with (
            patch("fragile.commands.plan.get_model"),
            patch("fragile.commands.plan.create_deep_agent", return_value=planner),
            patch("fragile.commands.plan.click.prompt", new_callable=AsyncMock) as prompt,
            pytest.raises(PlanGenerationError),
        ):
            await review_plan("task")
        prompt.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_agent_error_propagates_without_prompting(self) -> None:
        planner = SimpleNamespace(ainvoke=AsyncMock(side_effect=RuntimeError("agent failed")))

        with (
            patch("fragile.commands.plan.get_model"),
            patch("fragile.commands.plan.create_deep_agent", return_value=planner),
            patch("fragile.commands.plan.click.prompt", new_callable=AsyncMock) as prompt,
            pytest.raises(RuntimeError, match="agent failed"),
        ):
            await review_plan("task")
        prompt.assert_not_awaited()
