from __future__ import annotations
import uuid
import contextvars
import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class ExecutionContext:
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = "default_tenant"
    user_id: Optional[str] = None
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    start_time: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def set_attr(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def get_attr(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)

    @property
    def elapsed_ms(self) -> float:
        delta = datetime.datetime.utcnow() - self.start_time
        return delta.total_seconds() * 1000.0

_context_var: contextvars.ContextVar[Optional[ExecutionContext]] = contextvars.ContextVar("manta_context", default=None)

def get_current_context() -> ExecutionContext:
    ctx = _context_var.get()
    if ctx is None:
        ctx = ExecutionContext()
        _context_var.set(ctx)
    return ctx

def set_current_context(ctx: ExecutionContext) -> None:
    _context_var.set(ctx)
