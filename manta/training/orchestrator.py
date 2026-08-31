from __future__ import annotations
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from manta.training.config import TrainingJobConfig
from manta.core.tensor import Tensor
from manta.core.logging import get_logger
from manta.core.errors import TrainingError

logger = get_logger("training_orchestrator")

class ParameterServer:
    """Central parameter synchronization server for distributed asynchronous SGD / AllReduce."""
    def __init__(self, ps_id: str = "ps-0"):
        self.ps_id = ps_id
        self._parameters: Dict[str, Tensor] = {}
        self._lock = threading.Lock()
        self._step = 0

    def init_parameters(self, params: Dict[str, Tensor]) -> None:
        with self._lock:
            self._parameters = {k: Tensor(v.data, shape=v.shape, dtype=v.dtype) for k, v in params.items()}

    def pull(self) -> Dict[str, Tensor]:
        with self._lock:
            return {k: Tensor(v.data, shape=v.shape, dtype=v.dtype) for k, v in self._parameters.items()}

    def push_gradients(self, gradients: Dict[str, Tensor], lr: float = 1e-3) -> None:
        with self._lock:
            for name, grad in gradients.items():
                if name in self._parameters:
                    param = self._parameters[name]
                    # SGD Update: theta = theta - lr * grad
                    updated_data = [p - lr * g for p, g in zip(param.data, grad.data)]
                    self._parameters[name] = Tensor(updated_data, shape=param.shape, dtype=param.dtype)
            self._step += 1


class WorkerNode:
    """Distributed Training Worker computing forward/backward passes and local gradient updates."""
    def __init__(self, worker_id: int, ps: Optional[ParameterServer] = None):
        self.worker_id = worker_id
        self.ps = ps
        self.local_step = 0

    def step(self, batch_data: List[List[float]], lr: float = 1e-3) -> float:
        """Simulates training step: pull params, compute synthetic loss & grad, push to PS."""
        if self.ps:
            params = self.ps.pull()
        
        # Synthetic loss computation for simulation
        loss = max(0.01, 1.0 / (1.0 + self.local_step * 0.05))
        
        if self.ps:
            # Generate simulated gradients
            grads = {}
            for name, p in params.items():
                grad_data = [(x * 0.01) for x in p.data]
                grads[name] = Tensor(grad_data, shape=p.shape, dtype=p.dtype)
            self.ps.push_gradients(grads, lr=lr)

        self.local_step += 1
        return loss


class DistributedTrainingOrchestrator:
    """Coordinates distributed training execution across multiple workers and parameter servers."""
    def __init__(self):
        self._active_jobs: Dict[str, TrainingJobConfig] = {}

    def launch_job(
        self,
        config: TrainingJobConfig,
        train_fn: Optional[Callable[[int, TrainingJobConfig], Dict[str, float]]] = None
    ) -> Dict[str, Any]:
        logger.info(f"Launching distributed training job '{config.job_id}' (workers={config.num_workers}, epochs={config.epochs})")
        self._active_jobs[config.job_id] = config

        ps = ParameterServer("ps-main")
        # Initialize synthetic weight tensor
        ps.init_parameters({"weight": Tensor([0.5, -0.2, 0.1, 0.8], shape=[4])})

        workers = [WorkerNode(i, ps) for i in range(config.num_workers)]
        epoch_losses: List[float] = []

        start_time = time.time()
        for epoch in range(1, config.epochs + 1):
            losses = []
            for w in workers:
                # Simulated batch step
                l = w.step([[1.0, 2.0]], lr=config.learning_rate)
                losses.append(l)
            avg_loss = sum(losses) / len(losses)
            epoch_losses.append(avg_loss)
            logger.info(f"Job [{config.job_id}] Epoch {epoch}/{config.epochs} - Loss: {avg_loss:.4f}")

        duration = time.time() - start_time
        final_params = ps.pull()

        return {
            "job_id": config.job_id,
            "status": "COMPLETED",
            "epochs_completed": config.epochs,
            "final_loss": epoch_losses[-1] if epoch_losses else 0.0,
            "loss_history": epoch_losses,
            "duration_sec": duration,
            "parameters": {k: v.tolist() for k, v in final_params.items()},
        }
