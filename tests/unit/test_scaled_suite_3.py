"""Extended verification and unit tests for ML system module #3."""
import pytest
from manta.training.dist_comm_kernel_3 import DistributedCommunicator_3
from manta.training.optimizers_ext_3 import AdvancedOptimizer_3
from manta.serving.paged_kernel_3 import ServingInferenceEngine_3
from manta.monitoring.multivariate_drift_3 import MultiVariateDriftAnalyzer_3
from manta.feature_store.transformations_3 import FeatureWindowAggregator_3
from manta.registry.governance_rules_3 import GovernancePolicyEngine_3
from manta.pipeline.scheduler_kernel_3 import WorkflowTaskScheduler_3
from manta.gateway.qos_router_3 import GatewayQoSScheduler_3
from manta.core.tensor import Tensor

def test_scaled_module_components_3():
    comm = DistributedCommunicator_3(rank=0, world_size=4)
    t = Tensor([1.0, 2.0, 3.0, 4.0])
    red = comm.all_reduce(t, op='SUM')
    assert red.shape.dims == [4]

    opt = AdvancedOptimizer_3(lr=0.01)
    w = opt.step('w1', [0.5, 0.5], [0.1, -0.1])
    assert len(w) == 2

    engine = ServingInferenceEngine_3()
    blocks = engine.allocate_sequence_blocks(seq_id=1, num_tokens=30)
    assert len(blocks) >= 2
    engine.free_sequence(blocks)

    analyzer = MultiVariateDriftAnalyzer_3()
    dist = analyzer.compute_energy_distance([[1.0, 2.0]], [[1.1, 2.1]])
    assert dist >= 0.0

    agg = FeatureWindowAggregator_3(window_seconds=3600)
    res = agg.aggregate_sliding_window([10.0, 20.0], [5.0, 15.0], query_time=25.0)
    assert res['count'] == 2.0
    assert res['mean'] == 10.0

    gov = GovernancePolicyEngine_3()
    ok, _ = gov.evaluate_compliance_rule_1({'metrics': {'accuracy': 0.95}})
    assert ok is True

    sched = WorkflowTaskScheduler_3()
    res_tasks = sched.schedule_tasks_batch(['t1', 't2'])
    assert len(res_tasks) == 2

    qos = GatewayQoSScheduler_3()
    route_res = qos.handle_request_route_tier_1('/v1/predict', {})
    assert route_res['status'] == 200
