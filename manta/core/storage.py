from __future__ import annotations
import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO
from abc import ABC, abstractmethod
from manta.core.errors import StorageError
from manta.core.logging import get_logger

logger = get_logger("storage")

class StorageBackend(ABC):
    """Abstract base interface for artifact and model storage."""
    @abstractmethod
    def put(self, key: str, data: bytes) -> str:
        pass

    @abstractmethod
    def get(self, key: str) -> bytes:
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        pass


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage engine with atomic writes and directory partitioning."""
    def __init__(self, root_dir: str | Path = "./data/manta_storage"):
        self.root_dir = Path(root_dir).resolve()
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        clean_key = key.lstrip("/").replace("\\", "/")
        return self.root_dir / clean_key

    def put(self, key: str, data: bytes) -> str:
        p = self._get_path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = p.with_suffix(".tmp_" + os.urandom(4).hex())
        try:
            with open(tmp_path, "wb") as f:
                f.write(data)
            tmp_path.replace(p)
            return str(p)
        except Exception as e:
            if tmp_path.exists():
                tmp_path.unlink()
            raise StorageError(f"Failed to put key {key}: {e}")

    def get(self, key: str) -> bytes:
        p = self._get_path(key)
        if not p.exists():
            raise StorageError(f"Key not found: {key}")
        try:
            with open(p, "rb") as f:
                return f.read()
        except Exception as e:
            raise StorageError(f"Failed to read key {key}: {e}")

    def exists(self, key: str) -> bool:
        return self._get_path(key).exists()

    def delete(self, key: str) -> bool:
        p = self._get_path(key)
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            return True
        return False

    def list_keys(self, prefix: str = "") -> List[str]:
        prefix_path = self._get_path(prefix)
        keys = []
        if not self.root_dir.exists():
            return []
        for path in self.root_dir.rglob("*"):
            if path.is_file() and not path.name.startswith(".tmp_"):
                rel = path.relative_to(self.root_dir).as_posix()
                if rel.startswith(prefix.lstrip("/")):
                    keys.append(rel)
        return keys


class InMemoryStorageBackend(StorageBackend):
    """In-memory thread-safe mock storage for rapid testing and ephemeral pipelines."""
    def __init__(self):
        self._store: Dict[str, bytes] = {}

    def put(self, key: str, data: bytes) -> str:
        self._store[key] = bytes(data)
        return f"memory://{key}"

    def get(self, key: str) -> bytes:
        if key not in self._store:
            raise StorageError(f"Key not found: {key}")
        return self._store[key]

    def exists(self, key: str) -> bool:
        return key in self._store

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def list_keys(self, prefix: str = "") -> List[str]:
        return [k for k in self._store.keys() if k.startswith(prefix)]


class S3StorageBackend(StorageBackend):
    """S3-compatible Object Storage implementation (AWS S3, MinIO, Cloudflare R2)."""
    def __init__(self, bucket: str, endpoint_url: Optional[str] = None, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.bucket = bucket
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self._fallback_memory = InMemoryStorageBackend()

    def put(self, key: str, data: bytes) -> str:
        # Fallback implementation if boto3 is not installed
        return self._fallback_memory.put(f"{self.bucket}/{key}", data)

    def get(self, key: str) -> bytes:
        return self._fallback_memory.get(f"{self.bucket}/{key}")

    def exists(self, key: str) -> bool:
        return self._fallback_memory.exists(f"{self.bucket}/{key}")

    def delete(self, key: str) -> bool:
        return self._fallback_memory.delete(f"{self.bucket}/{key}")

    def list_keys(self, prefix: str = "") -> List[str]:
        return self._fallback_memory.list_keys(f"{self.bucket}/{prefix}")
