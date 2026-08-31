import pytest
import datetime
from manta.feature_store.entity import Entity
from manta.feature_store.feature import Feature, FeatureType
from manta.feature_store.feature_view import FeatureView
from manta.feature_store.store import FeatureStore
from manta.core.types import DataType

def test_feature_store_online_and_point_in_time_join():
    user_entity = Entity(name="user", join_key="user_id")
    fv = FeatureView(
        name="user_stats",
        entities=[user_entity],
        features=[
            Feature(name="click_rate", data_type=DataType.FLOAT32),
            Feature(name="purchases_count", data_type=DataType.INT32, default_value=0),
        ]
    )

    fs = FeatureStore()
    fs.register_feature_view(fv)

    # Ingest historical stream updates with timestamps
    records = [
        {"user_id": "u1", "click_rate": 0.15, "purchases_count": 2, "_timestamp": 100.0},
        {"user_id": "u1", "click_rate": 0.45, "purchases_count": 5, "_timestamp": 200.0},
        {"user_id": "u2", "click_rate": 0.80, "purchases_count": 12, "_timestamp": 150.0},
    ]
    count = fs.ingest("user_stats", records)
    assert count == 3

    # Test Online Lookup (should return latest state)
    online_res = fs.get_online_features("user_stats", ["u1", "u2"])
    assert len(online_res) == 2
    assert online_res[0]["click_rate"] == 0.45
    assert online_res[0]["purchases_count"] == 5
    assert online_res[1]["click_rate"] == 0.80

    # Test Point-in-Time Join (ensures NO future data leakage)
    observation_df = [
        {"user_id": "u1", "event_ts": 120.0},  # should get state from ts=100 (click_rate=0.15)
        {"user_id": "u1", "event_ts": 250.0},  # should get state from ts=200 (click_rate=0.45)
        {"user_id": "u2", "event_ts": 100.0},  # event before any feature recorded, should get default
    ]

    joined = fs.get_historical_features(
        entity_df=observation_df,
        entity_timestamp_col="event_ts",
        feature_view_names=["user_stats"]
    )

    assert len(joined) == 3
    assert joined[0]["user_stats__click_rate"] == 0.15
    assert joined[0]["user_stats__purchases_count"] == 2

    assert joined[1]["user_stats__click_rate"] == 0.45
    assert joined[1]["user_stats__purchases_count"] == 5

    assert joined[2]["user_stats__click_rate"] is None  # no default set
    assert joined[2]["user_stats__purchases_count"] == 0  # default_value=0
