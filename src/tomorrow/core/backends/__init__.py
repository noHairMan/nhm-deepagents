from deepagents.backends import FilesystemBackend

from tomorrow.conf import settings
from tomorrow.models.constants import BackendType


def get_backend() -> FilesystemBackend:
    backend_type = settings.BACKEND.get("type")
    backend_config = settings.BACKEND.get(backend_type, {})
    match backend_type:
        case BackendType.FILESYSTEM:
            root_dir = backend_config.get("root_dir")
            if not root_dir:
                raise ValueError("root_dir is required for Filesystem backend")
            return FilesystemBackend(root_dir=root_dir, virtual_mode=True)
        case _:
            raise ValueError(f"Unsupported backend type: {backend_type}")
