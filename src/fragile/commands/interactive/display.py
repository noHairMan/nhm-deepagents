"""Terminal display handling."""

from uuid import UUID

import typer
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


def clear_screen() -> None:
    typer.echo("\033[2J\033[3J\033[H", nl=False, color=True)


def enter_fullscreen() -> None:
    """Switch to a terminal screen isolated from the main scrollback buffer."""
    typer.echo("\033[?1049h", nl=False, color=True)


def leave_fullscreen() -> None:
    """Restore the terminal's main screen and its scrollback buffer."""
    typer.echo("\033[?1049l", nl=False, color=True)


def print_stream(content: str) -> None:
    """打印流式响应内容，但不在每个片段后追加换行。"""
    console.print(content, end="")


def show_startup(thread_id: UUID, resumed: bool) -> None:
    """显示交互式会话的启动信息。"""
    console.print(Text(STARTUP_BANNER, style="cyan"), end="")
    if resumed:
        console.print(Panel(f"已恢复会话  {thread_id}", title="Fragile", border_style="green"))
    else:
        console.print(
            Panel(
                "Fresh start\nAll previous messages and task state have been cleared\n"
                "Use --thread to continue a previous conversation",
                title="Fragile",
                border_style="yellow",
            )
        )
    console.print("[bold green]✓ Connected to Tomorrow agent[/bold green]")
    console.print("[bold cyan]● Fragile is ready.[/bold cyan]\n")
