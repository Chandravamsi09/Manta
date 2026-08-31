from __future__ import annotations
import datetime
from typing import Dict, Any, List, Optional
from manta.registry.model import RegisteredModel, ModelVersion, ModelArtifact
from manta.registry.state_machine import ModelLifecycleStateMachine
from manta.registry.contract import ModelContract
from manta.registry.bom import MLBOMGenerator, MLBillOfMaterials
from manta.registry.lineage import LineageGraph
from manta.core.types import ModelStage
from manta.core.errors import RegistryError
from manta.core.logging import get_logger

logger = get_logger("model_registry")

class ModelRegistry:
    """Central Enterprise Model Registry with lifecycle governance, BOM, and lineage."""
    def __init__(self):
        self._models: Dict[str, RegisteredModel] = {}
        self.state_machine = ModelLifecycleStateMachine()
        self.bom_generator = MLBOMGenerator()
        self.lineage_graph = LineageGraph()
        self._contracts: Dict[str, ModelContract] = {}
        self._boms: Dict[str, MLBillOfMaterials] = {}

    def create_model(self, name: str, description: str = "", tags: Optional[Dict[str, str]] = None) -> RegisteredModel:
        if name in self._models:
            raise RegistryError(f"Model '{name}' already exists in registry")
        m = RegisteredModel(name=name, description=description, tags=tags or {})
        self._models[name] = m
        self.lineage_graph.add_node(f"model_{name}", "MODEL", name)
        logger.info(f"Registered new Model in registry: {name}")
        return m

    def create_version(
        self,
        model_name: str,
        version: str,
        artifact_uri: str,
        checksum: str = "sha256:dummy",
        size_bytes: int = 1024,
        metrics: Optional[Dict[str, float]] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> ModelVersion:
        if model_name not in self._models:
            self.create_model(model_name)
        model = self._models[model_name]

        artifact = ModelArtifact(
            artifact_id=f"art_{model_name}_{version}",
            uri=artifact_uri,
            checksum_sha256=checksum,
            size_bytes=size_bytes
        )

        mv = ModelVersion(
            version=version,
            model_name=model_name,
            stage=ModelStage.DRAFT,
            artifact=artifact,
            metrics=metrics or {},
            hyperparameters=hyperparameters or {},
            tags=tags or {}
        )
        model.versions[version] = mv

        # Generate ML-BOM
        bom = self.bom_generator.generate_bom(model_name, version)
        self._boms[f"{model_name}:{version}"] = bom

        logger.info(f"Registered version {version} for model {model_name}")
        return mv

    def transition_stage(
        self,
        model_name: str,
        version: str,
        target_stage: ModelStage,
        actor: str = "admin",
        comment: str = ""
    ) -> ModelVersion:
        if model_name not in self._models or version not in self._models[model_name].versions:
            raise RegistryError(f"Model version {model_name}:{version} not found")

        mv = self._models[model_name].versions[version]
        self.state_machine.transition(model_name, version, mv.stage, target_stage, actor=actor, comment=comment)
        mv.stage = target_stage
        mv.updated_at = datetime.datetime.utcnow()
        return mv

    def get_model(self, name: str) -> RegisteredModel:
        if name not in self._models:
            raise RegistryError(f"Model '{name}' not found")
        return self._models[name]

    def list_models(self) -> List[RegisteredModel]:
        return list(self._models.values())

# Enterprise Model Lifecycle State Machine & ML-BOM Generator
