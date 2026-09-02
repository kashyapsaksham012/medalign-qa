"""Model backends for the substitute-model run (Path B, RA-16).

NOT the paper's models. Every number produced through these backends is labelled
`REPLICATION ASSUMPTION -- SUBSTITUTE MODEL` and is never presented as reproducing
PaLM / Flan-PaLM / Med-PaLM.

The Path B backend is **local vLLM** (`vllm_backend.VLLMBackend`). `openai_compat`
is a legacy hosted-API backend kept only for the quarantined B1 run
(attic/, Groq / qwen3-27b partial); it is not used by the committed pipeline.
"""
from .base import LLM, GenConfig, GenResult
from .mock import MockLLM

__all__ = ["LLM", "GenConfig", "GenResult", "MockLLM", "load_model"]


def load_model(config_path=None, *, mock: bool = False):
    """Factory. `mock=True` returns a MockLLM (no network / no GPU) for tests.

    Dispatch on `provider` in the model config:
      vllm | local  -> VLLMBackend      (Path B backend; local GPU, RA-16/RA-24/RA-25)
      openai_compat -> OpenAICompatLLM   (LEGACY hosted API; B1 only, not the Path B path)
    """
    if mock:
        # Isolation of --mock output under */mock/ is driven by MEDALIGN_RUN_TAG,
        # which run.py / run_pathb_pipeline.py export before the phase runs (so it
        # is set before medalign_qa.utils.paths is imported). Nothing to do here.
        return MockLLM()
    from ..utils import io, paths
    if config_path is None:
        config_path = paths.CONFIGS / "model" / "qwen25-7b-local.yaml"
    cfg = io.read_yaml(config_path)
    provider = str(cfg.get("provider") or "vllm").lower()
    if provider in ("vllm", "local"):
        from .vllm_backend import VLLMBackend
        return VLLMBackend.from_config(cfg)
    from .openai_compat import OpenAICompatLLM  # legacy, lazy-imported
    return OpenAICompatLLM.from_config(cfg)
