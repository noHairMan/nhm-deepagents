"""Structured plan data shared by planning and interactive sessions."""

from pydantic import BaseModel, Field


class PlanOutput(BaseModel):
    """Structured plan returned by the planning agent."""

    requirements: list[str] = Field(default_factory=list)
    technical_design: list[str] = Field(default_factory=list)
    testing: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)


def _format_section(title: str, entries: list[str]) -> list[str]:
    values = [entry.strip() for entry in entries if isinstance(entry, str) and entry.strip()]
    if not values:
        return []
    return [f"## {title}", *(f"- {value}" for value in values)]


def format_plan(plan: PlanOutput) -> str:
    """Serialize a structured plan to stable, reviewable Markdown."""
    sections = [
        *_format_section("需求", plan.requirements),
        *_format_section("技术设计", plan.technical_design),
        *_format_section("测试", plan.testing),
    ]
    steps = [step.strip() for step in plan.steps if isinstance(step, str) and step.strip()]
    if steps:
        sections.extend(("## 交付步骤", *(f"{index}. {step}" for index, step in enumerate(steps, start=1))))
    return "\n".join(sections)
