import typer

from fragile.commands.interactive import interactive

app = typer.Typer(help="Fragile CLI for interacting with the Tomorrow agent.")


@app.callback(invoke_without_command=True)
def main(
    thread: str | None = typer.Option(None, "--thread", "-t", help="Thread UUID to resume a conversation."),
) -> None:
    """Start an interactive session. Enter /quit to exit."""
    interactive(thread)
