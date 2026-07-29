from pathlib import Path

import typer

from fragile.commands.interactive import interactive
from tomorrow.conf import settings
from tomorrow.models.constants import CheckpointType

app = typer.Typer(help="Fragile CLI for interacting with the Tomorrow agent.")


def configure_checkpoint() -> None:
    settings.CHECKPOINT.type = CheckpointType.SQLITE
    settings.CHECKPOINT.sqlite.path = Path.cwd() / "fragile.db"


@app.callback(invoke_without_command=True)
def main(
    thread: str | None = typer.Option(None, "--thread", "-t", help="Thread UUID to resume a conversation."),
) -> None:
    """Start an interactive session. Enter /quit to exit."""
    interactive(thread)


if __name__ == "__main__":  # pragma: no cover
    configure_checkpoint()
    app()
