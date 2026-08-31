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
    """Factory. `mock=True` returns a MockLLM (no network) for tests."""
    if mock:
        return MockLLM()
    from ..utils import io, paths
    if config_path is None:
        config_path = paths.CONFIGS / "model" / "llama31-8b-instruct.yaml"
    cfg = io.read_yaml(config_path)
    return OpenAICompatLLM.from_config(cfg)
