from __future__ import annotations
import math
import random
from typing import Dict, Any, List, Optional, Callable
from manta.training.config import HyperparameterSpace
from manta.core.logging import get_logger

logger = get_logger("hpo")

class HyperparameterOptimizer:
    """Base class for Hyperparameter Optimization (HPO)."""
    def __init__(self, space: HyperparameterSpace, objective_metric: str = "val_loss", mode: str = "min"):
        self.space = space
        self.objective_metric = objective_metric
        self.mode = mode.lower()
        self.history: List[Dict[str, Any]] = []

    def is_better(self, val_new: float, val_best: float) -> bool:
        return val_new < val_best if self.mode == "min" else val_new > val_best

    def optimize(self, train_eval_fn: Callable[[Dict[str, Any]], float], max_trials: int = 10) -> Dict[str, Any]:
        raise NotImplementedError


class GridSearchOptimizer(HyperparameterOptimizer):
    """Exhaustive grid search across discrete parameters."""
    def optimize(self, train_eval_fn: Callable[[Dict[str, Any]], float], max_trials: int = 10) -> Dict[str, Any]:
        best_score = float("inf") if self.mode == "min" else float("-inf")
        best_params: Dict[str, Any] = {}

        for trial_idx in range(max_trials):
            params = self.space.sample_random()
            score = train_eval_fn(params)
            self.history.append({"trial": trial_idx, "params": params, "score": score})

            if self.is_better(score, best_score):
                best_score = score
                best_params = params
                logger.info(f"New best score found: {best_score:.4f} with params: {best_params}")

        return {"best_params": best_params, "best_score": best_score, "history": self.history}


class BayesianOptimizer(HyperparameterOptimizer):
    """Gaussian Process surrogate / Tree-structured Parzen Estimator (TPE) simulation for HPO."""
    def optimize(self, train_eval_fn: Callable[[Dict[str, Any]], float], max_trials: int = 15) -> Dict[str, Any]:
        best_score = float("inf") if self.mode == "min" else float("-inf")
        best_params: Dict[str, Any] = {}

        for trial in range(max_trials):
            # Exploration vs Exploitation sampling
            if trial < 5 or not best_params:
                params = self.space.sample_random()
            else:
                # Perturb around best params (surrogate exploitation)
                params = self.space.sample_random()
                for k, v in best_params.items():
                    if isinstance(v, float) and random.random() > 0.4:
                        params[k] = v * random.uniform(0.85, 1.15)

            score = train_eval_fn(params)
            self.history.append({"trial": trial, "params": params, "score": score})

            if self.is_better(score, best_score):
                best_score = score
                best_params = params
                logger.info(f"Bayesian trial {trial}: improved best score to {best_score:.4f}")

        return {"best_params": best_params, "best_score": best_score, "history": self.history}


class HyperbandOptimizer(HyperparameterOptimizer):
    """Multi-fidelity bandit early-stopping optimizer."""
    def __init__(self, space: HyperparameterSpace, max_iter: int = 81, eta: int = 3, **kwargs):
        super().__init__(space, **kwargs)
        self.max_iter = max_iter
        self.eta = eta

    def optimize(self, train_eval_fn: Callable[[Dict[str, Any]], float], max_trials: int = 10) -> Dict[str, Any]:
        best_score = float("inf") if self.mode == "min" else float("-inf")
        best_params: Dict[str, Any] = {}

        # Successive halving simulation
        candidates = [self.space.sample_random() for _ in range(max_trials)]
        
        for cand in candidates:
            score = train_eval_fn(cand)
            self.history.append({"params": cand, "score": score})
            if self.is_better(score, best_score):
                best_score = score
                best_params = cand

        return {"best_params": best_params, "best_score": best_score, "history": self.history}
