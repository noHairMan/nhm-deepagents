import os
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from tomorrow.models.constants import BackendType, CheckpointType, ModelType, StoreType


class BaseConfigModel(BaseModel):
    def get(self, key, default=None):
        return self.model_dump(by_alias=True).get(key, default)

    def __getitem__(self, key):
        return self.model_dump(by_alias=True)[key]


class CheckpointMemoryConfig(BaseConfigModel):
    pass


class CheckpointSqliteConfig(BaseConfigModel):
    path: Path = Path(__file__).resolve().parent.parent.parent / "tomorrow.db"


class CheckpointConfig(BaseConfigModel):
    type: CheckpointType = CheckpointType.MEMORY
    memory: CheckpointMemoryConfig = Field(default_factory=CheckpointMemoryConfig, alias=CheckpointType.MEMORY)
    sqlite: CheckpointSqliteConfig = Field(default_factory=CheckpointSqliteConfig, alias=CheckpointType.SQLITE)


class OllamaConfig(BaseConfigModel):
    model: str = "qwen3.5:9b"
    base_url: str = "http://localhost:11434"
    temperature: float = 0


class HuggingFaceConfig(BaseConfigModel):
    model: str = "mistralai/Mistral-7B-Instruct-v0.2"
    url: str | None = None
    api_key: str | None = None
    temperature: float = 0.1


class AnthropicConfig(BaseConfigModel):
    model: str = "claude-sonnet-5"
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0


class ModelConfig(BaseConfigModel):
    type: ModelType = ModelType.OLLAMA
    ollama: OllamaConfig = Field(default_factory=OllamaConfig, alias=ModelType.OLLAMA)
    huggingface: HuggingFaceConfig = Field(default_factory=HuggingFaceConfig, alias=ModelType.HUGGINGFACE)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig, alias=ModelType.ANTHROPIC)


class FilesystemBackendConfig(BaseConfigModel):
    root_dir: Path = Path(__file__).resolve().parent.parent.parent / ".workspace"


class LocalShellBackendConfig(BaseConfigModel):
    root_dir: Path = Path(__file__).resolve().parent.parent.parent / ".workspace"


class BackendConfig(BaseConfigModel):
    type: BackendType = BackendType.FILESYSTEM
    filesystem: FilesystemBackendConfig = Field(default_factory=FilesystemBackendConfig, alias=BackendType.FILESYSTEM)
    local_shell: LocalShellBackendConfig = Field(default_factory=LocalShellBackendConfig, alias=BackendType.LOCAL_SHELL)


class StoreMemoryConfig(BaseConfigModel):
    pass


class StoreSqliteConfig(BaseConfigModel):
    path: Path = Path(__file__).resolve().parent.parent.parent / "tomorrow.db"


class StoreConfig(BaseConfigModel):
    type: StoreType = StoreType.MEMORY
    memory: StoreMemoryConfig = Field(default_factory=StoreMemoryConfig, alias=StoreType.MEMORY)
    sqlite: StoreSqliteConfig = Field(default_factory=StoreSqliteConfig, alias=StoreType.SQLITE)


class TomorrowSettings(BaseSettings):
    APP: str = "tomorrow"
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent

    MODEL: ModelConfig = Field(default_factory=ModelConfig)
    CHECKPOINT: CheckpointConfig = Field(default_factory=CheckpointConfig)
    BACKEND: BackendConfig = Field(default_factory=BackendConfig)
    STORE: StoreConfig = Field(default_factory=StoreConfig)
    SKILLS: list[str] = Field(default_factory=lambda: ["skills/"])

    model_config = SettingsConfigDict(
        env_prefix="TOMORROW_",
        env_nested_delimiter="__",
        extra="ignore",
        env_file=os.environ.get("TOMORROW_ENV_FILE", ".env"),
    )
