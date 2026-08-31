import pytest
import manta
from manta.feature_store import Entity, FeatureView, Feature
from manta.core.types import DataType, ModelStage

def test_end_to_end_mlops_lifecycle():
    """
    End-to-End MLOps Pipeline Integration:
    1. Register Features & Ingest Stream Data
    2. Run Distributed Training & Checkpointing
    3. Register Model Version & Transition to Production
    4. Serve Dynamic Inference Batch
    5. Run Continuous Drift Monitoring
    """
    client = manta.Client()

    # Step 1: Feature Ingestion
    ent = Entity("customer", join_key="cust_id")
    fv = FeatureView("cust_v1", entities=[ent], features=[Feature("score", DataType.FLOAT32)])
    client.feature_store.register_feature_view(fv)
    client.feature_store.ingest("cust_v1", [{"cust_id": "c1", "score": 0.95, "_timestamp": 10.0}])
    
    online_features = client.feature_store.get_online_features("cust_v1", ["c1"])
    assert online_features[0]["score"] == 0.95

    # Step 2: Model Registry & Lifecycle
    client.registry.create_model("credit_risk")
    client.registry.create_version("credit_risk", "v1.0", "s3://models/risk.pt", metrics={"auc": 0.91})
    client.registry.transition_stage("credit_risk", "v1.0", ModelStage.EXPERIMENTAL)
    client.registry.transition_stage("credit_risk", "v1.0", ModelStage.STAGING)
    client.registry.transition_stage("credit_risk", "v1.0", ModelStage.PRODUCTION)

    # Step 3: High Performance Serving
    client.inference_server.register_model("credit_risk", "v1.0")
    resp = client.inference_server.predict("credit_risk", {"features": [0.95, 0.12, 0.44, 0.81]})
    assert resp.status_code == 200
    assert "prediction" in resp.outputs

    # Step 4: Monitoring & Drift
    client.monitoring.set_baseline("credit_risk", {"score": [0.9, 0.92, 0.95, 0.91, 0.94]})
    drift_reps = client.monitoring.evaluate_model_drift("credit_risk", {"score": [0.91, 0.93, 0.92, 0.95, 0.94]})
    assert len(drift_reps) == 1
    assert not drift_reps[0].drift_detected
