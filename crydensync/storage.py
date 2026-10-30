"""Token storage adapters used by :class:`Cryden`."""

from __future__ import annotations

from typing import Dict, Optional, Protocol, runtime_checkable


@runtime_checkable
class StorageAdapter(Protocol):
    """Small interface for persisting the SDK's token pair."""

    def get(self, key: str) -> Optional[str]: ...

    def set(self, key: str, value: str) -> None: ...

    def remove(self, key: str) -> None: ...


class MemoryStorageAdapter:
    """In-memory token storage. Values do not survive process restarts."""

    def __init__(self) -> None:
        self._values: Dict[str, str] = {}

    def get(self, key: str) -> Optional[str]:
        return self._values.get(key)

    def set(self, key: str, value: str) -> None:
        self._values[key] = value

    def remove(self, key: str) -> None:
        self._values.pop(key, None)


class FileStorageAdapter:
    """Simple file-backed storage for applications that need persistence.

    This adapter writes the serialized token record as plain text. Use an
    encrypted storage implementation when the local filesystem is not trusted.
    """

    def __init__(self, path: str) -> None:
        from pathlib import Path

        self.path = Path(path).expanduser()

    def get(self, key: str) -> Optional[str]:
        import json

        try:
            values = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError, OSError):
            return None
        value = values.get(key)
        return value if isinstance(value, str) else None

    def set(self, key: str, value: str) -> None:
        import json

        try:
            values = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError, OSError):
            values = {}
        values[key] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(values), encoding="utf-8")

    def remove(self, key: str) -> None:
        import json

        try:
            values = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError, OSError):
            return
        values.pop(key, None)
        if values:
            self.path.write_text(json.dumps(values), encoding="utf-8")
        else:
            self.path.unlink(missing_ok=True)


def default_storage_adapter() -> StorageAdapter:
    """Return the safe, process-local default for Python applications."""
    return MemoryStorageAdapter()
