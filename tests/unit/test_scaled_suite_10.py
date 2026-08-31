"""Extended verification and unit tests for ML system module #10."""
import pytest
from manta.training.dist_comm_kernel_10 import DistributedCommunicator_10
from manta.training.optimizers_ext_10 import AdvancedOptimizer_10
from manta.serving.paged_kernel_10 import ServingInferenceEngine_10
from manta.monitoring.multivariate_drift_10 import MultiVariateDriftAnalyzer_10
from manta.feature_store.transformations_10 import FeatureWindowAggregator_10
from manta.registry.governance_rules_10 import GovernancePolicyEngine_10
from manta.pipeline.scheduler_kernel_10 import WorkflowTaskScheduler_10
from manta.gateway.qos_router_10 import GatewayQoSScheduler_10
from manta.core.tensor import Tensor

def test_scaled_module_components_10():
    comm = DistributedCommunicator_10(rank=0, world_size=4)
    t = Tensor([1.0, 2.0, 3.0, 4.0])
    red = comm.all_reduce(t, op='SUM')
    assert red.shape.dims == [4]

    opt = AdvancedOptimizer_10(lr=0.01)
    w = opt.step('w1', [0.5, 0.5], [0.1, -0.1])
    assert len(w) == 2

    engine = ServingInferenceEngine_10()
    blocks = engine.allocate_sequence_blocks(seq_id=1, num_tokens=30)
    assert len(blocks) >= 2
    engine.free_sequence(blocks)

    analyzer = MultiVariateDriftAnalyzer_10()
    dist = analyzer.compute_energy_distance([[1.0, 2.0]], [[1.1, 2.1]])
    assert dist >= 0.0

    agg = FeatureWindowAggregator_10(window_seconds=3600)
    res = agg.aggregate_sliding_window([10.0, 20.0], [5.0, 15.0], query_time=25.0)
    assert res['count'] == 2.0
    assert res['mean'] == 10.0

    gov = GovernancePolicyEngine_10()
    ok, _ = gov.evaluate_compliance_rule_1({'metrics': {'accuracy': 0.95}})
    assert ok is True

    sched = WorkflowTaskScheduler_10()
    res_tasks = sched.schedule_tasks_batch(['t1', 't2'])
    assert len(res_tasks) == 2

    qos = GatewayQoSScheduler_10()
    route_res = qos.handle_request_route_tier_1('/v1/predict', {})
    assert route_res['status'] == 200
