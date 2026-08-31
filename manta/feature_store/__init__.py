"""
Manta Feature Store: Dual-tier online/offline feature engine with point-in-time joins.
"""

from manta.feature_store.entity import Entity
from manta.feature_store.feature import Feature, FeatureType
from manta.feature_store.feature_view import FeatureView, BatchFeatureView, StreamFeatureView
from manta.feature_store.online_store import OnlineStore, InMemoryOnlineStore, RedisOnlineStore
from manta.feature_store.offline_store import OfflineStore, ParquetOfflineStore, InMemoryOfflineStore
from manta.feature_store.point_in_time import PointInTimeJoinEngine
from manta.feature_store.ingestion import FeatureIngestionPipeline, StreamIngestor
from manta.feature_store.store import FeatureStore

__all__ = [
    "Entity",
    "Feature",
    "FeatureType",
    "FeatureView",
    "BatchFeatureView",
    "StreamFeatureView",
    "OnlineStore",
    "InMemoryOnlineStore",
    "RedisOnlineStore",
    "OfflineStore",
    "ParquetOfflineStore",
    "InMemoryOfflineStore",
    "PointInTimeJoinEngine",
    "FeatureIngestionPipeline",
    "StreamIngestor",
    "FeatureStore",
]

# Feature store point-in-time subsystem initialized
