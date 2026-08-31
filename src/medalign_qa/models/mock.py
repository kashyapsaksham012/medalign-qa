"""Deterministic + stochastic mock model for offline tests (no network, no cost)."""
from __future__ import annotations

import hashlib
import random

from .base import GenConfig, GenResult


class MockLLM:
    name = "mock"

    def __init__(self, accuracy: float = 0.6, seed: int = 0):
        self._acc = accuracy
        self._seed = seed
        self.n_calls = 0

    def _answer_for(self, prompt: str, jitter: int) -> str:
        # deterministic pseudo-answer from the prompt hash; `jitter` varies samples
        h = int(hashlib.sha256((prompt + str(jitter)).encode()).hexdigest(), 16)
        rng = random.Random(h ^ self._seed)
        # infer the option set from the tail of the prompt ("(A) .. (B) .. (C) .. (D) ..")
        import re
        opts = sorted(set(re.findall(r"\(([A-E])\)", prompt.split("Question:")[-1]))) or ["A", "B", "C", "D"]
        letter = opts[0] if rng.random() < self._acc else rng.choice(opts)
        return f"Explanation: mock reasoning.\nAnswer: ({letter})"

    def generate(self, prompt: str, cfg: GenConfig) -> GenResult:
        self.n_calls += cfg.n
        key = (cfg.system or "") + prompt
        texts = [self._answer_for(key, i if cfg.temperature > 0 else 0)
                 for i in range(cfg.n)]
        return GenResult(texts=texts, prompt_tokens=len(prompt.split()),
                         completion_tokens=8 * cfg.n, cost_usd=0.0, model="mock")

    def usage_summary(self) -> dict:
        return {"model": "mock", "n_calls": self.n_calls, "est_cost_usd": 0.0}
