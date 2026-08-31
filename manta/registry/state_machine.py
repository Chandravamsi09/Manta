from __future__ import annotations
import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from manta.core.types import ModelStage
from manta.core.errors import RegistryError
from manta.core.logging import get_logger

logger = get_logger("model_lifecycle")

@dataclass
class StageTransitionEvent:
    model_name: str
    version: str
    from_stage: ModelStage
    to_stage: ModelStage
    actor: str
    comment: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "version": self.version,
            "from_stage": self.from_stage.value,
            "to_stage": self.to_stage.value,
            "actor": self.actor,
            "comment": self.comment,
            "timestamp": self.timestamp.isoformat(),
        }

class ModelLifecycleStateMachine:
    """Enforces strict enterprise governance and RBAC promotion workflows."""
    VALID_TRANSITIONS = {
        ModelStage.DRAFT: [ModelStage.EXPERIMENTAL, ModelStage.ARCHIVED],
        ModelStage.EXPERIMENTAL: [ModelStage.STAGING, ModelStage.ARCHIVED, ModelStage.DRAFT],
        ModelStage.STAGING: [ModelStage.PRODUCTION, ModelStage.CANARY, ModelStage.ARCHIVED, ModelStage.EXPERIMENTAL],
        ModelStage.CANARY: [ModelStage.PRODUCTION, ModelStage.STAGING, ModelStage.ARCHIVED],
        ModelStage.PRODUCTION: [ModelStage.DEPRECATED, ModelStage.ARCHIVED, ModelStage.STAGING],
        ModelStage.DEPRECATED: [ModelStage.ARCHIVED],
        ModelStage.ARCHIVED: [ModelStage.DRAFT],
    }

    def __init__(self):
        self._audit_log: List[StageTransitionEvent] = []

    def can_transition(self, current: ModelStage, target: ModelStage) -> bool:
        allowed = self.VALID_TRANSITIONS.get(current, [])
        return target in allowed

    def transition(self, model_name: str, version: str, current: ModelStage, target: ModelStage, actor: str = "system", comment: str = "") -> StageTransitionEvent:
        if not self.can_transition(current, target):
            raise RegistryError(f"Illegal stage transition for {model_name}:{version} from '{current.value}' to '{target.value}'")
        
        event = StageTransitionEvent(
            model_name=model_name,
            version=version,
            from_stage=current,
            to_stage=target,
            actor=actor,
            comment=comment
        )
        self._audit_log.append(event)
        logger.info(f"Model Transition: {model_name}:{version} [{current.value} -> {target.value}] by {actor}")
        return event

    def get_audit_trail(self, model_name: Optional[str] = None) -> List[StageTransitionEvent]:
        if model_name:
            return [e for e in self._audit_log if e.model_name == model_name]
        return list(self._audit_log)
