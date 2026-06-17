from deepagents.backends import FilesystemBackend

from tomorrow.conf import settings
from tomorrow.exceptions import TomorrowBackendError
from tomorrow.models.constants import BackendType


def get_backend() -> FilesystemBackend:
    backend_config = settings.BACKEND.get(BackendType.FILESYSTEM, {})
    root_dir = backend_config.get("root_dir")
    if not root_dir:
        raise TomorrowBackendError("root_dir is required for Filesystem backend")
    return FilesystemBackend(root_dir=root_dir, virtual_mode=True)
