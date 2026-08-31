import pytest
import time
from manta.serving.server import InferenceServer
from manta.serving.worker import NativePythonWorker
from manta.serving.batcher import DynamicBatcher, BatcherConfig
from manta.serving.request import InferenceRequest, RequestPriority
from manta.serving.router import CanaryRoute

def test_dynamic_batching_and_concurrency():
    worker = NativePythonWorker("fraud_model", "v1.0")
    config = BatcherConfig(max_batch_size=4, max_latency_ms=10.0)
    batcher = DynamicBatcher(worker, config=config)
    batcher.start()

    req1 = InferenceRequest(inputs={"features": [1.0, 2.0, 3.0, 4.0]}, priority=RequestPriority.HIGH)
    req2 = InferenceRequest(inputs={"features": [0.0, 0.5, 1.0, 1.5]}, priority=RequestPriority.NORMAL)

    resp1 = batcher.submit(req1)
    resp2 = batcher.submit(req2)

    assert resp1.status_code == 200
    assert "prediction" in resp1.outputs
    assert resp2.status_code == 200
    assert "prediction" in resp2.outputs
    batcher.stop()

def test_inference_server_router_and_canary():
    server = InferenceServer()
    server.register_model("risk_model", "v1.0")
    server.register_model("risk_model", "v2.0")

    server.router.set_traffic_split("risk_model", [
        CanaryRoute(version="v1.0", weight=0.8),
        CanaryRoute(version="v2.0", weight=0.2),
    ])

    resp = server.predict("risk_model", {"features": [0.5, 0.5, 0.5, 0.5]})
    assert resp.status_code == 200
    assert resp.model_version in ("v1.0", "v2.0")
