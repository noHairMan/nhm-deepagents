"""Plan review workflow for the Fragile CLI."""

from typing import Any

import asyncclick as click
from deepagents import create_deep_agent
from pydantic import BaseModel

from fragile.exceptions import AgentResponseError
from tomorrow.core.model import get_model

PLAN_SYSTEM_PROMPT = """你是计划助手。请仅分析用户任务并输出清晰、可执行的分步计划。
规划阶段不得执行任务、委派子代理、读写文件或采取任何外部操作。仅使用 write_todos 工具记录待执行步骤，
不要将任何步骤标记为已完成；不要声称已执行任何工作。"""


class PlanGenerationError(AgentResponseError):
    """Raised when the configured model does not return a usable plan."""


class PlanOutput(BaseModel):
    """Structured plan returned by the planning agent."""

    steps: list[str]


def _format_todos(state: Any) -> str:
    """Format usable structured plan steps as a reviewable plan."""
    response = state.get("structured_response") if isinstance(state, dict) else None
    steps = response.steps if isinstance(response, PlanOutput) else []
    steps = [step.strip() for step in steps if isinstance(step, str) and step.strip()]
    return "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))


async def _generate_plan(task: str, feedback: str | None = None, previous_plan: str | None = None) -> str:
    request = f"用户任务：\n{task}"
    if feedback is not None:
        request += f"\n\n此前计划：\n{previous_plan}\n\n用户对计划的修改要求：\n{feedback}"
    planner = create_deep_agent(
        model=get_model(),
        tools=[],
        system_prompt=PLAN_SYSTEM_PROMPT,
        response_format=PlanOutput,
    )
    state = await planner.ainvoke({"messages": [{"role": "user", "content": request}]})
    plan = _format_todos(state)
    if not plan:
        raise PlanGenerationError("规划 agent 未返回有效待办步骤。")
    return plan


async def review_plan(task: str) -> str | None:
    """Return the confirmed plan, or None if the user cancels review."""
    try:
        plan = await _generate_plan(task)
        while True:
            click.echo("\n计划：\n")
            click.echo(plan)
            action = (await click.prompt("操作：[c]确认执行 / [m]修改计划 / [x]取消")).strip().lower()
            if action in {"c", "confirm", "确认"}:
                return plan
            if action in {"x", "cancel", "取消", "q", "quit"}:
                click.echo("已取消。")
                return None
            if action in {"m", "modify", "修改"}:
                feedback = (await click.prompt("请描述修改要求")).strip()
                if not feedback:
                    click.echo("修改要求不能为空。")
                    continue
                plan = await _generate_plan(task, feedback, plan)
                continue
            click.echo("请输入 c（确认）、m（修改）或 x（取消）。")
    except EOFError, KeyboardInterrupt, click.Abort:
        click.echo("\n已退出计划审阅，未确认执行。")
        return None
