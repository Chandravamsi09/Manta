"""Extended verification and unit tests for ML system module #20."""
import pytest
from manta.training.dist_comm_kernel_20 import DistributedCommunicator_20
from manta.training.optimizers_ext_20 import AdvancedOptimizer_20
from manta.serving.paged_kernel_20 import ServingInferenceEngine_20
from manta.monitoring.multivariate_drift_20 import MultiVariateDriftAnalyzer_20
from manta.feature_store.transformations_20 import FeatureWindowAggregator_20
from manta.registry.governance_rules_20 import GovernancePolicyEngine_20
from manta.pipeline.scheduler_kernel_20 import WorkflowTaskScheduler_20
from manta.gateway.qos_router_20 import GatewayQoSScheduler_20
from manta.core.tensor import Tensor

def test_scaled_module_components_20():
    comm = DistributedCommunicator_20(rank=0, world_size=4)
    t = Tensor([1.0, 2.0, 3.0, 4.0])
    red = comm.all_reduce(t, op='SUM')
    assert red.shape.dims == [4]

    opt = AdvancedOptimizer_20(lr=0.01)
    w = opt.step('w1', [0.5, 0.5], [0.1, -0.1])
    assert len(w) == 2

    engine = ServingInferenceEngine_20()
    blocks = engine.allocate_sequence_blocks(seq_id=1, num_tokens=30)
    assert len(blocks) >= 2
    engine.free_sequence(blocks)

    analyzer = MultiVariateDriftAnalyzer_20()
    dist = analyzer.compute_energy_distance([[1.0, 2.0]], [[1.1, 2.1]])
    assert dist >= 0.0

    agg = FeatureWindowAggregator_20(window_seconds=3600)
    res = agg.aggregate_sliding_window([10.0, 20.0], [5.0, 15.0], query_time=25.0)
    assert res['count'] == 2.0
    assert res['mean'] == 10.0

    gov = GovernancePolicyEngine_20()
    ok, _ = gov.evaluate_compliance_rule_1({'metrics': {'accuracy': 0.95}})
    assert ok is True

    sched = WorkflowTaskScheduler_20()
    res_tasks = sched.schedule_tasks_batch(['t1', 't2'])
    assert len(res_tasks) == 2

    qos = GatewayQoSScheduler_20()
    route_res = qos.handle_request_route_tier_1('/v1/predict', {})
    assert route_res['status'] == 200
