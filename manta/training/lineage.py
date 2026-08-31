from __future__ import annotations
import uuid
import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from manta.core.logging import get_logger

logger = get_logger("experiment_tracker")

@dataclass
class TrialRun:
    run_id: str
    experiment_name: str
    parameters: Dict[str, Any]
    metrics: Dict[str, List[float]] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    start_time: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    end_time: Optional[datetime.datetime] = None
    status: str = "RUNNING"

    def log_metric(self, name: str, value: float) -> None:
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

    def finish(self, status: str = "COMPLETED") -> None:
        self.status = status
        self.end_time = datetime.datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "experiment_name": self.experiment_name,
            "parameters": self.parameters,
            "metrics": self.metrics,
            "tags": self.tags,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
        }

class ExperimentTracker:
    """Tracks experiment runs, metrics series, lineage graphs, and parameters."""
    def __init__(self):
        self._runs: Dict[str, TrialRun] = {}

    def start_run(self, experiment_name: str, parameters: Dict[str, Any], tags: Optional[Dict[str, str]] = None) -> TrialRun:
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        run = TrialRun(
            run_id=run_id,
            experiment_name=experiment_name,
            parameters=parameters,
            tags=tags or {}
        )
        self._runs[run_id] = run
        logger.info(f"Started Run [{run_id}] in Experiment '{experiment_name}'")
        return run

    def get_run(self, run_id: str) -> Optional[TrialRun]:
        return self._runs.get(run_id)

    def list_runs(self, experiment_name: Optional[str] = None) -> List[TrialRun]:
        if experiment_name:
            return [r for r in self._runs.values() if r.experiment_name == experiment_name]
        return list(self._runs.values())
