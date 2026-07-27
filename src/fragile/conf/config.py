from fragile.settings import FragileSettings
from tomorrow.utils.functional import SimpleLazyObject


def _get_settings() -> FragileSettings:
    return FragileSettings()


settings = SimpleLazyObject(_get_settings)
