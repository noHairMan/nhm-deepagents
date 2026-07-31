import os
from pathlib import Path
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FragileSettings(BaseSettings):
    APP: str = "fragile"
    AGENT: str = "tomorrow.core.agent.AgentManager.create_agent"
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent
    INTERRUPT_EXIT_THRESHOLD: float = Field(default=0.5, gt=0)
    ENABLED_COMMANDS: tuple[str, ...] = (
        "fragile.commands.interactive.commands.quit.QuitCommand",
        "fragile.commands.interactive.commands.new.NewCommand",
        "fragile.commands.interactive.commands.history.HistoryCommand",
    )

    model_config = SettingsConfigDict(
        env_prefix="FRAGILE_",
        env_nested_delimiter="__",
        extra="ignore",
        env_file=os.environ.get("FRAGILE_ENV_FILE", ".env"),
    )
