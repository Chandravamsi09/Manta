from __future__ import annotations
from typing import Dict, Any, List, Optional
from manta.feature_store.entity import Entity
from manta.feature_store.feature_view import FeatureView
from manta.feature_store.online_store import OnlineStore, InMemoryOnlineStore, RedisOnlineStore
from manta.feature_store.offline_store import OfflineStore, ParquetOfflineStore, InMemoryOfflineStore
from manta.feature_store.point_in_time import PointInTimeJoinEngine
from manta.feature_store.ingestion import FeatureIngestionPipeline
from manta.core.errors import FeatureStoreError
from manta.core.logging import get_logger

logger = get_logger("feature_store")

class FeatureStore:
    """Unified Feature Store Client providing catalog registry, online retrieval, and historical joins."""
    def __init__(
        self,
        online_store: Optional[OnlineStore] = None,
        offline_store: Optional[OfflineStore] = None
    ):
        self.online_store = online_store or InMemoryOnlineStore()
        self.offline_store = offline_store or InMemoryOfflineStore()
        self.join_engine = PointInTimeJoinEngine(self.offline_store)
        self.ingestion_pipeline = FeatureIngestionPipeline(self.online_store, self.offline_store)
        
        self._entities: Dict[str, Entity] = {}
        self._feature_views: Dict[str, FeatureView] = {}

    def register_entity(self, entity: Entity) -> None:
        self._entities[entity.name] = entity
        logger.info(f"Registered Entity: {entity.name} (key={entity.join_key})")

    def register_feature_view(self, feature_view: FeatureView) -> None:
        for ent in feature_view.entities:
            if ent.name not in self._entities:
                self.register_entity(ent)
        self._feature_views[feature_view.name] = feature_view
        logger.info(f"Registered FeatureView: {feature_view.name} ({len(feature_view.features)} features)")

    def get_feature_view(self, name: str) -> FeatureView:
        if name not in self._feature_views:
            raise FeatureStoreError(f"FeatureView '{name}' not found")
        return self._feature_views[name]

    def list_feature_views(self) -> List[FeatureView]:
        return list(self._feature_views.values())

    def ingest(self, feature_view_name: str, records: List[Dict[str, Any]]) -> int:
        fv = self.get_feature_view(feature_view_name)
        return self.ingestion_pipeline.ingest_batch(fv, records)

    def get_online_features(
        self,
        feature_view_name: str,
        entity_keys: List[str],
        features: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        fv = self.get_feature_view(feature_view_name)
        return self.online_store.batch_get(fv.name, entity_keys, features)

    def get_historical_features(
        self,
        entity_df: List[Dict[str, Any]],
        entity_timestamp_col: str,
        feature_view_names: List[str],
        selected_features: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        fvs = [self.get_feature_view(name) for name in feature_view_names]
        return self.join_engine.join_features(entity_df, entity_timestamp_col, fvs, selected_features)
