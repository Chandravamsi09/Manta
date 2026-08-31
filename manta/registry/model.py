from __future__ import annotations
import uuid
import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from manta.core.types import ModelStage

@dataclass
class ModelArtifact:
    artifact_id: str
    uri: str
    checksum_sha256: str
    size_bytes: int
    format: str = "onnx"  # onnx, pytorch, tensorrt, pickle
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "uri": self.uri,
            "checksum_sha256": self.checksum_sha256,
            "size_bytes": self.size_bytes,
            "format": self.format,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ModelVersion:
    version: str
    model_name: str
    stage: ModelStage = ModelStage.DRAFT
    artifact: Optional[ModelArtifact] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    author: str = "system"
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "model_name": self.model_name,
            "stage": self.stage.value,
            "artifact": self.artifact.to_dict() if self.artifact else None,
            "metrics": self.metrics,
            "hyperparameters": self.hyperparameters,
            "tags": self.tags,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class RegisteredModel:
    name: str
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    versions: Dict[str, ModelVersion] = field(default_factory=dict)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def get_latest_version(self, stage: Optional[ModelStage] = None) -> Optional[ModelVersion]:
        if not self.versions:
            return None
        if stage is None:
            return list(self.versions.values())[-1]
        matching = [v for v in self.versions.values() if v.stage == stage]
        return matching[-1] if matching else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "versions": {k: v.to_dict() for k, v in self.versions.items()},
            "created_at": self.created_at.isoformat(),
        }
