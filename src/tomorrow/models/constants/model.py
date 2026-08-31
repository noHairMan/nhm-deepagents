from tomorrow.core.enums import TextChoices


class ModelType(TextChoices):
    ANTHROPIC = "anthropic", "Anthropic"
    OPENAI = "openai", "OpenAI"
