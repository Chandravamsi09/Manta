from __future__ import annotations
import time
import queue
import threading
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from manta.serving.request import InferenceRequest, InferenceResponse, RequestPriority
from manta.serving.worker import ModelWorker
from manta.core.logging import get_logger

logger = get_logger("dynamic_batcher")

@dataclass
class BatcherConfig:
    max_batch_size: int = 32
    max_latency_ms: float = 10.0
    queue_timeout_ms: float = 100.0

class DynamicBatcher:
    """
    Microsecond adaptive dynamic request batcher.
    Aggregates concurrent incoming requests up to max_batch_size or max_latency_ms deadline,
    dispatches vector batch to worker, and fans-out responses back to waiting callers.
    """
    def __init__(self, worker: ModelWorker, config: Optional[BatcherConfig] = None):
        self.worker = worker
        self.config = config or BatcherConfig()
        self._queue: queue.PriorityQueue[Tuple[int, float, InferenceRequest, queue.Queue]] = queue.PriorityQueue()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self.total_requests_served = 0
        self.total_batches_processed = 0

    def start(self) -> None:
        self._running = True
        self._worker_thread = threading.Thread(target=self._batch_loop, daemon=True)
        self._worker_thread.start()
        logger.info(f"DynamicBatcher started for model '{self.worker.model_name}' (batch_size={self.config.max_batch_size})")

    def stop(self) -> None:
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=1.0)

    def submit(self, request: InferenceRequest) -> InferenceResponse:
        response_queue: queue.Queue[InferenceResponse] = queue.Queue()
        # PriorityQueue entry: (-priority, created_at, request, response_q)
        priority_key = -int(request.priority)
        self._queue.put((priority_key, request.created_at, request, response_queue))
        
        # Block until response is ready
        try:
            return response_queue.get(timeout=request.timeout_ms / 1000.0)
        except queue.Empty:
            return InferenceResponse(
                request_id=request.request_id,
                outputs={},
                latency_ms=request.age_ms,
                model_name=self.worker.model_name,
                model_version=self.worker.version,
                error="Request timed out in queue",
                status_code=504,
            )

    def _batch_loop(self) -> None:
        while self._running:
            batch_items: List[Tuple[InferenceRequest, queue.Queue]] = []
            deadline = time.time() + (self.config.max_latency_ms / 1000.0)

            while len(batch_items) < self.config.max_batch_size and time.time() < deadline:
                try:
                    timeout = max(0.001, deadline - time.time())
                    _, _, req, resp_q = self._queue.get(timeout=timeout)
                    if not req.is_expired:
                        batch_items.append((req, resp_q))
                    else:
                        resp_q.put(InferenceResponse(
                            request_id=req.request_id,
                            outputs={},
                            latency_ms=req.age_ms,
                            model_name=self.worker.model_name,
                            model_version=self.worker.version,
                            error="Expired before batch formation",
                            status_code=408
                        ))
                except queue.Empty:
                    break

            if not batch_items:
                time.sleep(0.001)
                continue

            # Process collected batch
            self._execute_batch(batch_items)

    def _execute_batch(self, batch_items: List[Tuple[InferenceRequest, queue.Queue]]) -> None:
        start_t = time.time()
        requests = [item[0] for item in batch_items]
        queues = [item[1] for item in batch_items]

        inputs = [r.inputs for r in requests]
        try:
            outputs = self.worker.predict_batch(inputs)
            latency = (time.time() - start_t) * 1000.0

            for r, q, out in zip(requests, queues, outputs):
                resp = InferenceResponse(
                    request_id=r.request_id,
                    outputs=out,
                    latency_ms=latency,
                    model_name=self.worker.model_name,
                    model_version=self.worker.version,
                )
                q.put(resp)

            self.total_requests_served += len(batch_items)
            self.total_batches_processed += 1
        except Exception as e:
            logger.error(f"Batch execution error: {e}", exc_info=True)
            for r, q in zip(requests, queues):
                q.put(InferenceResponse(
                    request_id=r.request_id,
                    outputs={},
                    latency_ms=(time.time() - start_t) * 1000.0,
                    model_name=self.worker.model_name,
                    model_version=self.worker.version,
                    error=str(e),
                    status_code=500
                ))
