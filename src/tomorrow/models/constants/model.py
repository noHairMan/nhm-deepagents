from tomorrow.core.enums import TextChoices


class ModelType(TextChoices):
    OLLAMA = "ollama", "Ollama"
    HUGGINGFACE = "huggingface", "HuggingFace"
