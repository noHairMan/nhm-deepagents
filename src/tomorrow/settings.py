from pathlib import Path
from typing import Final

APP = "TOMORROW"
BASE_DIR: Final = Path(__file__).resolve().parent.parent
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3.5:9b"
