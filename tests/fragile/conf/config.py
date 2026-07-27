from fragile.conf import settings
from fragile.settings import FragileSettings
from tomorrow.utils.functional import SimpleLazyObject


class TestConfig:
    def test_settings_is_lazy(self) -> None:
        assert isinstance(settings, SimpleLazyObject)

    def test_settings_loads_fragile_defaults(self) -> None:
        configured = FragileSettings(_env_file=None)

        assert configured.APP == "fragile"
        assert configured.INTERRUPT_EXIT_THRESHOLD == 0.5
