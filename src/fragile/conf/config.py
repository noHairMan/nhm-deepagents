from fragile.settings import FragileSettings
from tomorrow.utils.functional import SimpleLazyObject


def get_settings() -> FragileSettings:
    return FragileSettings()


settings = SimpleLazyObject(get_settings)
