import pytest
from manta.registry.registry import ModelRegistry
from manta.registry.contract import ModelContract, TensorSpec
from manta.core.types import ModelStage, DataType
from manta.core.errors import RegistryError

def test_model_registry_lifecycle_and_governance():
    registry = ModelRegistry()
    model = registry.create_model("recommendation_engine", description="Deep Ranker")
    
    mv = registry.create_version(
        model_name="recommendation_engine",
        version="v1.0.0",
        artifact_uri="s3://models/ranker/v1.0.0.onnx",
        metrics={"auc": 0.892, "ndcg": 0.741}
    )

    assert mv.stage == ModelStage.DRAFT

    # Transition: DRAFT -> EXPERIMENTAL -> STAGING -> PRODUCTION
    mv = registry.transition_stage("recommendation_engine", "v1.0.0", ModelStage.EXPERIMENTAL)
    assert mv.stage == ModelStage.EXPERIMENTAL

    mv = registry.transition_stage("recommendation_engine", "v1.0.0", ModelStage.STAGING)
    assert mv.stage == ModelStage.STAGING

    mv = registry.transition_stage("recommendation_engine", "v1.0.0", ModelStage.PRODUCTION)
    assert mv.stage == ModelStage.PRODUCTION

    # Disallowed transition should raise error (PRODUCTION -> EXPERIMENTAL directly without STAGING)
    with pytest.raises(RegistryError):
        registry.transition_stage("recommendation_engine", "v1.0.0", ModelStage.EXPERIMENTAL)

def test_ml_bom_generation():
    registry = ModelRegistry()
    registry.create_version("nlp_sentiment", "v1.0", "s3://nlp/model.pt")
    bom = registry._boms.get("nlp_sentiment:v1.0")
    assert bom is not None
    assert len(bom.components) >= 3
    assert bom.security_scans["integrity"] == "VERIFIED"
