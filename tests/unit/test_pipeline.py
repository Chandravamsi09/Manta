import pytest
from manta.pipeline.task import Task, TaskContext
from manta.pipeline.dag import DAG
from manta.pipeline.executor import PipelineExecutor

def test_pipeline_dag_topological_execution():
    dag = DAG("test_etl_pipeline")

    def task1_fn(ctx: TaskContext):
        return {"data": [1, 2, 3]}

    def task2_fn(ctx: TaskContext):
        upstream = ctx.upstream_results["extract"]
        return {"processed": [x * 2 for x in upstream["data"]]}

    def task3_fn(ctx: TaskContext):
        upstream = ctx.upstream_results["transform"]
        return {"sum": sum(upstream["processed"])}

    t1 = Task("extract", task1_fn)
    t2 = Task("transform", task2_fn)
    t3 = Task("load", task3_fn)

    dag.add_task(t1)
    dag.add_task(t2, depends_on=["extract"])
    dag.add_task(t3, depends_on=["transform"])

    executor = PipelineExecutor()
    plan = executor.run_dag(dag)

    assert plan.status == "SUCCESS"
    assert plan.task_outputs["load"] == {"sum": (2 + 4 + 6)}
