from __future__ import annotations
import uuid
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import datetime
from manta.pipeline.dag import DAG
from manta.pipeline.task import TaskContext, TaskStatus
from manta.core.logging import get_logger

logger = get_logger("pipeline_executor")

@dataclass
class ExecutionPlan:
    dag_id: str
    run_id: str
    status: str
    task_outputs: Dict[str, Any] = field(default_factory=dict)
    duration_sec: float = 0.0
    start_time: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    end_time: Optional[datetime.datetime] = None

class PipelineExecutor:
    """Executes DAG pipelines with dependency propagation."""
    def run_dag(self, dag: DAG) -> ExecutionPlan:
        dag.validate()
        run_id = f"dag_run_{uuid.uuid4().hex[:8]}"
        plan = ExecutionPlan(dag_id=dag.dag_id, run_id=run_id, status="RUNNING")
        logger.info(f"Starting DAG execution: {dag.dag_id} [{run_id}]")

        order = dag.get_topological_order()
        start_t = time.time()

        for t_id in order:
            task = dag.tasks[t_id]
            upstreams = dag.dependencies[t_id]
            upstream_results = {u: plan.task_outputs.get(u) for u in upstreams}

            ctx = TaskContext(
                dag_id=dag.dag_id,
                run_id=run_id,
                task_id=t_id,
                upstream_results=upstream_results
            )

            try:
                res = task.execute(ctx)
                plan.task_outputs[t_id] = res
            except Exception as e:
                plan.status = "FAILED"
                plan.duration_sec = time.time() - start_t
                plan.end_time = datetime.datetime.utcnow()
                logger.error(f"DAG Run [{run_id}] aborted due to failure in task '{t_id}': {e}")
                return plan

        plan.status = "SUCCESS"
        plan.duration_sec = time.time() - start_t
        plan.end_time = datetime.datetime.utcnow()
        logger.info(f"DAG Run [{run_id}] completed successfully in {plan.duration_sec:.3f}s")
        return plan

# Declarative DAG Pipeline Compiler and Topological Distributed Executor
