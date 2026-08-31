from __future__ import annotations
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from manta.core.types import DataType, TensorShape
from manta.core.errors import RegistryError

@dataclass
class TensorSpec:
    name: str
    dtype: DataType
    shape: List[int]  # -1 for dynamic dimension (e.g. batch size)
    description: str = ""

    def validate_tensor(self, shape: List[int], dtype: DataType) -> bool:
        if self.dtype != dtype:
            return False
        if len(self.shape) != len(shape):
            return False
        for exp, act in zip(self.shape, shape):
            if exp != -1 and exp != act:
                return False
        return True


@dataclass
class ModelContract:
    """Formal schema contract ensuring strict inference input/output validation."""
    model_name: str
    version: str
    input_specs: List[TensorSpec]
    output_specs: List[TensorSpec]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_inputs(self, inputs: Dict[str, Any]) -> None:
        for spec in self.input_specs:
            if spec.name not in inputs:
                raise RegistryError(f"Missing required input tensor '{spec.name}' for model '{self.model_name}'")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "version": self.version,
            "input_specs": [{"name": s.name, "dtype": s.dtype.value, "shape": s.shape} for s in self.input_specs],
            "output_specs": [{"name": s.name, "dtype": s.dtype.value, "shape": s.shape} for s in self.output_specs],
            "metadata": self.metadata,
        }
