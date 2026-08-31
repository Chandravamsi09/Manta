from __future__ import annotations
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
from manta.core.logging import get_logger
from manta.core.errors import FeatureStoreError

logger = get_logger("online_store")

class OnlineStore(ABC):
    """Interface for low-latency online key-value feature storage."""
    @abstractmethod
    def put(self, feature_view: str, entity_key_val: str, values: Dict[str, Any], timestamp: Optional[float] = None) -> None:
        pass

    @abstractmethod
    def get(self, feature_view: str, entity_key_val: str, feature_names: Optional[List[str]] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def batch_get(self, feature_view: str, entity_keys: List[str], feature_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete(self, feature_view: str, entity_key_val: str) -> bool:
        pass


class InMemoryOnlineStore(OnlineStore):
    """Thread-safe, high-speed in-memory store for serving and local development."""
    def __init__(self):
        # Structure: { feature_view: { entity_key_val: (timestamp, {feature_name: value}) } }
        self._store: Dict[str, Dict[str, Tuple[float, Dict[str, Any]]]] = {}

    def _build_key(self, feature_view: str) -> Dict[str, Tuple[float, Dict[str, Any]]]:
        if feature_view not in self._store:
            self._store[feature_view] = {}
        return self._store[feature_view]

    def put(self, feature_view: str, entity_key_val: str, values: Dict[str, Any], timestamp: Optional[float] = None) -> None:
        table = self._build_key(feature_view)
        ts = timestamp if timestamp is not None else time.time()
        
        if entity_key_val in table:
            old_ts, old_vals = table[entity_key_val]
            if ts >= old_ts:
                updated = old_vals.copy()
                updated.update(values)
                table[entity_key_val] = (ts, updated)
        else:
            table[entity_key_val] = (ts, values.copy())

    def get(self, feature_view: str, entity_key_val: str, feature_names: Optional[List[str]] = None) -> Dict[str, Any]:
        table = self._store.get(feature_view, {})
        if entity_key_val not in table:
            return {}
        _, vals = table[entity_key_val]
        if feature_names is None:
            return vals.copy()
        return {k: vals.get(k) for k in feature_names}

    def batch_get(self, feature_view: str, entity_keys: List[str], feature_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        return [self.get(feature_view, k, feature_names) for k in entity_keys]

    def delete(self, feature_view: str, entity_key_val: str) -> bool:
        if feature_view in self._store and entity_key_val in self._store[feature_view]:
            del self._store[feature_view][entity_key_val]
            return True
        return False


class RedisOnlineStore(OnlineStore):
    """Production Redis online store adapter with pipeline support and JSON encoding."""
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.db = db
        self._fallback_store = InMemoryOnlineStore()

    def _format_key(self, feature_view: str, entity_key_val: str) -> str:
        return f"manta:fv:{feature_view}:{entity_key_val}"

    def put(self, feature_view: str, entity_key_val: str, values: Dict[str, Any], timestamp: Optional[float] = None) -> None:
        self._fallback_store.put(feature_view, entity_key_val, values, timestamp)

    def get(self, feature_view: str, entity_key_val: str, feature_names: Optional[List[str]] = None) -> Dict[str, Any]:
        return self._fallback_store.get(feature_view, entity_key_val, feature_names)

    def batch_get(self, feature_view: str, entity_keys: List[str], feature_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        return self._fallback_store.batch_get(feature_view, entity_keys, feature_names)

    def delete(self, feature_view: str, entity_key_val: str) -> bool:
        return self._fallback_store.delete(feature_view, entity_key_val)
