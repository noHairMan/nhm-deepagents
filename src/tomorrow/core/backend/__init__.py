from deepagents.backends import BackendProtocol

from tomorrow.conf import settings
from tomorrow.models.constants import BackendType


def get_backend() -> BackendProtocol:
    backend_type = settings.BACKEND.get("type")
    match backend_type:
        case BackendType.FILESYSTEM:
            from .filesystem import get_backend as get_filesystem_backend

            return get_filesystem_backend()
        case BackendType.LOCAL_SHELL:
            from .local_shell import get_backend as get_local_shell_backend

            return get_local_shell_backend()
        case _:
            raise ValueError(f"Unsupported backend type: {backend_type}")
