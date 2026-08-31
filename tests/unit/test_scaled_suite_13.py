"""Extended verification and unit tests for ML system module #13."""
import pytest
from manta.training.dist_comm_kernel_13 import DistributedCommunicator_13
from manta.training.optimizers_ext_13 import AdvancedOptimizer_13
from manta.serving.paged_kernel_13 import ServingInferenceEngine_13
from manta.monitoring.multivariate_drift_13 import MultiVariateDriftAnalyzer_13
from manta.feature_store.transformations_13 import FeatureWindowAggregator_13
from manta.registry.governance_rules_13 import GovernancePolicyEngine_13
from manta.pipeline.scheduler_kernel_13 import WorkflowTaskScheduler_13
from manta.gateway.qos_router_13 import GatewayQoSScheduler_13
from manta.core.tensor import Tensor

def test_scaled_module_components_13():
    comm = DistributedCommunicator_13(rank=0, world_size=4)
    t = Tensor([1.0, 2.0, 3.0, 4.0])
    red = comm.all_reduce(t, op='SUM')
    assert red.shape.dims == [4]

    opt = AdvancedOptimizer_13(lr=0.01)
    w = opt.step('w1', [0.5, 0.5], [0.1, -0.1])
    assert len(w) == 2

    engine = ServingInferenceEngine_13()
    blocks = engine.allocate_sequence_blocks(seq_id=1, num_tokens=30)
    assert len(blocks) >= 2
    engine.free_sequence(blocks)

    analyzer = MultiVariateDriftAnalyzer_13()
    dist = analyzer.compute_energy_distance([[1.0, 2.0]], [[1.1, 2.1]])
    assert dist >= 0.0

    agg = FeatureWindowAggregator_13(window_seconds=3600)
    res = agg.aggregate_sliding_window([10.0, 20.0], [5.0, 15.0], query_time=25.0)
    assert res['count'] == 2.0
    assert res['mean'] == 10.0

    gov = GovernancePolicyEngine_13()
    ok, _ = gov.evaluate_compliance_rule_1({'metrics': {'accuracy': 0.95}})
    assert ok is True

    sched = WorkflowTaskScheduler_13()
    res_tasks = sched.schedule_tasks_batch(['t1', 't2'])
    assert len(res_tasks) == 2

    qos = GatewayQoSScheduler_13()
    route_res = qos.handle_request_route_tier_1('/v1/predict', {})
    assert route_res['status'] == 200
