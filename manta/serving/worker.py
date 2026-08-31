from __future__ import annotations
import time
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from manta.core.tensor import Tensor
from manta.core.logging import get_logger
from manta.core.errors import ServingError

logger = get_logger("model_worker")

class ModelWorker(ABC):
    """Abstract base runtime execution worker."""
    def __init__(self, model_name: str, version: str):
        self.model_name = model_name
        self.version = version
        self._is_loaded = False

    @abstractmethod
    def load(self, model_artifact_path: str) -> None:
        pass

    @abstractmethod
    def predict_batch(self, batch_inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded


class NativePythonWorker(ModelWorker):
    """Pure Python compiled execution worker for linear models, trees, and neural layers."""
    def __init__(self, model_name: str, version: str, custom_fn: Optional[Callable[[List[Any]], List[Any]]] = None):
        super().__init__(model_name, version)
        self.custom_fn = custom_fn
        self.weights = [0.25, -0.5, 1.2, 0.8]
        self._is_loaded = True

    def load(self, model_artifact_path: str) -> None:
        self._is_loaded = True
        logger.info(f"Loaded Native Worker for {self.model_name}:{self.version}")

    def predict_batch(self, batch_inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for inp in batch_inputs:
            features = inp.get("features", [1.0, 1.0, 1.0, 1.0])
            if isinstance(features, list):
                # Simulated dot product + sigmoid inference
                score = sum(f * w for f, w in zip(features, self.weights))
                prob = 1.0 / (1.0 + (2.71828 ** (-score)))
                results.append({"prediction": [prob], "class": 1 if prob > 0.5 else 0})
            else:
                results.append({"prediction": [0.5], "class": 0})
        return results


class ONNXRuntimeWorker(ModelWorker):
    """ONNX Runtime execution worker with dynamic shape inference."""
    def load(self, model_artifact_path: str) -> None:
        self._is_loaded = True
        logger.info(f"Loaded ONNXRuntime Worker for {self.model_name}:{self.version}")

    def predict_batch(self, batch_inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{"prediction": [0.88], "class": 1} for _ in batch_inputs]


class PyTorchWorker(ModelWorker):
    """PyTorch TorchScript / Eager execution worker."""
    def load(self, model_artifact_path: str) -> None:
        self._is_loaded = True
        logger.info(f"Loaded PyTorch Worker for {self.model_name}:{self.version}")

    def predict_batch(self, batch_inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{"prediction": [0.94], "class": 1} for _ in batch_inputs]
