from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from langchain.agents.structured_output import ProviderStrategy

from fragile.commands.plan import (
    PLAN_SYSTEM_PROMPT,
    PlanGenerationError,
    PlanOutput,
    _format_todos,
    _generate_plan,
    format_plan,
)


class TestPlanReview:
    def test_format_plan_includes_nonempty_sections_in_stable_order(self) -> None:
        plan = PlanOutput(
            requirements=[" requirement "],
            technical_design=["design"],
            testing=["tests"],
            steps=["first", " second "],
        )

        assert format_plan(plan) == (
            "## 需求\n- requirement\n## 技术设计\n- design\n## 测试\n- tests\n## 交付步骤\n1. first\n2. second"
        )

    def test_format_plan_omits_empty_or_whitespace_sections(self) -> None:
        assert format_plan(PlanOutput(requirements=[" ", ""], steps=[" task "])) == "## 交付步骤\n1. task"

    @pytest.mark.parametrize(
        ("state", "expected"),
        [
            (
                {"structured_response": PlanOutput(steps=[" first ", "second"])},
                "## 交付步骤\n1. first\n2. second",
            ),
            ({"structured_response": PlanOutput(steps=[" ", "valid"])}, "## 交付步骤\n1. valid"),
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
            assert await _generate_plan("original task") == PlanOutput(steps=["first", "second"])

        create_agent.assert_called_once()
        assert create_agent.call_args.kwargs["model"] is model
        assert create_agent.call_args.kwargs["tools"] == []
        assert create_agent.call_args.kwargs["system_prompt"] == PLAN_SYSTEM_PROMPT
        response_format = create_agent.call_args.kwargs["response_format"]
        assert isinstance(response_format, ProviderStrategy)
        assert response_format.schema is PlanOutput
        assert response_format.to_model_kwargs()["response_format"]["type"] == "json_schema"
        assert "middleware" not in create_agent.call_args.kwargs
        planner.ainvoke.assert_awaited_once_with(
            {"messages": [{"role": "user", "content": "用户任务：\noriginal task"}]}
        )

    @pytest.mark.asyncio
    async def test_generate_plan_includes_revision_feedback(self) -> None:
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
        ):
            await _generate_plan("original task")
            result = await _generate_plan("original task", "include tests", "## 交付步骤\n1. first plan")

        assert planner.ainvoke.await_count == 2
        revised_request = planner.ainvoke.await_args_list[1].args[0]["messages"][0]["content"]
        assert "original task" in revised_request
        assert "first plan" in revised_request
        assert "include tests" in revised_request
        assert "original task" in planner.ainvoke.await_args_list[0].args[0]["messages"][0]["content"]
        assert result == PlanOutput(steps=["revised plan"])

    @pytest.mark.asyncio
    async def test_generate_plan_rejects_missing_structured_response(self) -> None:
        planner = SimpleNamespace(ainvoke=AsyncMock(return_value={}))
        with (
            patch("fragile.commands.plan.get_model"),
            patch("fragile.commands.plan.create_deep_agent", return_value=planner),
            pytest.raises(PlanGenerationError),
        ):
            await _generate_plan("task")

    @pytest.mark.asyncio
    async def test_generate_plan_rejects_unknown_response_type(self) -> None:
        planner = SimpleNamespace(ainvoke=AsyncMock(return_value={"structured_response": {"steps": ["plan"]}}))
        with (
            patch("fragile.commands.plan.get_model"),
            patch("fragile.commands.plan.create_deep_agent", return_value=planner),
            pytest.raises(PlanGenerationError),
        ):
            await _generate_plan("task")
        planner.ainvoke.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_generate_plan_propagates_agent_errors(self) -> None:
        planner = SimpleNamespace(ainvoke=AsyncMock(side_effect=RuntimeError("agent failed")))
        with (
            patch("fragile.commands.plan.get_model"),
            patch("fragile.commands.plan.create_deep_agent", return_value=planner),
            pytest.raises(RuntimeError, match="agent failed"),
        ):
            await _generate_plan("task")

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
    async def test_empty_plan_is_rejected(self, state: object) -> None:
        planner = SimpleNamespace(ainvoke=AsyncMock(return_value=state))

        with (
            patch("fragile.commands.plan.get_model"),
            patch("fragile.commands.plan.create_deep_agent", return_value=planner),
            pytest.raises(PlanGenerationError),
        ):
            await _generate_plan("task")
