from __future__ import annotations
import uuid
import time
import enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

class RequestPriority(int, enum.Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class InferenceRequest:
    inputs: Dict[str, Any]
    request_id: str = field(default_factory=lambda: f"req_{uuid.uuid4().hex[:10]}")
    model_name: str = "default_model"
    model_version: Optional[str] = None
    priority: RequestPriority = RequestPriority.NORMAL
    timeout_ms: float = 5000.0
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def age_ms(self) -> float:
        return (time.time() - self.created_at) * 1000.0

    @property
    def is_expired(self) -> bool:
        return self.age_ms > self.timeout_ms


@dataclass
class InferenceResponse:
    request_id: str
    outputs: Dict[str, Any]
    latency_ms: float
    model_name: str
    model_version: str
    error: Optional[str] = None
    status_code: int = 200

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "outputs": self.outputs,
            "latency_ms": round(self.latency_ms, 3),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "error": self.error,
            "status_code": self.status_code,
        }
