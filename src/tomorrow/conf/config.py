from tomorrow.settings import TomorrowSettings
from tomorrow.utils.functional import SimpleLazyObject


def _get_settings() -> TomorrowSettings:
    return TomorrowSettings()


settings = SimpleLazyObject(_get_settings)
