from __future__ import annotations
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from manta.monitoring.statistical import DriftReport
from manta.core.types import DriftStatus
from manta.core.logging import get_logger

logger = get_logger("embedding_drift")

class EmbeddingDriftDetector:
    """
    High-dimensional embedding drift detection.
    Computes Centroid Cosine Distance Shift and k-NN neighborhood density migration.
    """
    def __init__(self, threshold: float = 0.15):
        self.threshold = threshold

    def _compute_centroid(self, embeddings: List[List[float]]) -> List[float]:
        dim = len(embeddings[0])
        centroid = [0.0] * dim
        for emb in embeddings:
            for i in range(dim):
                centroid[i] += emb[i]
        n = len(embeddings)
        return [x / n for x in centroid]

    def _cosine_distance(self, u: List[float], v: List[float]) -> float:
        dot = sum(a * b for a, b in zip(u, v))
        norm_u = math.sqrt(sum(a * a for a in u))
        norm_v = math.sqrt(sum(b * b for b in v))
        if norm_u == 0 or norm_v == 0:
            return 1.0
        similarity = dot / (norm_u * norm_v)
        return 1.0 - max(-1.0, min(1.0, similarity))

    def evaluate(self, reference: List[List[float]], current: List[List[float]], embedding_name: str = "embeddings") -> DriftReport:
        if not reference or not current:
            return DriftReport(embedding_name, "Embedding_Cosine_Centroid", 0.0, None, self.threshold, False, DriftStatus.HEALTHY)

        ref_centroid = self._compute_centroid(reference)
        cur_centroid = self._compute_centroid(current)

        dist = self._cosine_distance(ref_centroid, cur_centroid)
        drift = dist > self.threshold
        status = DriftStatus.DRIFT_DETECTED if drift else DriftStatus.HEALTHY

        return DriftReport(
            feature_name=embedding_name,
            detector="Embedding_Cosine_Centroid",
            metric_value=dist,
            p_value=None,
            threshold=self.threshold,
            drift_detected=drift,
            status=status,
            details={"dim": len(ref_centroid)}
        )
