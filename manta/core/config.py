from __future__ import annotations
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class SystemSettings(BaseModel):
    app_name: str = "Manta"
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str = "manta-secret-super-key-change-in-prod"
    cluster_name: str = "manta-primary-cluster"
    num_workers: int = 8
    temp_dir: str = "/tmp/manta"

class StorageSettings(BaseModel):
    backend_type: str = "local" # local, s3, gcs, memory
    base_path: str = "./data/manta_storage"
    s3_bucket: Optional[str] = "manta-artifacts"
    s3_endpoint_url: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    compression: str = "snappy"

class FeatureStoreSettings(BaseModel):
    online_backend: str = "memory" # redis, memory, rocksdb
    offline_backend: str = "parquet" # parquet, duckdb, delta
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    offline_storage_path: str = "./data/feature_store"
    cache_ttl_seconds: int = 3600
    sync_interval_seconds: int = 300

class TrainingSettings(BaseModel):
    orchestrator_backend: str = "local" # local, k8s, slurm, ray
    default_device: str = "cpu"
    checkpoint_dir: str = "./data/checkpoints"
    max_concurrent_jobs: int = 4
    enable_elastic_resumption: bool = True
    heartbeat_interval_sec: int = 10
    hpo_default_trials: int = 30

class ServingSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    grpc_port: int = 50051
    workers: int = 4
    dynamic_batching: bool = True
    max_batch_size: int = 64
    max_batch_latency_ms: int = 15
    request_timeout_sec: float = 30.0
    enable_streaming: bool = True
    default_worker_type: str = "native" # native, onnx, torch, triton

class MonitoringSettings(BaseModel):
    drift_eval_interval_minutes: int = 60
    ks_test_p_value_threshold: float = 0.05
    psi_drift_threshold: float = 0.25
    wasserstein_threshold: float = 0.15
    embedding_drift_threshold: float = 0.20
    alert_webhook_url: Optional[str] = None

class MantaConfig(BaseModel):
    system: SystemSettings = Field(default_factory=SystemSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    feature_store: FeatureStoreSettings = Field(default_factory=FeatureStoreSettings)
    training: TrainingSettings = Field(default_factory=TrainingSettings)
    serving: ServingSettings = Field(default_factory=ServingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)

    @classmethod
    def from_yaml(cls, path: str | Path) -> MantaConfig:
        p = Path(path)
        if not p.exists():
            return cls()
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls(**data)

    def to_yaml(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.dict(), f, default_flow_style=False)

_global_config: Optional[MantaConfig] = None

def get_config() -> MantaConfig:
    global _global_config
    if _global_config is None:
        cfg_path = os.environ.get("MANTA_CONFIG_PATH", "manta_config.yaml")
        _global_config = MantaConfig.from_yaml(cfg_path)
    return _global_config

def load_config(path: str | Path) -> MantaConfig:
    global _global_config
    _global_config = MantaConfig.from_yaml(path)
    return _global_config
