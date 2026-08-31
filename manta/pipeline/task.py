from __future__ import annotations
import time
import enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
import datetime
from manta.core.logging import get_logger

logger = get_logger("pipeline_task")

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

@dataclass
class RetryPolicy:
    max_retries: int = 3
    delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0

@dataclass
class TaskContext:
    dag_id: str
    run_id: str
    task_id: str
    upstream_results: Dict[str, Any] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)


class Task:
    """Atomic unit of computation in an ML DAG."""
    def __init__(
        self,
        task_id: str,
        fn: Callable[[TaskContext], Any],
        retry_policy: Optional[RetryPolicy] = None,
        timeout_sec: float = 300.0,
        tags: Optional[Dict[str, str]] = None
    ):
        self.task_id = task_id
        self.fn = fn
        self.retry_policy = retry_policy or RetryPolicy()
        self.timeout_sec = timeout_sec
        self.tags = tags or {}
        self.status = TaskStatus.PENDING
        self.output: Any = None
        self.error: Optional[str] = None
        self.execution_duration_sec: float = 0.0

    def execute(self, ctx: TaskContext) -> Any:
        self.status = TaskStatus.RUNNING
        retries = 0
        delay = self.retry_policy.delay_seconds

        while retries <= self.retry_policy.max_retries:
            start_t = time.time()
            try:
                logger.info(f"Executing Task [{self.task_id}] (attempt {retries + 1})")
                self.output = self.fn(ctx)
                self.status = TaskStatus.SUCCESS
                self.execution_duration_sec = time.time() - start_t
                return self.output
            except Exception as e:
                retries += 1
                logger.warning(f"Task [{self.task_id}] failed: {e}. Retrying in {delay}s...")
                if retries > self.retry_policy.max_retries:
                    self.status = TaskStatus.FAILED
                    self.error = str(e)
                    self.execution_duration_sec = time.time() - start_t
                    raise e
                time.sleep(delay)
                delay *= self.retry_policy.backoff_multiplier
