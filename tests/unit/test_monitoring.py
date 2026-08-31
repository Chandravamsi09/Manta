import pytest
from manta.monitoring.statistical import (
    KolmogorovSmirnovDetector,
    PopulationStabilityIndexDetector,
    WassersteinDistanceDetector,
    JensenShannonDetector,
    ChiSquareDetector,
)
from manta.monitoring.embedding import EmbeddingDriftDetector
from manta.core.types import DriftStatus

def test_kolmogorov_smirnov_no_drift():
    detector = KolmogorovSmirnovDetector(p_value_threshold=0.01)
    baseline = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    current = [1.1, 2.0, 2.9, 4.2, 5.0, 6.1, 7.0, 8.1, 8.9, 10.2]
    
    report = detector.evaluate(baseline, current, feature_name="sensor_val")
    assert not report.drift_detected
    assert report.status == DriftStatus.HEALTHY

def test_kolmogorov_smirnov_with_drift():
    detector = KolmogorovSmirnovDetector(p_value_threshold=0.05)
    baseline = [1.0, 2.0, 3.0, 4.0, 5.0]
    current = [100.0, 105.0, 110.0, 120.0, 130.0]  # extreme shift
    
    report = detector.evaluate(baseline, current, feature_name="sensor_val")
    assert report.drift_detected
    assert report.metric_value > 0.8

def test_psi_and_wasserstein_drift():
    psi_det = PopulationStabilityIndexDetector(threshold=0.25)
    w_det = WassersteinDistanceDetector(threshold=0.15)

    ref = [1.0] * 50 + [2.0] * 50
    cur = [1.0] * 48 + [2.0] * 52
    rep_psi = psi_det.evaluate(ref, cur)
    assert not rep_psi.drift_detected

    rep_w = w_det.evaluate(ref, cur)
    assert not rep_w.drift_detected

def test_embedding_drift():
    detector = EmbeddingDriftDetector(threshold=0.10)
    ref_embeddings = [[1.0, 0.0], [0.9, 0.1], [0.8, 0.2]]
    cur_embeddings = [[0.0, 1.0], [0.1, 0.9], [0.2, 0.8]]  # 90-degree orthogonal shift

    rep = detector.evaluate(ref_embeddings, cur_embeddings, "query_embedding")
    assert rep.drift_detected
    assert rep.metric_value > 0.5
