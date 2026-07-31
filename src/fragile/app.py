import asyncclick as click

from fragile.commands.interactive.session import interactive
from fragile.commands.purge import purge_sessions


async def main(ctx: click.Context, thread: str | None) -> None:
    """Start an interactive session. Enter /quit to exit."""
    if ctx and ctx.invoked_subcommand:
        return
    await interactive(thread)


app = click.group(invoke_without_command=True, help="Fragile CLI for interacting with the Tomorrow agent.")(
    click.pass_context(click.option("--thread", "-t", default=None, help="Thread UUID to resume a conversation.")(main))
)


@app.command("purge")
async def purge() -> None:
    """Clear all persisted session information."""
    deleted = await purge_sessions()
    click.echo(f"Cleared {deleted} session records.")
