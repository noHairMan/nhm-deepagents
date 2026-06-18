from rainy.settings import RainySettings
from tomorrow.utils.functional import SimpleLazyObject


def _get_settings() -> RainySettings:
    return RainySettings()


settings = SimpleLazyObject(_get_settings)
