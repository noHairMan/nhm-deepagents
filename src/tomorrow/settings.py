from pathlib import Path
from typing import Final

from tomorrow.models.constants.checkpoint import CheckpointType

APP: Final = "TOMORROW"
BASE_DIR: Final = Path(__file__).resolve().parent.parent

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3.5:9b"
CHECKPOINT = {
    "type": CheckpointType.MEMORY,
}
