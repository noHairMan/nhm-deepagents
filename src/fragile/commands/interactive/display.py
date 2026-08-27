"""Terminal display handling."""

from urllib.parse import urlsplit, urlunsplit
from uuid import UUID

import asyncclick as click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

STARTUP_BANNER = """\
  ███████╗██████╗  █████╗  ██████╗ ██╗██╗     ███████╗
  ██╔════╝██╔══██╗██╔══██╗██╔════╝ ██║██║     ██╔════╝
  █████╗  ██████╔╝███████║██║  ███╗██║██║     █████╗
  ██╔══╝  ██╔══██╗██╔══██║██║   ██║██║██║     ██╔══╝
  ██║     ██║  ██║██║  ██║╚██████╔╝██║███████╗███████╗
  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝╚══════╝╚══════╝
"""
console = Console()


def enter_fullscreen() -> None:
    """Switch to a terminal screen isolated from the main scrollback buffer."""
    click.echo("\033[?1049h", nl=False, color=True)


def leave_fullscreen() -> None:
    """Restore the terminal's main screen and its scrollback buffer."""
    click.echo("\033[?1049l", nl=False, color=True)


def print_stream(content: str) -> None:
    """打印流式响应内容，但不在每个片段后追加换行。"""
    console.print(content, end="")


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


def replay_outputs(records: list[object]) -> None:
    """Replay persisted user prompts and Rich-markup assistant responses."""
    for record in records:
        user_input = getattr(record, "user_input", "")
        assistant_output = getattr(record, "assistant_output", "")
        console.print(Text(f"> {user_input}"))
        if assistant_output:
            console.print(Text.from_markup(assistant_output), end="")
            console.print()


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
