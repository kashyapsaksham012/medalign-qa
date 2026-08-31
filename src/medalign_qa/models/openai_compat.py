"""OpenAI-compatible chat-completions backend (OpenRouter / Together / Fireworks / ...).

Design notes:
  * We send the assembled prompt as a single user message; the model continues it.
    This keeps the paper's few-shot / CoT prompt formatting intact.
  * `n > 1` (self-consistency) is done as n INDEPENDENT requests -- many providers
    ignore the `n` body param, and independent requests guarantee real samples.
  * Cost is estimated from usage tokens x the price table in the model config.
"""
from __future__ import annotations

import dataclasses
import threading
import time

import requests

from ..utils.io import utcnow
from .base import GenConfig, GenResult
from .env import get


class OpenAICompatLLM:
    def __init__(self, model: str, base_url: str, api_key: str,
                 price_in_per_m: float = 0.0, price_out_per_m: float = 0.0,
                 timeout: int = 120, max_retries: int = 5,
                 extra_headers: dict | None = None):
        self.name = model
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._key = api_key
        self.price_in = price_in_per_m
        self.price_out = price_out_per_m
        self.timeout = timeout
        self.max_retries = max_retries
        self.extra_headers = extra_headers or {}
        # running totals (for cost tracking across a phase)
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost_usd = 0.0
        self.n_calls = 0
        self._lock = threading.Lock()

    @classmethod
    def from_config(cls, cfg: dict) -> "OpenAICompatLLM":
        return cls(
            model=get(cfg.get("model_env", "MEDALIGN_MODEL_PRIMARY"), cfg.get("model"), required=not cfg.get("model")),
            base_url=get("MEDALIGN_API_BASE", cfg.get("base_url"), required=True),
            api_key=get("MEDALIGN_API_KEY", required=True),
            price_in_per_m=float(cfg.get("price_in_per_m", 0.0)),
            price_out_per_m=float(cfg.get("price_out_per_m", 0.0)),
            timeout=int(cfg.get("timeout", 120)),
            max_retries=int(cfg.get("max_retries", 5)),
            extra_headers=cfg.get("extra_headers") or {},
        )

    # ------------------------------------------------------------------ #
    def _one_call(self, prompt: str, cfg: GenConfig) -> tuple[str, int, int]:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self._key}",
                   "Content-Type": "application/json", **self.extra_headers}
        messages = []
        if cfg.system:
            messages.append({"role": "system", "content": cfg.system})
        messages.append({"role": "user", "content": prompt})
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": cfg.temperature,
            "top_p": cfg.top_p,
            "max_tokens": cfg.max_tokens,
        }
        if cfg.stop:
            body["stop"] = cfg.stop
        if cfg.seed is not None:
            body["seed"] = cfg.seed

        last_err = None
        for attempt in range(self.max_retries):
            try:
                r = requests.post(url, headers=headers, json=body, timeout=self.timeout)
                if r.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(f"{r.status_code}: {r.text[:200]}")
                r.raise_for_status()
                j = r.json()
                text = j["choices"][0]["message"]["content"] or ""
                usage = j.get("usage", {}) or {}
                return (text, int(usage.get("prompt_tokens", 0)),
                        int(usage.get("completion_tokens", 0)))
            except Exception as e:  # noqa: BLE001
                last_err = e
                if attempt == self.max_retries - 1:
                    break
                time.sleep(min(2 ** attempt, 30))
        raise RuntimeError(f"API call failed after {self.max_retries} retries: {last_err}")

    def generate(self, prompt: str, cfg: GenConfig) -> GenResult:
        texts, p_tok, c_tok = [], 0, 0
        for i in range(cfg.n):
            # self-consistency: each of the n decodes must be an INDEPENDENT sample.
            # If a fixed seed is supplied, offset it per decode -- otherwise providers
            # that honour `seed` return n identical outputs and SC collapses to 1 sample.
            call_cfg = cfg if (cfg.seed is None or cfg.n == 1) \
                else dataclasses.replace(cfg, seed=cfg.seed + i)
            t, pt, ct = self._one_call(prompt, call_cfg)
            texts.append(t)
            p_tok += pt
            c_tok += ct
        cost = (p_tok / 1e6) * self.price_in + (c_tok / 1e6) * self.price_out
        with self._lock:
            self.total_prompt_tokens += p_tok
            self.total_completion_tokens += c_tok
            self.total_cost_usd += cost
            self.n_calls += cfg.n
        return GenResult(texts=texts, prompt_tokens=p_tok, completion_tokens=c_tok,
                         cost_usd=cost, model=self.model,
                         raw_meta={"ts": utcnow()})

    def usage_summary(self) -> dict:
        return {"model": self.model, "n_calls": self.n_calls,
                "prompt_tokens": self.total_prompt_tokens,
                "completion_tokens": self.total_completion_tokens,
                "est_cost_usd": round(self.total_cost_usd, 4)}
