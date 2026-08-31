from __future__ import annotations
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from manta.serving.request import InferenceRequest, InferenceResponse
from manta.serving.batcher import DynamicBatcher
from manta.core.errors import ServingError
from manta.core.logging import get_logger

logger = get_logger("model_router")

@dataclass
class CanaryRoute:
    version: str
    weight: float  # 0.0 to 1.0

class TrafficSplitter:
    """Traffic routing controller for Canary, Shadow, and A/B Testing deployments."""
    def __init__(self, routes: List[CanaryRoute]):
        total_weight = sum(r.weight for r in routes)
        if abs(total_weight - 1.0) > 1e-4:
            raise ValueError(f"Route weights must sum to 1.0, got {total_weight}")
        self.routes = routes

    def select_route(self) -> str:
        r = random.random()
        cumulative = 0.0
        for route in self.routes:
            cumulative += route.weight
            if r <= cumulative:
                return route.version
        return self.routes[-1].version


class ModelRouter:
    """Routes requests to appropriate versioned model batchers."""
    def __init__(self):
        # { model_name: { version: DynamicBatcher } }
        self._routes: Dict[str, Dict[str, DynamicBatcher]] = {}
        self._traffic_splitters: Dict[str, TrafficSplitter] = {}

    def register_worker(self, batcher: DynamicBatcher) -> None:
        name = batcher.worker.model_name
        ver = batcher.worker.version
        if name not in self._routes:
            self._routes[name] = {}
        self._routes[name][ver] = batcher
        batcher.start()

    def set_traffic_split(self, model_name: str, routes: List[CanaryRoute]) -> None:
        self._traffic_splitters[model_name] = TrafficSplitter(routes)

    def route_request(self, request: InferenceRequest) -> InferenceResponse:
        if request.model_name not in self._routes:
            raise ServingError(f"Model '{request.model_name}' not registered in router")

        versions = self._routes[request.model_name]
        target_version = request.model_version

        if not target_version:
            if request.model_name in self._traffic_splitters:
                target_version = self._traffic_splitters[request.model_name].select_route()
            else:
                target_version = list(versions.keys())[-1]

        if target_version not in versions:
            raise ServingError(f"Version '{target_version}' for model '{request.model_name}' not found")

        batcher = versions[target_version]
        return batcher.submit(request)
