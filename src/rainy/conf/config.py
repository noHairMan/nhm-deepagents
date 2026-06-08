import os
from typing import Any

from tomorrow.utils.functional import SimpleLazyObject


def _get_settings() -> Any:
    from dynaconf import Dynaconf

    app_name = os.environ.get("RAINY_APP", "rainy")
    settings_module = os.environ.get("RAINY_SETTINGS_MODULE", "rainy.settings")

    from rainy.settings import BASE_DIR

    settings_file = "/".join(settings_module.split(".")) + ".py"
    abs_settings_path = BASE_DIR / settings_file

    return Dynaconf(
        envvar_prefix=app_name.upper(),
        settings_files=[str(abs_settings_path) if abs_settings_path.exists() else settings_file],
        load_dotenv=True,
    )


settings = SimpleLazyObject(_get_settings)
