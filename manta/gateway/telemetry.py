from __future__ import annotations
import time
import json
from typing import Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class MetricCounter:
    name: str
    count: int = 0
    labels: Dict[str, str] = field(default_factory=dict)

class MetricsExporter:
    """Prometheus / OpenTelemetry metrics collector."""
    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._histograms: Dict[str, List[float]] = {}

    def increment(self, metric: str, amount: int = 1) -> None:
        self._counters[metric] = self._counters.get(metric, 0) + amount

    def record_timing(self, metric: str, duration_ms: float) -> None:
        if metric not in self._histograms:
            self._histograms[metric] = []
        self._histograms[metric].append(duration_ms)

    def export_prometheus(self) -> str:
        lines = []
        for k, v in self._counters.items():
            lines.append(f"# TYPE {k} counter")
            lines.append(f"{k} {v}")
        for k, vals in self._histograms.items():
            if vals:
                lines.append(f"# TYPE {k}_latency_ms summary")
                lines.append(f"{k}_count {len(vals)}")
                lines.append(f"{k}_sum {sum(vals)}")
                lines.append(f"{k}_avg {sum(vals)/len(vals):.3f}")
        return "
".join(lines)


class TracerProvider:
    """Distributed trace span generator."""
    def start_span(self, name: str) -> Dict[str, Any]:
        return {
            "trace_id": "tr_" + __import__("uuid").uuid4().hex[:16],
            "span_name": name,
            "start_time": time.time(),
        }
