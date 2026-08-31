from __future__ import annotations
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import datetime

@dataclass
class QualityReport:
    feature_name: str
    total_count: int
    missing_count: int
    missing_percentage: float
    mean: Optional[float]
    std: Optional[float]
    min_val: Optional[float]
    max_val: Optional[float]
    anomalies_count: int
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "total_count": self.total_count,
            "missing_count": self.missing_count,
            "missing_percentage": round(self.missing_percentage, 2),
            "mean": round(self.mean, 4) if self.mean else None,
            "std": round(self.std, 4) if self.std else None,
            "min_val": self.min_val,
            "max_val": self.max_val,
            "anomalies_count": self.anomalies_count,
            "timestamp": self.timestamp.isoformat(),
        }

class DataQualityProfiler:
    """Generates data quality profiles and missingness metrics."""
    def profile(self, data: List[Any], feature_name: str = "feature") -> QualityReport:
        total = len(data)
        if total == 0:
            return QualityReport(feature_name, 0, 0, 0.0, None, None, None, None, 0)

        none_count = sum(1 for x in data if x is None)
        valid_nums = [x for x in data if isinstance(x, (int, float)) and x is not None]

        mean_v = sum(valid_nums) / len(valid_nums) if valid_nums else None
        std_v = math.sqrt(sum((x - mean_v) ** 2 for x in valid_nums) / len(valid_nums)) if valid_nums and len(valid_nums) > 1 else None
        min_v = min(valid_nums) if valid_nums else None
        max_v = max(valid_nums) if valid_nums else None

        # Z-score outlier count (|z| > 3)
        anomalies = 0
        if mean_v is not None and std_v and std_v > 0:
            anomalies = sum(1 for x in valid_nums if abs(x - mean_v) / std_v > 3.0)

        return QualityReport(
            feature_name=feature_name,
            total_count=total,
            missing_count=none_count,
            missing_percentage=(none_count / total) * 100.0,
            mean=mean_v,
            std=std_v,
            min_val=min_v,
            max_val=max_v,
            anomalies_count=anomalies
        )


class AnomalyDetector:
    """Isolation & Tukey's Fences (IQR) Anomaly Detection."""
    def detect_outliers_iqr(self, values: List[float], k: float = 1.5) -> List[int]:
        if len(values) < 4:
            return []
        sorted_indices = sorted(range(len(values)), key=lambda i: values[i])
        n = len(values)
        q1 = values[sorted_indices[int(n * 0.25)]]
        q3 = values[sorted_indices[int(n * 0.75)]]
        iqr = q3 - q1
        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr

        outliers = [i for i, x in enumerate(values) if x < lower_bound or x > upper_bound]
        return outliers
