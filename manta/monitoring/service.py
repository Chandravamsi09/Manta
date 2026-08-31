from __future__ import annotations
from typing import List, Dict, Any, Optional
from manta.monitoring.statistical import KolmogorovSmirnovDetector, PopulationStabilityIndexDetector, WassersteinDistanceDetector, DriftReport
from manta.monitoring.embedding import EmbeddingDriftDetector
from manta.monitoring.quality import DataQualityProfiler, QualityReport
from manta.monitoring.alerting import AlertManager, RetrainingTrigger
from manta.core.logging import get_logger

logger = get_logger("monitoring_service")

class ModelMonitoringService:
    """Unified monitoring service tracking production models, features, and drift metrics."""
    def __init__(self):
        self.ks_detector = KolmogorovSmirnovDetector()
        self.psi_detector = PopulationStabilityIndexDetector()
        self.wasserstein_detector = WassersteinDistanceDetector()
        self.embedding_detector = EmbeddingDriftDetector()
        self.quality_profiler = DataQualityProfiler()
        self.alert_manager = AlertManager()
        self.retraining_trigger = RetrainingTrigger()

        self._baseline_data: Dict[str, Dict[str, List[float]]] = {}

    def set_baseline(self, model_name: str, baseline_features: Dict[str, List[float]]) -> None:
        self._baseline_data[model_name] = baseline_features
        logger.info(f"Set baseline for model '{model_name}' ({len(baseline_features)} features)")

    def evaluate_model_drift(self, model_name: str, current_features: Dict[str, List[float]]) -> List[DriftReport]:
        baselines = self._baseline_data.get(model_name, {})
        reports: List[DriftReport] = []

        for feat_name, cur_vals in current_features.items():
            if feat_name in baselines:
                ref_vals = baselines[feat_name]
                rep = self.ks_detector.evaluate(ref_vals, cur_vals, feature_name=feat_name)
                reports.append(rep)
                self.alert_manager.dispatch(rep)

        drifted_count = sum(1 for r in reports if r.drift_detected)
        if drifted_count > 0:
            self.retraining_trigger.trigger_retraining(model_name, f"{drifted_count} features drifted")

        return reports
