from __future__ import annotations
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from manta.serving.server import InferenceServer
from manta.feature_store.store import FeatureStore
from manta.registry.registry import ModelRegistry
from manta.monitoring.service import ModelMonitoringService
from manta.gateway.auth import Authenticator, UserPrincipal, Role
from manta.gateway.rate_limiter import TokenBucketRateLimiter
from manta.gateway.telemetry import MetricsExporter

def create_app() -> FastAPI:
    app = FastAPI(title="Manta ML Systems Platform", version="1.0.0")
    
    server = InferenceServer()
    feature_store = FeatureStore()
    registry = ModelRegistry()
    monitoring = ModelMonitoringService()
    auth = Authenticator()
    rate_limiter = TokenBucketRateLimiter()
    metrics = MetricsExporter()

    # Pre-register default linear baseline model
    server.register_model("fraud_detector", "v1.0")

    @app.get("/health")
    def health_check():
        metrics.increment("manta_health_checks_total")
        return {"status": "HEALTHY", "cluster": "manta-primary-cluster", "version": "1.0.0"}

    @app.get("/metrics")
    def get_metrics():
        return metrics.export_prometheus()

    class InferencePayload(BaseModel):
        model_name: str
        version: Optional[str] = None
        inputs: Dict[str, Any]

    @app.post("/v1/models/predict")
    def predict(payload: InferencePayload):
        if not rate_limiter.acquire("api_client"):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        metrics.increment("manta_inference_requests_total")
        resp = server.predict(payload.model_name, payload.inputs, version=payload.version)
        metrics.record_timing("manta_inference_latency", resp.latency_ms)
        return resp.to_dict()

    class FeatureLookupPayload(BaseModel):
        feature_view: str
        entity_keys: List[str]
        features: Optional[List[str]] = None

    @app.post("/v1/features/online")
    def get_online_features(payload: FeatureLookupPayload):
        metrics.increment("manta_feature_lookups_total")
        try:
            return feature_store.get_online_features(payload.feature_view, payload.entity_keys, payload.features)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/v1/models")
    def list_models():
        return [m.to_dict() for m in registry.list_models()]

    return app
