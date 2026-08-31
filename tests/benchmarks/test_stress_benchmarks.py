import pytest
import time
from manta.serving.server import InferenceServer
from manta.feature_store.store import FeatureStore
from manta.feature_store.entity import Entity
from manta.feature_store.feature_view import FeatureView
from manta.feature_store.feature import Feature
from manta.core.types import DataType

def test_benchmark_inference_throughput():
    server = InferenceServer()
    server.register_model("benchmark_model", "v1.0")

    start_time = time.time()
    total_inferences = 500

    for _ in range(total_inferences):
        resp = server.predict("benchmark_model", {"features": [1.0, 2.0, 3.0, 4.0]})
        assert resp.status_code == 200

    elapsed = time.time() - start_time
    qps = total_inferences / max(0.0001, elapsed)
    assert qps > 100.0  # Verify sub-10ms performance per request
