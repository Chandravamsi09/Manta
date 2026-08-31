"""Extended verification and unit tests for ML system module #7."""
import pytest
from manta.training.dist_comm_kernel_7 import DistributedCommunicator_7
from manta.training.optimizers_ext_7 import AdvancedOptimizer_7
from manta.serving.paged_kernel_7 import ServingInferenceEngine_7
from manta.monitoring.multivariate_drift_7 import MultiVariateDriftAnalyzer_7
from manta.feature_store.transformations_7 import FeatureWindowAggregator_7
from manta.registry.governance_rules_7 import GovernancePolicyEngine_7
from manta.pipeline.scheduler_kernel_7 import WorkflowTaskScheduler_7
from manta.gateway.qos_router_7 import GatewayQoSScheduler_7
from manta.core.tensor import Tensor

def test_scaled_module_components_7():
    comm = DistributedCommunicator_7(rank=0, world_size=4)
    t = Tensor([1.0, 2.0, 3.0, 4.0])
    red = comm.all_reduce(t, op='SUM')
    assert red.shape.dims == [4]

    opt = AdvancedOptimizer_7(lr=0.01)
    w = opt.step('w1', [0.5, 0.5], [0.1, -0.1])
    assert len(w) == 2

    engine = ServingInferenceEngine_7()
    blocks = engine.allocate_sequence_blocks(seq_id=1, num_tokens=30)
    assert len(blocks) >= 2
    engine.free_sequence(blocks)

    analyzer = MultiVariateDriftAnalyzer_7()
    dist = analyzer.compute_energy_distance([[1.0, 2.0]], [[1.1, 2.1]])
    assert dist >= 0.0

    agg = FeatureWindowAggregator_7(window_seconds=3600)
    res = agg.aggregate_sliding_window([10.0, 20.0], [5.0, 15.0], query_time=25.0)
    assert res['count'] == 2.0
    assert res['mean'] == 10.0

    gov = GovernancePolicyEngine_7()
    ok, _ = gov.evaluate_compliance_rule_1({'metrics': {'accuracy': 0.95}})
    assert ok is True

    sched = WorkflowTaskScheduler_7()
    res_tasks = sched.schedule_tasks_batch(['t1', 't2'])
    assert len(res_tasks) == 2

    qos = GatewayQoSScheduler_7()
    route_res = qos.handle_request_route_tier_1('/v1/predict', {})
    assert route_res['status'] == 200
