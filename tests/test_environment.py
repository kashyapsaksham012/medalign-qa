"""Phase 1 validation tests."""
from __future__ import annotations

import importlib
import sys

import pytest

REQUIRED_LIBS = ["numpy", "pandas", "scipy", "openpyxl", "lxml", "requests",
                 "matplotlib", "yaml", "tqdm"]


def test_python_version():
    assert sys.version_info >= (3, 11)


@pytest.mark.parametrize("lib", REQUIRED_LIBS)
def test_lib_importable(lib):
    importlib.import_module(lib)


def test_package_imports():
    import medalign_qa
    from medalign_qa.utils import io, logging_utils, paths, seeding  # noqa: F401
    assert medalign_qa.__version__


def test_directory_skeleton():
    from medalign_qa.utils import paths
    paths.ensure_dirs()
    for d in (paths.RAW, paths.PROCESSED, paths.DERIVED, paths.CONFIGS,
              paths.METADATA, paths.PROMPTS, paths.DOCS, paths.RESULTS,
              paths.FIGURES, paths.TABLES, paths.LOGS):
        assert d.is_dir(), d


def test_phase1_files_present():
    from medalign_qa.utils import paths
    for f in (paths.ROOT / "requirements.txt",
              paths.ROOT / "requirements.lock.txt",
              paths.ROOT / "pyproject.toml",
              paths.CONFIGS / "global.yaml",
              paths.METADATA / "dataset_specs.yaml",
              paths.METADATA / "expected_counts.yaml",
              paths.METADATA / "data_provenance.md",
              paths.DOCS / "blockers.md",
              paths.DOCS / "deviations.md",
              paths.DOCS / "replication_plan.md"):
        assert f.is_file(), f


def test_originals_present_and_readonly_intent():
    from medalign_qa.utils import paths
    for key, f in paths.ORIGINALS.items():
        assert f.is_file(), f"missing original: {key} -> {f}"


def test_global_config_loads():
    from medalign_qa.utils import io, paths
    cfg = io.read_yaml(paths.CONFIGS / "global.yaml")
    assert cfg["seed"] == 0
    assert cfg["self_consistency"]["n_chains"] == 11          # PAPER-SPECIFIED
    assert cfg["selective_prediction"]["n_chains"] == 41      # PAPER-SPECIFIED
    assert cfg["instruction_prompt_tuning"]["soft_prompt_length"] == 100  # PAPER-SPECIFIED
    assert cfg["human_eval"]["n_questions"] == 140            # PAPER-SPECIFIED


def test_seeding_reproducible():
    import random

    import numpy as np

    from medalign_qa.utils.seeding import set_seed
    set_seed(0)
    a = (random.random(), float(np.random.rand()))
    set_seed(0)
    b = (random.random(), float(np.random.rand()))
    assert a == b


def test_expected_counts_match_paper_arithmetic():
    from medalign_qa.utils import io, paths
    ec = io.read_yaml(paths.METADATA / "expected_counts.yaml")
    m = ec["medqa_usmle_4opt"]
    assert m["local_train"] + m["local_dev"] == m["paper_dev"] == 11450
    assert m["local_test"] == m["paper_test"] == 1273
