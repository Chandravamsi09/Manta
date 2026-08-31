from __future__ import annotations
import json
import time
from typing import Iterator, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class StreamChunk:
    token: str
    index: int
    is_finished: bool = False
    metadata: Optional[Dict[str, Any]] = None

class SSEFormatter:
    """Server-Sent Events (SSE) formatter for token streaming."""
    @staticmethod
    def format_event(data: Dict[str, Any], event: str = "message") -> str:
        return f"event: {event}
data: {json.dumps(data)}

"


class TokenStreamer:
    """Simulated real-time LLM / sequence token streamer with KV-cache chunking."""
    def __init__(self, prompt: str, generated_tokens: Optional[list[str]] = None):
        self.prompt = prompt
        self.tokens = generated_tokens or ["Manta", " provides", " ultra", "-low", " latency", " inference", " for", " modern", " ML", " systems", "."]

    def stream(self) -> Iterator[StreamChunk]:
        for i, tok in enumerate(self.tokens):
            time.sleep(0.01)  # Simulate token generation step
            is_last = (i == len(self.tokens) - 1)
            yield StreamChunk(token=tok, index=i, is_finished=is_last)
