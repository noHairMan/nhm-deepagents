"""Terminal display handling."""

import json
from urllib.parse import urlsplit, urlunsplit
from uuid import UUID

import asyncclick as click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from fragile.commands.interactive.trace import TraceEvent, safe_value, trace_from_json

STARTUP_BANNER = """\
  ███████╗██████╗  █████╗  ██████╗ ██╗██╗     ███████╗
  ██╔════╝██╔══██╗██╔══██╗██╔════╝ ██║██║     ██╔════╝
  █████╗  ██████╔╝███████║██║  ███╗██║██║     █████╗
  ██╔══╝  ██╔══██╗██╔══██║██║   ██║██║██║     ██╔══╝
  ██║     ██║  ██║██║  ██║╚██████╔╝██║███████╗███████╗
  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝╚══════╝╚══════╝
"""
console = Console()
MAX_DISPLAY_CHARS = 4000


def enter_fullscreen() -> None:
    """Switch to a terminal screen isolated from the main scrollback buffer."""
    click.echo("\033[?1049h", nl=False, color=True)


def leave_fullscreen() -> None:
    """Restore the terminal's main screen and its scrollback buffer."""
    click.echo("\033[?1049l", nl=False, color=True)


def print_stream(content: str) -> None:
    """打印流式响应内容，但不在每个片段后追加换行。"""
    console.print(content, end="", markup=False)


def print_thinking(content: str) -> None:
    """Print model-provided thinking in a distinct, safe terminal style."""
    if content:
        console.print(Text(content, style="dim yellow"), end="")


def _truncate(content: str, limit: int = MAX_DISPLAY_CHARS) -> str:
    """Limit one terminal block while keeping a clear indication of truncation."""
    if len(content) <= limit:
        return content
    suffix = "\n… [truncated]"
    return content[: max(0, limit - len(suffix))] + suffix


def _plain_value(value: object) -> str:
    """Format normalized values as safe plain text rather than Rich markup."""
    normalized = safe_value(value)
    if isinstance(normalized, str):
        return _truncate(normalized)
    return _truncate(json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True))


class TimelineRenderer:
    """Append normalized trace events to the terminal without screen redraws."""

    def __init__(self) -> None:
        self._active_text_kind: str | None = None

    def _close_text(self) -> None:
        if self._active_text_kind is not None:
            print_stream("\n")
            self._active_text_kind = None

    def _open_text(self, kind: str, title: str, style: str) -> None:
        if self._active_text_kind == kind:
            return
        self._close_text()
        console.print(Text(title, style=style))
        self._active_text_kind = kind

    def _print_activity(self, title: str, style: str, details: str = "") -> None:
        self._close_text()
        console.print(Text(title, style=style))
        if details:
            console.print(Text(_truncate(details), style="dim"))

    @staticmethod
    def _stage_title(event: TraceEvent, status: str) -> str:
        name = event.name or "unknown"
        if "skill" in name.lower():
            return f"{status} Skill: {name}"
        return f"{status} Subagent: {name}"

    def render(self, event: TraceEvent) -> None:
        """Render one trace event and merge adjacent model content blocks."""
        if event.kind == "thinking":
            self._open_text("thinking", "Thinking (provider summary)", "dim yellow")
            print_thinking(event.content or "")
        elif event.kind == "text":
            self._open_text("text", "Assistant", "bold cyan")
            print_stream(event.content or "")
        elif event.kind == "tool_start":
            details = f"  Input: {_plain_value(event.input)}"
            if event.content:
                details = f"  Command: {_truncate(event.content)}\n{details}"
            self._print_activity(f"⠋ Tool: {event.name or 'unknown'}", "yellow", details)
        elif event.kind == "tool_end":
            self._print_activity(
                f"✓ Completed: {event.name or 'unknown'}", "green", f"  Result: {_plain_value(event.output)}"
            )
        elif event.kind == "tool_error":
            self._print_activity(
                f"✗ Failed: {event.name or 'unknown'}",
                "red",
                f"  Error: {_truncate(event.content or _plain_value(event.output))}",
            )
        elif event.kind == "stage":
            if not event.name or ("subagent" not in event.name.lower() and "skill" not in event.name.lower()):
                return
            status = event.status or "updated"
            body = event.content or ""
            if event.input is not None:
                input_text = _plain_value(event.input)
                body = f"  Input: {input_text}" if not body else f"{body}\n  Input: {input_text}"
            title = self._stage_title(event, "⠋" if status == "running" else "✓")
            self._print_activity(title, "blue", body)

    def finish(self) -> None:
        """Terminate an open streamed text block with one stable newline."""
        self._close_text()


def render_trace(events: list[TraceEvent]) -> None:
    """Replay normalized events using the same renderer as live output."""
    renderer = TimelineRenderer()
    for event in sorted(events, key=lambda item: item.sequence):
        renderer.render(event)
    renderer.finish()


def show_connection_error(provider: str | None = None, model: str | None = None, base_url: str | None = None) -> None:
    """Show a prominent, actionable model connection error."""
    details = ""
    if provider is not None and model is not None and base_url is not None:
        parsed_url = urlsplit(base_url)
        hostname = parsed_url.hostname or parsed_url.netloc
        port = f":{parsed_url.port}" if parsed_url.port is not None else ""
        safe_url = urlunsplit((parsed_url.scheme, f"{hostname}{port}", parsed_url.path, parsed_url.query, ""))
        details = f"（provider: {provider}，模型: {model}，地址: {safe_url}）"
    console.print(
        Text(
            f"模型服务连接失败{details}：请检查服务进程、模型名称、服务地址和账户配置后重试。",
            style="bold red",
        )
    )


def show_request_error(error: str) -> None:
    """Show an actionable model request error."""
    console.print(Text(f"模型请求失败：{error}，请检查请求参数后重试。", style="bold red"))


def replay_outputs(records: list[object]) -> None:
    """Replay persisted user prompts and safe assistant timeline responses."""
    for record in records:
        user_input = getattr(record, "user_input", "")
        assistant_output = getattr(record, "assistant_output", "")
        thinking_output = getattr(record, "thinking_output", "") or ""
        console.print(Text(f"> {user_input}"))
        events = trace_from_json(getattr(record, "trace_payload", None))
        if events:
            render_trace(events)
            continue
        renderer = TimelineRenderer()
        if thinking_output:
            renderer.render(TraceEvent(0, "thinking", content=thinking_output))
        if assistant_output:
            renderer.render(TraceEvent(1, "text", content=assistant_output))
        renderer.finish()


def show_startup(thread_id: UUID, resumed: bool) -> None:
    """显示交互式会话的启动信息。"""
    console.print(Text(STARTUP_BANNER, style="cyan"), end="")
    if resumed:
        console.print(Panel(f"Resumed conversation  {thread_id}", title="Fragile", border_style="green"))
    else:
        console.print(
            Panel(
                "Fresh start\nAll previous messages and task state have been cleared\n"
                "Use --thread to continue a previous conversation",
                title="Fragile",
                border_style="yellow",
            )
        )
    console.print("[bold green]✓ Tomorrow agent client is ready[/bold green]")
    console.print("[bold cyan]● Fragile is ready.[/bold cyan]\n")
