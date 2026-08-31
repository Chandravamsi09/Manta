from __future__ import annotations
from typing import Dict, Any, Optional, List
from manta.serving.request import InferenceRequest, InferenceResponse, RequestPriority
from manta.serving.batcher import DynamicBatcher
from manta.serving.worker import ModelWorker, NativePythonWorker
from manta.serving.router import ModelRouter, CanaryRoute
from manta.core.logging import get_logger

logger = get_logger("inference_server")

class InferenceServer:
    """Unified high-throughput inference serving cluster."""
    def __init__(self):
        self.router = ModelRouter()

    def register_model(self, model_name: str, version: str, worker: Optional[ModelWorker] = None) -> None:
        w = worker or NativePythonWorker(model_name, version)
        batcher = DynamicBatcher(w)
        self.router.register_worker(batcher)
        logger.info(f"Registered model {model_name}:{version} on InferenceServer")

    def predict(
        self,
        model_name: str,
        inputs: Dict[str, Any],
        version: Optional[str] = None,
        priority: RequestPriority = RequestPriority.NORMAL
    ) -> InferenceResponse:
        req = InferenceRequest(
            inputs=inputs,
            model_name=model_name,
            model_version=version,
            priority=priority
        )
        return self.router.route_request(req)
