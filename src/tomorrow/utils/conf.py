import os

from tomorrow.utils.functional import SimpleLazyObject


def _get_settings():
    from dynaconf import Dynaconf

    return Dynaconf(
        envvar_prefix=os.environ.get("TOMORROW_APP", "").upper(),
        settings_files=["/".join(os.environ.get("TOMORROW_SETTINGS_MODULE", "").split(".")) + ".py"],
        load_dotenv=True,
    )


settings = SimpleLazyObject(_get_settings)
