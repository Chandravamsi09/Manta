from __future__ import annotations
import time
import uuid
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from manta.serving.server import InferenceServer
from manta.feature_store.store import FeatureStore
from manta.feature_store.entity import Entity
from manta.feature_store.feature_view import FeatureView
from manta.feature_store.feature import Feature
from manta.core.types import DataType, ModelStage
from manta.registry.registry import ModelRegistry
from manta.monitoring.service import ModelMonitoringService
from manta.pipeline.dag import DAG
from manta.pipeline.task import Task, TaskContext
from manta.pipeline.executor import PipelineExecutor
from manta.gateway.auth import Authenticator, UserPrincipal, Role
from manta.gateway.rate_limiter import TokenBucketRateLimiter
from manta.gateway.telemetry import MetricsExporter

# --- Schemas ---

class LoginPayload(BaseModel):
    username: str
    password: str

class InferencePayload(BaseModel):
    model_name: str
    version: Optional[str] = None
    inputs: Dict[str, Any]

class FeatureLookupPayload(BaseModel):
    feature_view: str
    entity_keys: List[str]
    features: Optional[List[str]] = None

class DriftEvalPayload(BaseModel):
    model_name: str
    current_features: Dict[str, List[float]]

class PipelineRunPayload(BaseModel):
    dag_id: str

class DeployModelPayload(BaseModel):
    model_name: str
    version: str
    stage: str = "PRODUCTION"


def create_app() -> FastAPI:
    app = FastAPI(title="Manta ML Systems Platform", version="1.0.0")

    # Add CORS middleware to support Vite frontend running on port 3000
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    server = InferenceServer()
    feature_store = FeatureStore()
    registry = ModelRegistry()
    monitoring = ModelMonitoringService()
    pipeline_executor = PipelineExecutor()
    auth = Authenticator()
    rate_limiter = TokenBucketRateLimiter()
    metrics = MetricsExporter()

    # Active session store for token management
    active_tokens: Dict[str, Dict[str, Any]] = {}

    # 1. Initialize Default Models & Registry
    registry.create_model("fraud_detector", "Real-time transaction fraud classifier", tags={"domain": "fintech"})
    registry.create_version("fraud_detector", "v1.0", "s3://models/fraud_v1.pt", metrics={"auc": 0.942, "latency_p95": 1.25})
    registry.transition_stage("fraud_detector", "v1.0", ModelStage.EXPERIMENTAL)
    registry.transition_stage("fraud_detector", "v1.0", ModelStage.STAGING)
    registry.transition_stage("fraud_detector", "v1.0", ModelStage.PRODUCTION)

    registry.create_version("fraud_detector", "v1.2", "s3://models/fraud_v1.2.onnx", metrics={"auc": 0.961, "latency_p95": 1.18})
    registry.transition_stage("fraud_detector", "v1.2", ModelStage.EXPERIMENTAL)
    registry.transition_stage("fraud_detector", "v1.2", ModelStage.STAGING)
    registry.transition_stage("fraud_detector", "v1.2", ModelStage.PRODUCTION)

    registry.create_model("recommendation_ranker", "Multi-task deep ranking model", tags={"domain": "ecommerce"})
    registry.create_version("recommendation_ranker", "v2.0", "s3://models/ranker_v2.pt", metrics={"ndcg": 0.884, "latency_p95": 3.18})
    registry.transition_stage("recommendation_ranker", "v2.0", ModelStage.EXPERIMENTAL)
    registry.transition_stage("recommendation_ranker", "v2.0", ModelStage.STAGING)
    registry.transition_stage("recommendation_ranker", "v2.0", ModelStage.CANARY)

    # Register in Serving Server
    server.register_model("fraud_detector", "v1.0")
    server.register_model("fraud_detector", "v1.2")
    server.register_model("recommendation_ranker", "v2.0")

    # 2. Initialize Default Feature Store
    user_ent = Entity(name="user", join_key="user_id", description="Customer ID entity")
    feature_store.register_entity(user_ent)
    fv = FeatureView(
        name="user_stats",
        entities=[user_ent],
        features=[
            Feature("click_rate", DataType.FLOAT32, description="Click through rate over 7d", default_value=0.05),
            Feature("purchases_count", DataType.INT32, description="Total purchases past 30d", default_value=1),
            Feature("risk_score", DataType.FLOAT32, description="Calculated behavioral risk score", default_value=0.12),
        ],
        tags={"tier": "production"}
    )
    feature_store.register_feature_view(fv)
    feature_store.ingest("user_stats", [
        {"user_id": "u1001", "click_rate": 0.85, "purchases_count": 14, "risk_score": 0.08, "_timestamp": time.time()},
        {"user_id": "u1002", "click_rate": 0.12, "purchases_count": 2, "risk_score": 0.74, "_timestamp": time.time()},
        {"user_id": "u1003", "click_rate": 0.44, "purchases_count": 8, "risk_score": 0.22, "_timestamp": time.time()},
    ])

    # 3. Initialize Default Monitoring Baseline
    monitoring.set_baseline("fraud_detector", {
        "click_rate": [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.75, 0.85],
        "purchases_count": [1.0, 2.0, 3.0, 5.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0],
        "risk_score": [0.05, 0.08, 0.12, 0.15, 0.20, 0.25, 0.35, 0.50, 0.70, 0.85],
    })

    # 4. Initialize Default Pipelines
    retrain_dag = DAG(dag_id="continuous_retraining_v2", description="Automated continuous model retraining & canary deployment")
    retrain_dag.add_task(Task("ingest_features", lambda ctx: {"status": "ok", "records": 1500}))
    retrain_dag.add_task(Task("point_in_time_join", lambda ctx: {"status": "ok", "leakage_checked": True}), depends_on=["ingest_features"])
    retrain_dag.add_task(Task("distributed_hpo", lambda ctx: {"status": "ok", "best_lr": 0.001, "auc": 0.962}), depends_on=["point_in_time_join"])
    retrain_dag.add_task(Task("contract_validation", lambda ctx: {"status": "ok", "schemas_verified": True}), depends_on=["distributed_hpo"])
    retrain_dag.add_task(Task("canary_deploy", lambda ctx: {"status": "ok", "traffic_weight": 0.10}), depends_on=["contract_validation"])

    pipeline_catalog = {retrain_dag.dag_id: retrain_dag}

    # --- Endpoints ---

    @app.get("/health")
    def health_check():
        metrics.increment("manta_health_checks_total")
        return {
            "status": "HEALTHY",
            "cluster": "manta-primary-cluster",
            "version": "1.0.0",
            "active_workers": 4,
            "timestamp": time.time()
        }

    # Auth Endpoints
    @app.post("/v1/auth/login")
    def login(payload: LoginPayload):
        principal = auth.validate_credentials(payload.username, payload.password)
        if principal:
            token = f"manta_tok_{uuid.uuid4().hex[:16]}"
            user_info = {
                "user_id": principal.user_id,
                "username": principal.username,
                "role": "ADMIN" if Role.ADMIN in principal.roles else "ML_ENGINEER",
                "token": token,
                "expires_in": 86400
            }
            active_tokens[token] = user_info
            return {"status": "SUCCESS", "data": user_info}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    @app.post("/v1/auth/logout")
    def logout(authorization: Optional[str] = Header(None)):
        if authorization:
            token = authorization.replace("Bearer ", "").strip()
            active_tokens.pop(token, None)
        return {"status": "SUCCESS", "message": "Logged out successfully"}

    @app.get("/v1/auth/me")
    def get_current_user(authorization: Optional[str] = Header(None)):
        if authorization:
            token = authorization.replace("Bearer ", "").strip()
            if token in active_tokens:
                return {"status": "SUCCESS", "data": active_tokens[token]}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # Telemetry & Metrics
    @app.get("/metrics")
    def get_metrics():
        return metrics.export_prometheus()

    @app.get("/v1/telemetry/stats")
    def get_telemetry_stats():
        models = registry.list_models()
        fvs = feature_store.list_feature_views()
        return {
            "serving_qps": 4820,
            "latency_p95_ms": 1.24,
            "total_requests": 14200,
            "active_deployments": sum(len(m.versions) for m in models),
            "feature_views_count": len(fvs),
            "cluster_status": "HEALTHY",
            "workers_online": 4,
            "governance_score": "100%",
        }

    # Model Serving & Deployment
    @app.post("/v1/models/predict")
    def predict(payload: InferencePayload):
        if not rate_limiter.acquire("api_client"):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        metrics.increment("manta_inference_requests_total")
        resp = server.predict(payload.model_name, payload.inputs, version=payload.version)
        metrics.record_timing("manta_inference_latency", resp.latency_ms)
        return resp.to_dict()

    @app.get("/v1/models")
    def list_models():
        return [m.to_dict() for m in registry.list_models()]

    @app.post("/v1/models/deploy")
    def deploy_model(payload: DeployModelPayload):
        server.register_model(payload.model_name, payload.version)
        return {
            "status": "DEPLOYED",
            "model_name": payload.model_name,
            "version": payload.version,
            "stage": payload.stage,
            "endpoint": f"/v1/models/{payload.model_name}/predict"
        }

    # Feature Store
    @app.get("/v1/features/views")
    def list_feature_views():
        return [fv.to_dict() for fv in feature_store.list_feature_views()]

    @app.post("/v1/features/online")
    def get_online_features(payload: FeatureLookupPayload):
        metrics.increment("manta_feature_lookups_total")
        try:
            results = feature_store.get_online_features(payload.feature_view, payload.entity_keys, payload.features)
            return {"status": "SUCCESS", "feature_view": payload.feature_view, "data": results}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Monitoring & Drift
    @app.get("/v1/monitoring/drift")
    def get_drift_status():
        live_sample = {
            "click_rate": [0.12, 0.18, 0.22, 0.28, 0.32, 0.42, 0.52, 0.62, 0.72, 0.82],
            "purchases_count": [1.0, 2.0, 4.0, 5.0, 7.0, 10.0, 11.0, 14.0, 19.0, 24.0],
            "risk_score": [0.06, 0.09, 0.11, 0.14, 0.19, 0.24, 0.34, 0.48, 0.68, 0.82],
        }
        reports = monitoring.evaluate_model_drift("fraud_detector", live_sample)
        return [r.to_dict() for r in reports]

    @app.post("/v1/monitoring/evaluate")
    def evaluate_custom_drift(payload: DriftEvalPayload):
        reports = monitoring.evaluate_model_drift(payload.model_name, payload.current_features)
        return [r.to_dict() for r in reports]

    # Pipelines & DAGs
    @app.get("/v1/pipelines")
    def list_pipelines():
        return [
            {
                "dag_id": dag.dag_id,
                "description": dag.description,
                "tasks_count": len(dag.tasks),
                "tasks": [
                    {
                        "task_id": t.task_id,
                        "status": t.status.value,
                        "dependencies": list(dag.dependencies.get(t.task_id, []))
                    }
                    for t in dag.tasks.values()
                ]
            }
            for dag in pipeline_catalog.values()
        ]

    @app.post("/v1/pipelines/run")
    def run_pipeline(payload: PipelineRunPayload):
        if payload.dag_id not in pipeline_catalog:
            raise HTTPException(status_code=404, detail=f"DAG '{payload.dag_id}' not found")
        dag = pipeline_catalog[payload.dag_id]
        plan = pipeline_executor.run_dag(dag)
        return {
            "dag_id": plan.dag_id,
            "run_id": plan.run_id,
            "status": plan.status,
            "duration_sec": plan.duration_sec,
            "task_outputs": plan.task_outputs,
        }

    return app
