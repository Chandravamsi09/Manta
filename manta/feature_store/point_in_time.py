from __future__ import annotations
import datetime
from typing import List, Dict, Any, Optional
from manta.feature_store.feature_view import FeatureView
from manta.feature_store.offline_store import OfflineStore
from manta.core.logging import get_logger
from manta.core.errors import FeatureStoreError

logger = get_logger("point_in_time_join")

class PointInTimeJoinEngine:
    """
    Mathematically sound temporal join engine.
    For each observation in the entity DataFrame (with observation timestamp T_obs),
    finds the latest feature value recorded at timestamp T_feat such that T_feat <= T_obs,
    guaranteeing ZERO future data leakage during training dataset construction.
    """
    def __init__(self, offline_store: OfflineStore):
        self.offline_store = offline_store

    def join_features(
        self,
        entity_df: List[Dict[str, Any]],
        entity_timestamp_col: str,
        feature_views: List[FeatureView],
        selected_features: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        if not entity_df:
            return []

        # Validate entity_df has required timestamp
        for row in entity_df:
            if entity_timestamp_col not in row:
                raise FeatureStoreError(f"Entity row missing timestamp column: '{entity_timestamp_col}'")

        # Cache historical tables for feature views
        fv_history: Dict[str, List[Dict[str, Any]]] = {}
        for fv in feature_views:
            records = self.offline_store.read_records(fv.name)
            # Sort records ascending by timestamp
            records_sorted = sorted(records, key=lambda x: x.get("_timestamp", 0.0))
            fv_history[fv.name] = records_sorted

        joined_results: List[Dict[str, Any]] = []

        for row in entity_df:
            enriched_row = row.copy()
            raw_obs_ts = row[entity_timestamp_col]
            obs_ts = raw_obs_ts.timestamp() if isinstance(raw_obs_ts, datetime.datetime) else float(raw_obs_ts)

            for fv in feature_views:
                join_keys = fv.get_join_keys()
                history = fv_history.get(fv.name, [])

                # Find latest feature update before or at obs_ts
                latest_match: Optional[Dict[str, Any]] = None
                for rec in history:
                    rec_ts = rec.get("_timestamp", 0.0)
                    if rec_ts > obs_ts:
                        break  # since history is sorted asc, no further records are <= obs_ts

                    # Check entity key matching
                    matched = True
                    for jk in join_keys:
                        if row.get(jk) != rec.get(jk):
                            matched = False
                            break
                    if matched:
                        latest_match = rec

                # Project selected features
                for feat in fv.features:
                    if selected_features is None or feat.name in selected_features or f"{fv.name}:{feat.name}" in selected_features:
                        col_name = f"{fv.name}__{feat.name}"
                        if latest_match and feat.name in latest_match:
                            enriched_row[col_name] = latest_match[feat.name]
                        else:
                            enriched_row[col_name] = feat.default_value

            joined_results.append(enriched_row)

        return joined_results

# Temporal Point-in-Time Join Engine with Zero Data Leakage Guarantees
