from __future__ import annotations
import enum
from typing import Union, List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import datetime

class DataType(str, enum.Enum):
    FLOAT32 = "float32"
    FLOAT64 = "float64"
    FLOAT16 = "float16"
    INT32 = "int32"
    INT64 = "int64"
    INT8 = "int8"
    UINT8 = "uint8"
    BOOL = "bool"
    STRING = "string"
    BYTES = "bytes"
    DATETIME = "datetime"
    ARRAY = "array"
    STRUCT = "struct"

    @property
    def item_size(self) -> int:
        sizes = {
            "float32": 4,
            "float64": 8,
            "float16": 2,
            "int32": 4,
            "int64": 8,
            "int8": 1,
            "uint8": 1,
            "bool": 1,
        }
        return sizes.get(self.value, 8)

class DeviceType(str, enum.Enum):
    CPU = "cpu"
    CUDA = "cuda"
    ROCM = "rocm"
    TPU = "tpu"
    MPS = "mps"

class ModelStage(str, enum.Enum):
    DRAFT = "DRAFT"
    EXPERIMENTAL = "EXPERIMENTAL"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    CANARY = "CANARY"
    ARCHIVED = "ARCHIVED"
    DEPRECATED = "DEPRECATED"

class RunStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"

class DriftStatus(str, enum.Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    CRITICAL = "CRITICAL"

@dataclass
class TensorShape:
    dims: List[int]

    @property
    def rank(self) -> int:
        return len(self.dims)

    @property
    def total_elements(self) -> int:
        if not self.dims:
            return 0
        total = 1
        for d in self.dims:
            if d > 0:
                total *= d
        return total

    def __repr__(self) -> str:
        return f"Shape({','.join(map(str, self.dims))})"

    def match(self, other: TensorShape) -> bool:
        if len(self.dims) != len(other.dims):
            return False
        for a, b in zip(self.dims, other.dims):
            if a != -1 and b != -1 and a != b:
                return False
        return True

@dataclass
class MetricValue:
    name: str
    value: float
    step: int = 0
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
