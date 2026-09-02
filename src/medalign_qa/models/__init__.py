"""Model backends for the substitute-model run (Path B, RA-16).

NOT the paper's models. Every number produced through these backends is labelled
`REPLICATION ASSUMPTION -- SUBSTITUTE MODEL` and is never presented as reproducing
PaLM / Flan-PaLM / Med-PaLM.
"""
from .base import LLM, GenConfig, GenResult
from .mock import MockLLM
from .openai_compat import OpenAICompatLLM

__all__ = ["LLM", "GenConfig", "GenResult", "MockLLM", "OpenAICompatLLM", "load_model"]


def load_model(config_path=None, *, mock: bool = False):
    """Factory. `mock=True` returns a MockLLM (no network / no GPU) for tests.

    Dispatch on `provider` in the model config:
      vllm | local     -> VLLMBackend    (Path B default; local GPU, RA-16/RA-24/RA-25)
      anything else     -> OpenAICompatLLM (hosted OpenAI-compatible API; legacy)
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
    provider = str(cfg.get("provider") or "openai_compat").lower()
    if provider in ("vllm", "local"):
        from .vllm_backend import VLLMBackend
        return VLLMBackend.from_config(cfg)
    return OpenAICompatLLM.from_config(cfg)
