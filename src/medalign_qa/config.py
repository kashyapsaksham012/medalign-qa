"""Active-run configuration: which substitute model this run reads/writes.

Path B (RA-16) evaluates a substitute open model. `run_tag` (from
`configs/global.yaml`) namespaces the prediction tree

    derived_data/predictions/<run_tag>/<strategy>/<dataset>__<split>.jsonl

so one model's decodes are never appended to another's. In particular the
quarantined B1 run (Groq / qwen3.8-27b, partial 95/1273 few-shot) lives at the
legacy flat path `derived_data/predictions/few_shot/...` and stays isolated from
any fresh run with a non-empty `run_tag`.
"""
from __future__ import annotations

import os
from pathlib import Path

from .utils import io, paths

# A mock run sets this (see models.load_model) so its predictions land under
# derived_data/predictions/mock/ and can never overwrite a real run's decodes.
_RUN_TAG_ENV = "MEDALIGN_RUN_TAG"


def run_tag() -> str:
    """Active run tag. `MEDALIGN_RUN_TAG` (set by a --mock run) wins over
    `configs/global.yaml`; either may be empty (legacy flat layout)."""
    env = os.environ.get(_RUN_TAG_ENV)
    if env is not None:
        return env.strip().strip("/")
    g = io.read_yaml(paths.CONFIGS / "global.yaml") or {}
    return str(g.get("run_tag") or "").strip().strip("/")


def predictions_base(tag: str | None = None) -> Path:
    tag = run_tag() if tag is None else tag
    base = paths.DERIVED / "predictions"
    return base / tag if tag else base


def predictions_dir(strategy: str, tag: str | None = None) -> Path:
    """`derived_data/predictions/[<tag>/]<strategy>/`."""
    return predictions_base(tag) / strategy


def prediction_file(strategy: str, stem: str, tag: str | None = None) -> Path:
    """`.../<strategy>/<stem>.jsonl` where stem is `<dataset>__<split>`."""
    return predictions_dir(strategy, tag) / f"{stem}.jsonl"


def is_mock() -> bool:
    return run_tag() == "mock"


def substitute_label() -> str:
    """Short human label for figures/tables. Never claims to be the paper's model."""
    t = run_tag()
    return f"{t or 'substitute model'} (this replication — RA-16)"
