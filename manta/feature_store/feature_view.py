from __future__ import annotations
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import datetime
from manta.feature_store.entity import Entity
from manta.feature_store.feature import Feature
from manta.core.errors import FeatureStoreError

@dataclass
class FeatureView:
    """Schema group representing a set of logically related features tied to entities."""
    name: str
    entities: List[Entity]
    features: List[Feature]
    ttl_seconds: int = 86400 * 30  # 30 days
    online_enabled: bool = True
    batch_source: Optional[str] = None
    stream_source: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def __post_init__(self):
        self._feature_map = {f.name: f for f in self.features}
        self._entity_map = {e.name: e for e in self.entities}

    def get_feature(self, name: str) -> Feature:
        if name not in self._feature_map:
            raise FeatureStoreError(f"Feature '{name}' not found in FeatureView '{self.name}'")
        return self._feature_map[name]

    def get_join_keys(self) -> List[str]:
        return [e.join_key for e in self.entities]

    def validate_record(self, record: Dict[str, Any]) -> None:
        for entity in self.entities:
            if entity.join_key not in record:
                raise FeatureStoreError(f"Record missing required entity join key '{entity.join_key}'")
        for feat in self.features:
            if feat.name in record:
                val = record[feat.name]
                if not feat.validate_value(val):
                    raise FeatureStoreError(f"Invalid value '{val}' for feature '{feat.name}' of type {feat.data_type}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "entities": [e.to_dict() for e in self.entities],
            "features": [f.to_dict() for f in self.features],
            "ttl_seconds": self.ttl_seconds,
            "online_enabled": self.online_enabled,
            "batch_source": self.batch_source,
            "stream_source": self.stream_source,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
        }

@dataclass
class BatchFeatureView(FeatureView):
    query: Optional[str] = None

@dataclass
class StreamFeatureView(FeatureView):
    transformation_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
