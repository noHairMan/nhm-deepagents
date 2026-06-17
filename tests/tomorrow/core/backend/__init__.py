from unittest.mock import patch

import pytest

from tomorrow.core.backend import get_backend
from tomorrow.exceptions import TomorrowBackendError
from tomorrow.models.constants import BackendType


class TestBackends:
    def test_get_backend_filesystem(self):
        from deepagents.backends import FilesystemBackend

        from tomorrow.conf import settings

        with patch.object(
            settings, "BACKEND", {"type": BackendType.FILESYSTEM, BackendType.FILESYSTEM.value: {"root_dir": "/tmp"}}
        ):
            backend = get_backend()
            assert isinstance(backend, FilesystemBackend)
            assert backend.virtual_mode is True

    def test_get_backend_filesystem_no_root_dir(self):
        from tomorrow.conf import settings

        with patch.object(settings, "BACKEND", {"type": BackendType.FILESYSTEM, BackendType.FILESYSTEM.value: {}}):
            with pytest.raises(TomorrowBackendError, match="root_dir is required for Filesystem backend"):
                get_backend()

    def test_get_backend_local_shell(self):
        from deepagents.backends import LocalShellBackend

        from tomorrow.conf import settings

        with patch.object(
            settings, "BACKEND", {"type": BackendType.LOCAL_SHELL, BackendType.LOCAL_SHELL.value: {"root_dir": "/tmp"}}
        ):
            backend = get_backend()
            assert isinstance(backend, LocalShellBackend)

    def test_get_backend_local_shell_no_root_dir(self):
        from tomorrow.conf import settings

        with patch.object(settings, "BACKEND", {"type": BackendType.LOCAL_SHELL, BackendType.LOCAL_SHELL.value: {}}):
            with pytest.raises(TomorrowBackendError, match="root_dir is required for LocalShell backend"):
                get_backend()

    def test_get_backend_invalid(self):
        from tomorrow.conf import settings

        with patch.object(settings, "BACKEND", {"type": "invalid"}):
            with pytest.raises(TomorrowBackendError, match="Unsupported backend type: invalid"):
                get_backend()
