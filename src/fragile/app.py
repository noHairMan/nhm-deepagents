import asyncio

import typer

from fragile.commands.interactive.session import interactive
from fragile.commands.purge import purge_sessions

app = typer.Typer(help="Fragile CLI for interacting with the Tomorrow agent.")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    thread: str | None = typer.Option(None, "--thread", "-t", help="Thread UUID to resume a conversation."),
) -> None:
    """Start an interactive session. Enter /quit to exit."""
    if ctx and ctx.invoked_subcommand:
        return
    asyncio.run(interactive(thread))


@app.command("purge")
def purge() -> None:
    """Clear all persisted session information."""
    deleted = asyncio.run(purge_sessions())
    typer.echo(f"Cleared {deleted} session records.")
