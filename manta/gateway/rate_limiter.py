from __future__ import annotations
import time
import threading
from typing import Dict, Tuple
from manta.core.errors import RateLimitError

class TokenBucketRateLimiter:
    """Sliding window token bucket rate limiter for high-QPS inference endpoints."""
    def __init__(self, rate_limit_per_second: float = 1000.0, burst_capacity: float = 2000.0):
        self.rate = rate_limit_per_second
        self.capacity = burst_capacity
        # { client_id: (tokens, last_refill_timestamp) }
        self._buckets: Dict[str, Tuple[float, float]] = {}
        self._lock = threading.Lock()

    def acquire(self, client_id: str = "default", tokens: float = 1.0) -> bool:
        with self._lock:
            now = time.time()
            if client_id not in self._buckets:
                self._buckets[client_id] = (self.capacity, now)

            current_tokens, last_refill = self._buckets[client_id]
            # Refill tokens
            elapsed = now - last_refill
            refilled = min(self.capacity, current_tokens + elapsed * self.rate)

            if refilled >= tokens:
                self._buckets[client_id] = (refilled - tokens, now)
                return True
            else:
                self._buckets[client_id] = (refilled, now)
                return False
