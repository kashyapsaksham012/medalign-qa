"""Local vLLM backend for the Path B substitute-model run (RA-16 / RA-24 / RA-25).

NOT the paper's model. Runs an open instruction-tuned model on a local GPU (or a
free Kaggle / Colab T4). Every generation is `REPLICATION ASSUMPTION — SUBSTITUTE
MODEL` and is never presented as reproducing PaLM / Flan-PaLM / Med-PaLM.

Reproducibility anchor: the Hugging Face `revision` (a commit SHA) recorded in the
model config. Greedy decoding is deterministic per (revision, GPU architecture,
vLLM version). Sampled decoding (self-consistency / selective prediction) draws
`n` sequences from one seeded generator — distinct samples, reproducible per that
same triple (RA-25). This differs from the hosted-API backend, which needs a
per-decode seed offset because some providers return `n` identical outputs.

`vllm` / `torch` are imported lazily: only the GPU runtime installs them
(requirements-pathb.txt), the Phase 1–8 machine does not.
"""
from __future__ import annotations

import os

from ..utils.io import utcnow
from .base import GenConfig, GenResult


class VLLMBackend:
    def __init__(self, model: str, *, revision: str | None = None,
                 dtype: str = "bfloat16", max_model_len: int = 4096,
                 gpu_memory_utilization: float = 0.90,
                 tensor_parallel_size: int = 1, trust_remote_code: bool = False,
                 quantization: str | None = None, seed: int = 0,
                 hf_token_env: str = "HF_TOKEN"):
        if not revision or revision == "PIN_ME":
            raise RuntimeError(
                "configs/model/*.yaml: `revision` is not pinned. The substitute "
                "model must be frozen to an exact Hugging Face commit SHA before a "
                "run — execute `python scripts/pin_model.py` first."
            )
        from vllm import LLM
        from transformers import AutoTokenizer

        token = os.environ.get(hf_token_env)
        self.model_id = model
        self.revision = revision
        self.name = f"{model}@{revision[:12]}"
        self._tok = AutoTokenizer.from_pretrained(model, revision=revision, token=token)
        self._llm = LLM(
            model=model, revision=revision, dtype=dtype,
            max_model_len=max_model_len,
            gpu_memory_utilization=gpu_memory_utilization,
            tensor_parallel_size=tensor_parallel_size,
            trust_remote_code=trust_remote_code,
            quantization=quantization, seed=seed,
        )
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost_usd = 0.0
        self.n_calls = 0

    # ------------------------------------------------------------------ #
    @classmethod
    def from_config(cls, cfg: dict) -> "VLLMBackend":
        return cls(
            model=cfg["model"],
            revision=cfg.get("revision"),
            dtype=cfg.get("dtype", "bfloat16"),
            max_model_len=int(cfg.get("max_model_len", 4096)),
            gpu_memory_utilization=float(cfg.get("gpu_memory_utilization", 0.90)),
            tensor_parallel_size=int(cfg.get("tensor_parallel_size", 1)),
            trust_remote_code=bool(cfg.get("trust_remote_code", False)),
            quantization=cfg.get("quantization"),
            seed=int(cfg.get("seed", 0)),
        )

    # ------------------------------------------------------------------ #
    def _render(self, prompt: str, cfg: GenConfig) -> str:
        """Apply the model's chat template. The verbatim exemplar block (Tables
        A.13–A.21) is the user message; RA-24 output-format instruction is the
        system message. Content unchanged — only the chat wrapper is added."""
        msgs = []
        if cfg.system:
            msgs.append({"role": "system", "content": cfg.system})
        msgs.append({"role": "user", "content": prompt})
        return self._tok.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=True)

    def _sampling(self, cfg: GenConfig):
        from vllm import SamplingParams
        greedy = cfg.temperature <= 0.0
        return SamplingParams(
            n=1 if greedy else cfg.n,
            temperature=0.0 if greedy else cfg.temperature,
            top_p=1.0 if greedy else cfg.top_p,
            max_tokens=cfg.max_tokens,
            stop=cfg.stop or None,
            seed=cfg.seed,
        )

    # ------------------------------------------------------------------ #
    def generate_batch(self, prompts: list[str], cfg: GenConfig) -> list[GenResult]:
        """One vLLM pass over many prompts — the throughput path used by the runner."""
        rendered = [self._render(p, cfg) for p in prompts]
        outs = self._llm.generate(rendered, self._sampling(cfg))  # order preserved

        results: list[GenResult] = []
        for o in outs:
            texts = [c.text for c in o.outputs]
            if cfg.temperature <= 0.0 and cfg.n > 1:      # greedy asked for n>1 -> replicate
                texts = texts * cfg.n
            p_tok = len(o.prompt_token_ids)
            c_tok = sum(len(c.token_ids) for c in o.outputs)
            self.total_prompt_tokens += p_tok
            self.total_completion_tokens += c_tok
            self.n_calls += len(o.outputs)
            results.append(GenResult(
                texts=texts, prompt_tokens=p_tok, completion_tokens=c_tok,
                cost_usd=0.0, model=self.name, raw_meta={"ts": utcnow()}))
        return results

    def generate(self, prompt: str, cfg: GenConfig) -> GenResult:
        return self.generate_batch([prompt], cfg)[0]

    def usage_summary(self) -> dict:
        return {"model": self.name, "revision": self.revision,
                "n_calls": self.n_calls,
                "prompt_tokens": self.total_prompt_tokens,
                "completion_tokens": self.total_completion_tokens,
                "est_cost_usd": 0.0}
