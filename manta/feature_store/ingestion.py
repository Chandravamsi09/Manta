from __future__ import annotations
import time
import datetime
from typing import List, Dict, Any, Optional
from manta.feature_store.feature_view import FeatureView
from manta.feature_store.online_store import OnlineStore
from manta.feature_store.offline_store import OfflineStore
from manta.core.logging import get_logger
from manta.core.errors import FeatureStoreError

logger = get_logger("feature_ingestion")

class FeatureIngestionPipeline:
    """Dual-sink ingestion pipeline publishing simultaneously to online & offline stores."""
    def __init__(self, online_store: OnlineStore, offline_store: OfflineStore):
        self.online_store = online_store
        self.offline_store = offline_store

    def ingest_batch(self, feature_view: FeatureView, records: List[Dict[str, Any]], sync_online: bool = True) -> int:
        if not records:
            return 0

        # Validate all records
        for r in records:
            feature_view.validate_record(r)

        # Write to offline analytical store
        self.offline_store.write_records(feature_view.name, records)

        # Write to low-latency online store if enabled
        if sync_online and feature_view.online_enabled:
            join_keys = feature_view.get_join_keys()
            for r in records:
                key_parts = [str(r.get(jk)) for jk in join_keys]
                entity_val = ":".join(key_parts)
                feat_vals = {f.name: r.get(f.name) for f in feature_view.features if f.name in r}
                ts = r.get("_timestamp", time.time())
                self.online_store.put(feature_view.name, entity_val, feat_vals, timestamp=ts)

        logger.info(f"Ingested {len(records)} records into FeatureView '{feature_view.name}' (online={sync_online})")
        return len(records)


class StreamIngestor:
    """High-throughput single-record stream ingestor with micro-batch buffering."""
    def __init__(self, pipeline: FeatureIngestionPipeline, buffer_size: int = 100, flush_interval_sec: float = 1.0):
        self.pipeline = pipeline
        self.buffer_size = buffer_size
        self.flush_interval_sec = flush_interval_sec
        self._buffers: Dict[str, List[Dict[str, Any]]] = {}
        self._last_flush: float = time.time()

    def ingest(self, feature_view: FeatureView, record: Dict[str, Any]) -> None:
        if feature_view.name not in self._buffers:
            self._buffers[feature_view.name] = []
        
        self._buffers[feature_view.name].append(record)
        
        if len(self._buffers[feature_view.name]) >= self.buffer_size or (time.time() - self._last_flush) > self.flush_interval_sec:
            self.flush(feature_view)

    def flush(self, feature_view: FeatureView) -> int:
        buf = self._buffers.get(feature_view.name, [])
        if not buf:
            return 0
        count = self.pipeline.ingest_batch(feature_view, buf)
        self._buffers[feature_view.name] = []
        self._last_flush = time.time()
        return count
