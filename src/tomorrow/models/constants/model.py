from tomorrow.core.enums import TextChoices


class ModelType(TextChoices):
    OLLAMA = "ollama", "Ollama"
    ANTHROPIC = "anthropic", "Anthropic"
    OPENAI = "openai", "OpenAI"
