from __future__ import annotations
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import datetime
from manta.core.types import DriftStatus
from manta.core.logging import get_logger

logger = get_logger("statistical_drift")

@dataclass
class DriftReport:
    feature_name: str
    detector: str
    metric_value: float
    p_value: Optional[float]
    threshold: float
    drift_detected: bool
    status: DriftStatus
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "detector": self.detector,
            "metric_value": round(self.metric_value, 4),
            "p_value": round(self.p_value, 4) if self.p_value is not None else None,
            "threshold": self.threshold,
            "drift_detected": self.drift_detected,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


class KolmogorovSmirnovDetector:
    """
    Two-sample Kolmogorov-Smirnov (KS) test for continuous univariate feature distributions.
    Computes the maximum vertical divergence D = sup_x |F_1(x) - F_2(x)| between empirical CDFs.
    """
    def __init__(self, p_value_threshold: float = 0.05):
        self.p_value_threshold = p_value_threshold

    def evaluate(self, reference: List[float], current: List[float], feature_name: str = "feature") -> DriftReport:
        if not reference or not current:
            return DriftReport(feature_name, "KS_Test", 0.0, 1.0, self.p_value_threshold, False, DriftStatus.HEALTHY)

        n1, n2 = len(reference), len(current)
        sorted_ref = sorted(reference)
        sorted_cur = sorted(current)

        # Merge unique values for empirical CDF evaluation
        all_vals = sorted(list(set(sorted_ref + sorted_cur)))
        d_max = 0.0

        i1 = i2 = 0
        for val in all_vals:
            while i1 < n1 and sorted_ref[i1] <= val:
                i1 += 1
            while i2 < n2 and sorted_cur[i2] <= val:
                i2 += 1
            
            cdf1 = i1 / n1
            cdf2 = i2 / n2
            d_max = max(d_max, abs(cdf1 - cdf2))

        # Asymptotic KS p-value approximation
        en = math.sqrt((n1 * n2) / (n1 + n2))
        lambda_val = (en + 0.12 + 0.11 / en) * d_max
        
        # Kolmogorov distribution sum approximation
        p_val = 1.0
        if lambda_val > 0:
            sum_terms = sum(2 * ((-1) ** (k - 1)) * math.exp(-2 * (k ** 2) * (lambda_val ** 2)) for k in range(1, 20))
            p_val = max(0.0, min(1.0, sum_terms))

        drift = p_val < self.p_value_threshold
        status = DriftStatus.DRIFT_DETECTED if drift else DriftStatus.HEALTHY

        return DriftReport(
            feature_name=feature_name,
            detector="KS_Test",
            metric_value=d_max,
            p_value=p_val,
            threshold=self.p_value_threshold,
            drift_detected=drift,
            status=status,
            details={"ks_statistic_d": d_max, "effective_n": en}
        )


class PopulationStabilityIndexDetector:
    """
    Population Stability Index (PSI) detector.
    Measures distributional shift by binning continuous/categorical values:
    PSI = sum((Actual% - Expected%) * ln(Actual% / Expected%))
    """
    def __init__(self, num_bins: int = 10, threshold: float = 0.25):
        self.num_bins = num_bins
        self.threshold = threshold

    def evaluate(self, reference: List[float], current: List[float], feature_name: str = "feature") -> DriftReport:
        if not reference or not current:
            return DriftReport(feature_name, "PSI", 0.0, None, self.threshold, False, DriftStatus.HEALTHY)

        ref_sorted = sorted(reference)
        n_ref = len(ref_sorted)
        n_cur = len(current)

        # Quantile bin edges based on reference
        bin_edges = []
        for i in range(1, self.num_bins):
            idx = int((i / self.num_bins) * n_ref)
            bin_edges.append(ref_sorted[idx])
        bin_edges = sorted(list(set(bin_edges)))

        # Count frequencies
        def get_bin_counts(data: List[float]) -> List[int]:
            counts = [0] * (len(bin_edges) + 1)
            for x in data:
                placed = False
                for b_idx, edge in enumerate(bin_edges):
                    if x <= edge:
                        counts[b_idx] += 1
                        placed = True
                        break
                if not placed:
                    counts[-1] += 1
            return counts

        ref_counts = get_bin_counts(reference)
        cur_counts = get_bin_counts(current)

        psi = 0.0
        for r_c, c_c in zip(ref_counts, cur_counts):
            # Laplace smoothing
            actual_pct = max((c_c / n_cur), 1e-4)
            expected_pct = max((r_c / n_ref), 1e-4)
            psi += (actual_pct - expected_pct) * math.log(actual_pct / expected_pct)

        drift = psi > self.threshold
        if psi > 0.25:
            status = DriftStatus.CRITICAL
        elif psi > 0.1:
            status = DriftStatus.WARNING
        else:
            status = DriftStatus.HEALTHY

        return DriftReport(
            feature_name=feature_name,
            detector="PSI",
            metric_value=psi,
            p_value=None,
            threshold=self.threshold,
            drift_detected=drift,
            status=status,
            details={"bins": len(bin_edges) + 1}
        )


class WassersteinDistanceDetector:
    """
    1D Wasserstein-1 Distance (Earth Mover's Distance).
    W_1(u, v) = integral |U(t) - V(t)| dt
    """
    def __init__(self, threshold: float = 0.15):
        self.threshold = threshold

    def evaluate(self, reference: List[float], current: List[float], feature_name: str = "feature") -> DriftReport:
        if not reference or not current:
            return DriftReport(feature_name, "Wasserstein", 0.0, None, self.threshold, False, DriftStatus.HEALTHY)

        u = sorted(reference)
        v = sorted(current)

        # Merge sorted points
        all_vals = sorted(list(set(u + v)))
        n_u, n_v = len(u), len(v)

        w1 = 0.0
        i_u = i_v = 0

        for k in range(len(all_vals) - 1):
            val = all_vals[k]
            next_val = all_vals[k + 1]
            diff = next_val - val

            while i_u < n_u and u[i_u] <= val:
                i_u += 1
            while i_v < n_v and v[i_v] <= val:
                i_v += 1

            cdf_u = i_u / n_u
            cdf_v = i_v / n_v
            w1 += abs(cdf_u - cdf_v) * diff

        # Normalize by reference interquartile range (IQR)
        q75 = u[int(n_u * 0.75)]
        q25 = u[int(n_u * 0.25)]
        iqr = max(1e-4, q75 - q25)
        normalized_w1 = w1 / iqr

        drift = normalized_w1 > self.threshold
        status = DriftStatus.DRIFT_DETECTED if drift else DriftStatus.HEALTHY

        return DriftReport(
            feature_name=feature_name,
            detector="Wasserstein",
            metric_value=normalized_w1,
            p_value=None,
            threshold=self.threshold,
            drift_detected=drift,
            status=status,
            details={"raw_w1": w1, "iqr": iqr}
        )


class JensenShannonDetector:
    """Jensen-Shannon Divergence detector (symmetric, bounded Kullback-Leibler divergence)."""
    def __init__(self, threshold: float = 0.2):
        self.threshold = threshold

    def evaluate(self, p_dist: List[float], q_dist: List[float], feature_name: str = "feature") -> DriftReport:
        # Normalize probability distributions
        sum_p = max(1e-8, sum(p_dist))
        sum_q = max(1e-8, sum(q_dist))
        p = [x / sum_p for x in p_dist]
        q = [x / sum_q for x in q_dist]

        m = [(a + b) / 2.0 for a, b in zip(p, q)]

        def kl_div(dist1: List[float], dist2: List[float]) -> float:
            kl = 0.0
            for a, b in zip(dist1, dist2):
                if a > 0 and b > 0:
                    kl += a * math.log(a / b)
            return kl

        jsd = 0.5 * kl_div(p, m) + 0.5 * kl_div(q, m)
        js_distance = math.sqrt(max(0.0, jsd))

        drift = js_distance > self.threshold
        status = DriftStatus.DRIFT_DETECTED if drift else DriftStatus.HEALTHY

        return DriftReport(
            feature_name=feature_name,
            detector="Jensen-Shannon",
            metric_value=js_distance,
            p_value=None,
            threshold=self.threshold,
            drift_detected=drift,
            status=status
        )


class ChiSquareDetector:
    """Chi-Square Goodness-of-Fit test for categorical feature distributions."""
    def __init__(self, p_value_threshold: float = 0.05):
        self.p_value_threshold = p_value_threshold

    def evaluate(self, reference: List[str], current: List[str], feature_name: str = "feature") -> DriftReport:
        from collections import Counter
        ref_counts = Counter(reference)
        cur_counts = Counter(current)

        categories = set(list(ref_counts.keys()) + list(cur_counts.keys()))
        n_ref = len(reference)
        n_cur = len(current)

        chi2_stat = 0.0
        for cat in categories:
            observed = cur_counts.get(cat, 0)
            expected = max(1e-4, (ref_counts.get(cat, 0) / max(1, n_ref)) * n_cur)
            chi2_stat += ((observed - expected) ** 2) / expected

        # Approximate p-value
        deg_freedom = max(1, len(categories) - 1)
        p_val = max(0.001, math.exp(-chi2_stat / (2.0 * deg_freedom)))

        drift = p_val < self.p_value_threshold
        status = DriftStatus.DRIFT_DETECTED if drift else DriftStatus.HEALTHY

        return DriftReport(
            feature_name=feature_name,
            detector="Chi-Square",
            metric_value=chi2_stat,
            p_value=p_val,
            threshold=self.p_value_threshold,
            drift_detected=drift,
            status=status
        )
