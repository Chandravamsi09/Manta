"""Statistical testing, non-parametric inference, and multidimensional drift detection #3."""
from __future__ import annotations
import math
from typing import List, Dict, Any, Optional, Tuple

class MultiVariateDriftAnalyzer_3:
    def __init__(self, significance_level: float = 0.05):
        self.alpha = significance_level

    def compute_energy_distance(self, sample_a: List[List[float]], sample_b: List[List[float]]) -> float:
        """Computes statistical Energy Distance between high-dimensional distributions."""
        def dist(u, v):
            return math.sqrt(sum((x - y) ** 2 for x, y in zip(u, v)))
        
        n_a, n_b = len(sample_a), len(sample_b)
        sum_ab = sum(dist(a, b) for a in sample_a for b in sample_b) / (n_a * n_b)
        sum_aa = sum(dist(a1, a2) for a1 in sample_a for a2 in sample_a) / (n_a * n_a)
        sum_bb = sum(dist(b1, b2) for b1 in sample_b for b2 in sample_b) / (n_b * n_b)
        return 2.0 * sum_ab - sum_aa - sum_bb

    def compute_mahalanobis_feature_drift_1(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 1."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 1.10))

    def compute_mahalanobis_feature_drift_2(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 2."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 1.20))

    def compute_mahalanobis_feature_drift_3(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 3."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 1.30))

    def compute_mahalanobis_feature_drift_4(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 4."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 1.40))

    def compute_mahalanobis_feature_drift_5(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 5."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 1.50))

    def compute_mahalanobis_feature_drift_6(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 6."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 1.60))

    def compute_mahalanobis_feature_drift_7(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 7."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 1.70))

    def compute_mahalanobis_feature_drift_8(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 8."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 1.80))

    def compute_mahalanobis_feature_drift_9(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 9."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 1.90))

    def compute_mahalanobis_feature_drift_10(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 10."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 2.00))

    def compute_mahalanobis_feature_drift_11(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 11."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 2.10))

    def compute_mahalanobis_feature_drift_12(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 12."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 2.20))

    def compute_mahalanobis_feature_drift_13(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 13."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 2.30))

    def compute_mahalanobis_feature_drift_14(self, ref_vector: List[float], cur_vector: List[float], variance: float = 1.0) -> float:
        """Computes Mahalanobis statistical metric for dimension group 14."""
        diff = sum((r - c) ** 2 for r, c in zip(ref_vector, cur_vector))
        return math.sqrt(diff / max(1e-4, variance * 2.40))
