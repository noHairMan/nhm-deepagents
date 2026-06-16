from pathlib import Path
from typing import Final

from tomorrow.models.constants import BackendType, CheckpointType, ModelType, StoreType

APP: Final = "tomorrow"
BASE_DIR: Final = Path(__file__).resolve().parent.parent

MODEL = {
    "type": ModelType.OLLAMA,
    ModelType.OLLAMA: {
        "model": "qwen3.5:9b",
        "base_url": "http://localhost:11434",
        "temperature": 0,
    },
}
CHECKPOINT = {
    "type": CheckpointType.MEMORY,
    CheckpointType.MEMORY: {},
    CheckpointType.SQLITE: {
        "path": BASE_DIR.parent / "tomorrow.db",
    },
}
BACKEND = {
    "type": BackendType.FILESYSTEM,
    BackendType.FILESYSTEM: {
        "root_dir": BASE_DIR.parent / ".workspace",
    },
    BackendType.LOCAL_SHELL: {
        "root_dir": BASE_DIR.parent / ".workspace",
    },
}

STORE = {
    "type": StoreType.MEMORY,
    StoreType.MEMORY: {},
    StoreType.SQLITE: {
        "path": BASE_DIR.parent / "tomorrow.db",
    },
}
