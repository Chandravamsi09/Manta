from __future__ import annotations
from typing import Dict, Any, List, Optional
from manta.feature_store.store import FeatureStore

class FeatureStoreClient:
    """High-level client for feature catalog and point-in-time retrieval."""
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self._local_fs = FeatureStore()

    def get_online_features(self, feature_view: str, entity_keys: List[str], features: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        return self._local_fs.get_online_features(feature_view, entity_keys, features)
