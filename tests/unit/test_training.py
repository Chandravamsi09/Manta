import pytest
from manta.training.config import TrainingJobConfig, HyperparameterSpace
from manta.training.orchestrator import DistributedTrainingOrchestrator, ParameterServer, WorkerNode
from manta.training.hpo import BayesianOptimizer, HyperbandOptimizer
from manta.training.checkpoint import CheckpointManager
from manta.core.storage import InMemoryStorageBackend

def test_distributed_training_orchestrator():
    config = TrainingJobConfig(
        job_id="job_test_001",
        model_name="classifier_v1",
        num_workers=2,
        epochs=3,
        learning_rate=0.01
    )

    orchestrator = DistributedTrainingOrchestrator()
    result = orchestrator.launch_job(config)

    assert result["status"] == "COMPLETED"
    assert result["epochs_completed"] == 3
    assert len(result["loss_history"]) == 3
    assert result["loss_history"][-1] < result["loss_history"][0]

def test_bayesian_hpo():
    space = HyperparameterSpace()
    space.add_float("learning_rate", 0.0001, 0.1, log_scale=True)
    space.add_int("batch_size", 16, 128)

    def objective(params):
        # Synthetic convex objective: minimize (lr - 0.01)^2
        return (params["learning_rate"] - 0.01) ** 2

    optimizer = BayesianOptimizer(space=space, mode="min")
    res = optimizer.optimize(objective, max_trials=10)

    assert "best_params" in res
    assert "best_score" in res
    assert len(res["history"]) == 10

def test_checkpoint_manager():
    storage = InMemoryStorageBackend()
    manager = CheckpointManager(storage=storage)

    meta = manager.save_checkpoint(
        job_id="job_99",
        epoch=1,
        step=500,
        state_dict={"layer1": [0.1, 0.2]},
        metrics={"val_loss": 0.245}
    )

    assert meta.checkpoint_id == "chk_job_99_e1_s500"
    loaded = manager.load_checkpoint("job_99", meta.checkpoint_id)
    assert loaded["layer1"] == [0.1, 0.2]
