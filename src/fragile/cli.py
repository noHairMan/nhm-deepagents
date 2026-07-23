from __future__ import annotations

import typer

from fragile.commands.interactive import interactive

app = typer.Typer(help="与 Tomorrow 智能体交互的 Fragile 命令行工具。")


@app.callback(invoke_without_command=True)
def main(
    thread: str | None = typer.Option(None, "--thread", "-t", help="用于恢复会话的线程 UUID。"),
) -> None:
    """启动交互式会话。输入 exit 或 quit 退出。"""
    interactive(thread)


if __name__ == "__main__":  # pragma: no cover
    app()
