"""Plan review workflow for the Fragile CLI."""

from typing import Any

from deepagents import create_deep_agent
from langchain.agents.structured_output import ProviderStrategy

from fragile.exceptions import AgentResponseError
from fragile.models.plan import PlanOutput, format_plan
from tomorrow.core.model import get_model

PLAN_SYSTEM_PROMPT = """你是计划助手。请仅分析用户任务并输出结构化计划，内容包括需求、技术设计、测试方案和有序交付步骤。
不适用的分区可以留空，但至少提供一个有意义的分区。规划阶段不得执行任务、委派子代理、读写文件或采取任何外部操作。
仅使用 write_todos 工具记录待执行步骤，不要将任何步骤标记为已完成；不要声称已执行任何工作。"""


class PlanGenerationError(AgentResponseError):
    """Raised when the configured model does not return a usable plan."""


def _format_todos(state: Any) -> str:
    """Format a valid structured plan returned by the planning agent."""
    response = state.get("structured_response") if isinstance(state, dict) else None
    return format_plan(response) if isinstance(response, PlanOutput) else ""


async def _generate_plan(task: str, feedback: str | None = None, previous_plan: str | None = None) -> PlanOutput:
    request = f"用户任务：\n{task}"
    if feedback is not None:
        request += f"\n\n此前计划：\n{previous_plan}\n\n用户对计划的修改要求：\n{feedback}"
    planner = create_deep_agent(
        model=get_model(),
        tools=[],
        system_prompt=PLAN_SYSTEM_PROMPT,
        response_format=ProviderStrategy(PlanOutput),
    )
    state = await planner.ainvoke({"messages": [{"role": "user", "content": request}]})
    response = state.get("structured_response") if isinstance(state, dict) else None
    if not isinstance(response, PlanOutput) or not format_plan(response):
        raise PlanGenerationError("规划 agent 未返回有效计划内容。")
    return response
