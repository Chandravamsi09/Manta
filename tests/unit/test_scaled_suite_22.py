"""Extended verification and unit tests for ML system module #22."""
import pytest
from manta.training.dist_comm_kernel_22 import DistributedCommunicator_22
from manta.training.optimizers_ext_22 import AdvancedOptimizer_22
from manta.serving.paged_kernel_22 import ServingInferenceEngine_22
from manta.monitoring.multivariate_drift_22 import MultiVariateDriftAnalyzer_22
from manta.feature_store.transformations_22 import FeatureWindowAggregator_22
from manta.registry.governance_rules_22 import GovernancePolicyEngine_22
from manta.pipeline.scheduler_kernel_22 import WorkflowTaskScheduler_22
from manta.gateway.qos_router_22 import GatewayQoSScheduler_22
from manta.core.tensor import Tensor

def test_scaled_module_components_22():
    comm = DistributedCommunicator_22(rank=0, world_size=4)
    t = Tensor([1.0, 2.0, 3.0, 4.0])
    red = comm.all_reduce(t, op='SUM')
    assert red.shape.dims == [4]

    opt = AdvancedOptimizer_22(lr=0.01)
    w = opt.step('w1', [0.5, 0.5], [0.1, -0.1])
    assert len(w) == 2

    engine = ServingInferenceEngine_22()
    blocks = engine.allocate_sequence_blocks(seq_id=1, num_tokens=30)
    assert len(blocks) >= 2
    engine.free_sequence(blocks)

    analyzer = MultiVariateDriftAnalyzer_22()
    dist = analyzer.compute_energy_distance([[1.0, 2.0]], [[1.1, 2.1]])
    assert dist >= 0.0

    agg = FeatureWindowAggregator_22(window_seconds=3600)
    res = agg.aggregate_sliding_window([10.0, 20.0], [5.0, 15.0], query_time=25.0)
    assert res['count'] == 2.0
    assert res['mean'] == 10.0

    gov = GovernancePolicyEngine_22()
    ok, _ = gov.evaluate_compliance_rule_1({'metrics': {'accuracy': 0.95}})
    assert ok is True

    sched = WorkflowTaskScheduler_22()
    res_tasks = sched.schedule_tasks_batch(['t1', 't2'])
    assert len(res_tasks) == 2

    qos = GatewayQoSScheduler_22()
    route_res = qos.handle_request_route_tier_1('/v1/predict', {})
    assert route_res['status'] == 200
