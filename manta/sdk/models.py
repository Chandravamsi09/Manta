from __future__ import annotations
from typing import Dict, Any, List, Optional
from manta.serving.server import InferenceServer
from manta.serving.request import InferenceResponse

class ModelClient:
    """High-level client for model inference and routing."""
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self._local_server = InferenceServer()
        self._local_server.register_model("fraud_detector", "v1.0")

    def predict(self, model_name: str, inputs: Dict[str, Any], version: Optional[str] = None) -> InferenceResponse:
        return self._local_server.predict(model_name, inputs, version=version)
