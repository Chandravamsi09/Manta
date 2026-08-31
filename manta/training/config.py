from __future__ import annotations
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
import datetime
from manta.core.types import DeviceType

@dataclass
class HyperparameterSpace:
    """Search space specification for hyperparameter optimization."""
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def add_float(self, name: str, min_val: float, max_val: float, log_scale: bool = False) -> None:
        self.parameters[name] = {
            "type": "float",
            "min": min_val,
            "max": max_val,
            "log": log_scale,
        }

    def add_int(self, name: str, min_val: int, max_val: int) -> None:
        self.parameters[name] = {
            "type": "int",
            "min": min_val,
            "max": max_val,
        }

    def add_categorical(self, name: str, choices: List[Any]) -> None:
        self.parameters[name] = {
            "type": "categorical",
            "choices": choices,
        }

    def sample_random(self) -> Dict[str, Any]:
        import random
        import math
        sample = {}
        for k, v in self.parameters.items():
            if v["type"] == "float":
                if v.get("log", False):
                    log_min, log_max = math.log(v["min"]), math.log(v["max"])
                    sample[k] = math.exp(random.uniform(log_min, log_max))
                else:
                    sample[k] = random.uniform(v["min"], v["max"])
            elif v["type"] == "int":
                sample[k] = random.randint(v["min"], v["max"])
            elif v["type"] == "categorical":
                sample[k] = random.choice(v["choices"])
        return sample


@dataclass
class TrainingJobConfig:
    """Distributed Training Job Specification."""
    job_id: str
    model_name: str
    num_workers: int = 1
    num_parameter_servers: int = 0
    device: DeviceType = DeviceType.CPU
    batch_size: int = 64
    epochs: int = 10
    learning_rate: float = 1e-3
    optimizer: str = "adam"
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    dataset_uri: str = ""
    output_artifact_dir: str = "./data/models"
    max_retries: int = 3
    early_stopping_patience: int = 5
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
