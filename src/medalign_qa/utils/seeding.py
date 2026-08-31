"""Global determinism.

NOT SPECIFIED IN PAPER: the paper reports NO random seed for any experiment
(sampling decodes, soft-prompt init, bootstrap, the 140-question draw).
REPLICATION ASSUMPTION (RA-19): we fix a single project-wide seed (default 0)
for every stochastic step and record it in configs/global.yaml. This makes our
run reproducible; it does NOT recover the authors' exact draws.
"""
from __future__ import annotations

import os
import random

import numpy as np

DEFAULT_SEED = 0


def set_seed(seed: int = DEFAULT_SEED) -> int:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    try:  # only if a torch-based substitute model is ever added
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.use_deterministic_algorithms(True, warn_only=True)
    except Exception:
        pass
    return seed


def rng(seed: int = DEFAULT_SEED) -> np.random.Generator:
    """Explicit Generator for bootstrap / sampling (preferred over global state)."""
    return np.random.default_rng(seed)
