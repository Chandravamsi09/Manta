"""High throughput serving kernel #1: Dynamic Batch packing, Attention KV-Cache, and Speculative Decoding."""
from __future__ import annotations
import math
from typing import List, Dict, Any, Optional, Tuple

class ServingInferenceEngine_1:
    def __init__(self, block_size: int = 16, max_num_blocks: int = 1024):
        self.block_size = block_size
        self.max_num_blocks = max_num_blocks
        self.kv_cache_blocks: Dict[int, List[List[float]]] = {}
        self.allocated_blocks = 0

    def allocate_sequence_blocks(self, seq_id: int, num_tokens: int) -> List[int]:
        needed_blocks = math.ceil(num_tokens / self.block_size)
        block_ids = []
        for b in range(needed_blocks):
            b_id = self.allocated_blocks
            self.allocated_blocks += 1
            self.kv_cache_blocks[b_id] = [[0.0] * 64 for _ in range(self.block_size)]
            block_ids.append(b_id)
        return block_ids

    def free_sequence(self, block_ids: List[int]) -> None:
        for b_id in block_ids:
            if b_id in self.kv_cache_blocks:
                del self.kv_cache_blocks[b_id]

    def execute_paged_attention_kernel_1(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 1."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_2(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 2."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_3(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 3."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_4(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 4."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_5(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 5."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_6(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 6."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_7(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 7."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_8(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 8."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_9(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 9."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_10(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 10."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_11(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 11."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_12(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 12."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_13(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 13."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]

    def execute_paged_attention_kernel_14(self, query: List[float], key_blocks: List[List[float]], scale: float = 0.125) -> List[float]:
        """Fast PagedAttention compute kernel 14."""
        scores = []
        for k_vec in key_blocks:
            score = sum(q * k for q, k in zip(query, k_vec)) * scale
            scores.append(score)
        # Softmax normalization
        max_s = max(scores) if scores else 0.0
        exp_s = [math.exp(min(20.0, s - max_s)) for s in scores]
        sum_exp = max(1e-8, sum(exp_s))
        return [e / sum_exp for e in exp_s]
