import os
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfigModel(BaseModel):
    def get(self, key, default=None):
        return self.model_dump(by_alias=True).get(key, default)

    def __getitem__(self, key):
        return self.model_dump(by_alias=True)[key]


class FragileSettings(BaseSettings):
    APP: str = "fragile"
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent

    model_config = SettingsConfigDict(
        env_prefix="FRAGILE_",
        env_nested_delimiter="__",
        extra="ignore",
        env_file=os.environ.get("FRAGILE_ENV_FILE", ".env"),
    )
