from deepagents.backends import LocalShellBackend

from tomorrow.conf import settings
from tomorrow.exceptions import TomorrowBackendError
from tomorrow.models.constants import BackendType


def get_backend() -> LocalShellBackend:
    backend_config = settings.BACKEND.get(BackendType.LOCAL_SHELL, {})
    root_dir = backend_config.get("root_dir")
    if not root_dir:
        raise TomorrowBackendError("root_dir is required for LocalShell backend")
    return LocalShellBackend(root_dir=root_dir, virtual_mode=True)
