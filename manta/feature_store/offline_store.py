from __future__ import annotations
import os
import json
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from abc import ABC, abstractmethod
from manta.core.logging import get_logger
from manta.core.errors import FeatureStoreError

logger = get_logger("offline_store")

class OfflineStore(ABC):
    """Interface for analytical historical feature storage."""
    @abstractmethod
    def write_records(self, feature_view: str, records: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    def read_records(
        self,
        feature_view: str,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None
    ) -> List[Dict[str, Any]]:
        pass


class InMemoryOfflineStore(OfflineStore):
    """In-memory historical feature store for fast unit testing and benchmarks."""
    def __init__(self):
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    def write_records(self, feature_view: str, records: List[Dict[str, Any]]) -> None:
        if feature_view not in self._store:
            self._store[feature_view] = []
        for r in records:
            rec = r.copy()
            if "_timestamp" not in rec:
                rec["_timestamp"] = datetime.datetime.utcnow().timestamp()
            elif isinstance(rec["_timestamp"], datetime.datetime):
                rec["_timestamp"] = rec["_timestamp"].timestamp()
            self._store[feature_view].append(rec)

    def read_records(
        self,
        feature_view: str,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None
    ) -> List[Dict[str, Any]]:
        all_recs = self._store.get(feature_view, [])
        if not start_time and not end_time:
            return [r.copy() for r in all_recs]
        
        st = start_time.timestamp() if start_time else 0.0
        et = end_time.timestamp() if end_time else float("inf")
        
        filtered = []
        for r in all_recs:
            t = r.get("_timestamp", 0.0)
            if st <= t <= et:
                filtered.append(r.copy())
        return filtered


class ParquetOfflineStore(OfflineStore):
    """Partitioned Parquet/JSONL offline storage for scalable ML training datasets."""
    def __init__(self, base_dir: str | Path = "./data/feature_store"):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._fallback = InMemoryOfflineStore()

    def _get_path(self, feature_view: str) -> Path:
        p = self.base_dir / feature_view
        p.mkdir(parents=True, exist_ok=True)
        return p / "data.jsonl"

    def write_records(self, feature_view: str, records: List[Dict[str, Any]]) -> None:
        self._fallback.write_records(feature_view, records)
        fpath = self._get_path(feature_view)
        with open(fpath, "a", encoding="utf-8") as f:
            for r in records:
                rec = r.copy()
                if "_timestamp" not in rec:
                    rec["_timestamp"] = datetime.datetime.utcnow().timestamp()
                elif isinstance(rec["_timestamp"], datetime.datetime):
                    rec["_timestamp"] = rec["_timestamp"].timestamp()
                f.write(json.dumps(rec) + "
")

    def read_records(
        self,
        feature_view: str,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None
    ) -> List[Dict[str, Any]]:
        fpath = self._get_path(feature_view)
        if not fpath.exists():
            return self._fallback.read_records(feature_view, start_time, end_time)
        
        records = []
        st = start_time.timestamp() if start_time else 0.0
        et = end_time.timestamp() if end_time else float("inf")
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    t = r.get("_timestamp", 0.0)
                    if st <= t <= et:
                        records.append(r)
        return records
