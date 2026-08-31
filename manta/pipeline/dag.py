from __future__ import annotations
from typing import Dict, Any, List, Set, Optional
from manta.pipeline.task import Task
from manta.core.errors import PipelineError
from manta.core.logging import get_logger

logger = get_logger("pipeline_dag")

class DAG:
    """Declarative Directed Acyclic Graph ML workflow definition."""
    def __init__(self, dag_id: str, description: str = ""):
        self.dag_id = dag_id
        self.description = description
        self.tasks: Dict[str, Task] = {}
        self.dependencies: Dict[str, Set[str]] = {}  # task_id -> set of upstream task_ids

    def add_task(self, task: Task, depends_on: Optional[List[str]] = None) -> DAG:
        self.tasks[task.task_id] = task
        self.dependencies[task.task_id] = set(depends_on or [])
        return self

    def validate(self) -> None:
        # Verify no missing dependencies
        for t_id, upstreams in self.dependencies.items():
            for u in upstreams:
                if u not in self.tasks:
                    raise PipelineError(f"Task '{t_id}' depends on non-existent task '{u}'")

        # Cycle detection via topological sort
        in_degree = {t: len(self.dependencies[t]) for t in self.tasks}
        queue = [t for t, deg in in_degree.items() if deg == 0]
        visited_count = 0

        while queue:
            node = queue.pop(0)
            visited_count += 1
            # Find downstream nodes
            for t_id, upstreams in self.dependencies.items():
                if node in upstreams:
                    in_degree[t_id] -= 1
                    if in_degree[t_id] == 0:
                        queue.append(t_id)

        if visited_count != len(self.tasks):
            raise PipelineError(f"Cycle detected in DAG '{self.dag_id}'")

    def get_topological_order(self) -> List[str]:
        self.validate()
        in_degree = {t: len(self.dependencies[t]) for t in self.tasks}
        queue = [t for t, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for t_id, upstreams in self.dependencies.items():
                if node in upstreams:
                    in_degree[t_id] -= 1
                    if in_degree[t_id] == 0:
                        queue.append(t_id)

        return order


class DAGCompiler:
    """Compiles high-level Python pipeline definitions or YAML configs into executable DAGs."""
    @staticmethod
    def compile_from_dict(spec: Dict[str, Any]) -> DAG:
        dag = DAG(dag_id=spec.get("dag_id", "default_dag"), description=spec.get("description", ""))
        for t_spec in spec.get("tasks", []):
            t_id = t_spec["id"]
            # Default no-op task function
            fn = lambda ctx: f"Task {ctx.task_id} completed"
            task = Task(task_id=t_id, fn=fn)
            dag.add_task(task, depends_on=t_spec.get("depends_on", []))
        dag.validate()
        return dag
