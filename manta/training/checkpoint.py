from __future__ import annotations
import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
import datetime
from manta.core.storage import StorageBackend, LocalStorageBackend
from manta.core.logging import get_logger

logger = get_logger("checkpoint_manager")

@dataclass
class CheckpointMetadata:
    checkpoint_id: str
    job_id: str
    epoch: int
    step: int
    metrics: Dict[str, float]
    artifact_hash: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "job_id": self.job_id,
            "epoch": self.epoch,
            "step": self.step,
            "metrics": self.metrics,
            "artifact_hash": self.artifact_hash,
            "created_at": self.created_at.isoformat(),
        }

class CheckpointManager:
    """Sharded state snapshotting and incremental model recovery manager."""
    def __init__(self, storage: Optional[StorageBackend] = None):
        self.storage = storage or LocalStorageBackend("./data/checkpoints")
        self._checkpoints: Dict[str, List[CheckpointMetadata]] = {}

    def save_checkpoint(
        self,
        job_id: str,
        epoch: int,
        step: int,
        state_dict: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> CheckpointMetadata:
        payload = json.dumps(state_dict).encode("utf-8")
        chk_hash = hashlib.sha256(payload).hexdigest()
        chk_id = f"chk_{job_id}_e{epoch}_s{step}"
        
        storage_key = f"{job_id}/{chk_id}.bin"
        self.storage.put(storage_key, payload)

        meta = CheckpointMetadata(
            checkpoint_id=chk_id,
            job_id=job_id,
            epoch=epoch,
            step=step,
            metrics=metrics,
            artifact_hash=chk_hash,
        )

        if job_id not in self._checkpoints:
            self._checkpoints[job_id] = []
        self._checkpoints[job_id].append(meta)

        logger.info(f"Saved checkpoint '{chk_id}' for job '{job_id}' (metrics: {metrics})")
        return meta

    def load_checkpoint(self, job_id: str, checkpoint_id: str) -> Dict[str, Any]:
        storage_key = f"{job_id}/{checkpoint_id}.bin"
        data = self.storage.get(storage_key)
        return json.loads(data.decode("utf-8"))

    def get_latest_checkpoint(self, job_id: str) -> Optional[CheckpointMetadata]:
        history = self._checkpoints.get(job_id, [])
        return history[-1] if history else None
