import asyncio
import inspect

import typer

from fragile.commands.interactive.session import interactive_async
from fragile.commands.purge import purge_sessions

app = typer.Typer(help="Fragile CLI for interacting with the Tomorrow agent.")
interactive = interactive_async


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    thread: str | None = typer.Option(None, "--thread", "-t", help="Thread UUID to resume a conversation."),
) -> None:
    """Start an interactive session. Enter /quit to exit."""
    if ctx is None or ctx.invoked_subcommand is None:
        result = interactive(thread)
        if inspect.isawaitable(result):
            asyncio.run(result)


@app.command("purge")
def purge() -> None:
    """Clear all persisted session information."""
    deleted = purge_sessions()
    typer.echo(f"Cleared {deleted} session records.")
