from tomorrow.settings import TomorrowSettings
from tomorrow.utils.functional import SimpleLazyObject


def get_settings() -> TomorrowSettings:
    return TomorrowSettings()


settings = SimpleLazyObject(get_settings)
