from __future__ import annotations
from typing import Optional
from manta.sdk.models import ModelClient
from manta.sdk.features import FeatureStoreClient
from manta.feature_store.store import FeatureStore
from manta.serving.server import InferenceServer
from manta.registry.registry import ModelRegistry
from manta.monitoring.service import ModelMonitoringService
from manta.pipeline.executor import PipelineExecutor

class Client:
    """Unified Python SDK Entrypoint (`import manta`)."""
    def __init__(self, endpoint: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.endpoint = endpoint
        self.api_key = api_key
        self.serving = ModelClient(endpoint)
        self.features = FeatureStoreClient(endpoint)
        
        # Local system accessors
        self.feature_store = FeatureStore()
        self.inference_server = InferenceServer()
        self.registry = ModelRegistry()
        self.monitoring = ModelMonitoringService()
        self.pipeline_executor = PipelineExecutor()
