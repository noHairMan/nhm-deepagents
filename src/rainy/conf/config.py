from rainy.settings import RainySettings
from tomorrow.utils.functional import SimpleLazyObject


def get_settings() -> RainySettings:
    return RainySettings()


settings = SimpleLazyObject(get_settings)
