"""Prompt-toolkit plan review interaction."""

from pathlib import Path
from typing import Protocol

import asyncclick as click

from fragile.commands.plan import PlanOutput, _generate_plan, format_plan


class PlanInput(Protocol):
    """Minimal prompt-toolkit input interface used by the review view."""

    async def prompt_async(self, message: str) -> str: ...


def _sections(plan: PlanOutput) -> list[tuple[str, list[str]]]:
    sections = [
        ("需求", plan.requirements),
        ("技术设计", plan.technical_design),
        ("测试", plan.testing),
        ("交付步骤", plan.steps),
    ]
    return [(title, entries) for title, entries in sections if any(entry.strip() for entry in entries)]


async def _prompt(prompt_session: PlanInput, message: str) -> str | None:
    try:
        return await prompt_session.prompt_async(message)
    except EOFError, KeyboardInterrupt, click.Abort:
        click.echo("\n已退出计划审阅，未确认执行。")
        return None


async def review_plan(task: str, prompt_session: PlanInput) -> PlanOutput | None:
    """Review and optionally revise/save a generated plan before approval."""
    plan = await _generate_plan(task)
    response = plan
    index = 0
    while True:
        sections = _sections(response)
        title, entries = sections[index]
        click.echo(f"\n## {title}\n")
        click.echo("\n".join(f"- {entry}" for entry in entries))
        action_input = await _prompt(
            prompt_session,
            "计划操作：[n]下一部分 / [p]上一部分 / [v]全文 / [m]修改 / [s]保存 / [c]确认 / [x]取消 > ",
        )
        if action_input is None:
            return None
        action = action_input.strip().lower()
        if action in {"n", "next"}:
            index = (index + 1) % len(sections)
        elif action in {"p", "previous"}:
            index = (index - 1) % len(sections)
        elif action in {"v", "view"}:
            click.echo(format_plan(response))
        elif action in {"m", "modify"}:
            feedback_input = await _prompt(prompt_session, "请描述修改要求 > ")
            if feedback_input is None:
                return None
            feedback = feedback_input.strip()
            if feedback:
                response = await _generate_plan(task, feedback, format_plan(response))
                index = 0
            else:
                click.echo("修改要求不能为空。")
        elif action in {"s", "save"}:
            filename_input = await _prompt(prompt_session, "Markdown 保存路径 > ")
            if filename_input is None:
                return None
            filename = filename_input.strip()
            if filename:
                try:
                    Path(filename).write_text(format_plan(response) + "\n", encoding="utf-8")
                except OSError as error:
                    click.echo(f"无法保存计划：{error}")
                else:
                    click.echo(f"计划已保存：{filename}")
        elif action in {"c", "confirm", "确认"}:
            return response
        elif action in {"x", "cancel", "取消", "q", "quit"}:
            click.echo("已取消。")
            return None
        else:
            click.echo("无效操作。")
