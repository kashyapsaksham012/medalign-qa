"""Inference runner -- resume / no-resume semantics (offline, mock model)."""
from __future__ import annotations

import shutil

import pytest

from medalign_qa import config as run_config
from medalign_qa.inference import runner
from medalign_qa.models import load_model
from medalign_qa.utils import io, paths


@pytest.fixture
def pred_base(monkeypatch):
    # score_file() renders paths relative to paths.ROOT, so the sandbox must live
    # inside the repo tree, not pytest's tmp_path.
    base = paths.DERIVED / "predictions" / "_pytest_runner"
    if base.exists():
        shutil.rmtree(base)
    monkeypatch.setattr(run_config, "predictions_base", lambda tag=None: base)
    yield base
    shutil.rmtree(base, ignore_errors=True)


def _run(*, resume):
    return runner.run_mc_split(
        load_model(mock=True), "medqa_usmle_4opt", "test", "few_shot",
        temperature=0.0, max_tokens=8, limit=20, resume=resume, max_workers=4,
    )


def test_resume_true_skips_existing(pred_base):
    out = pred_base / "few_shot" / "medqa_usmle_4opt__test.jsonl"
    _run(resume=True)
    _run(resume=True)                                   # second pass: all uids present
    assert sum(1 for _ in io.read_jsonl(out)) == 20     # not appended


def test_resume_false_replaces_not_doubles(pred_base):
    """Regression: resume=False + append-mode write used to double the file
    (this is what corrupted the Phase 15 variance runs)."""
    out = pred_base / "few_shot" / "medqa_usmle_4opt__test.jsonl"
    _run(resume=False)
    assert sum(1 for _ in io.read_jsonl(out)) == 20
    _run(resume=False)                                  # re-run from scratch
    uids = [r["uid"] for r in io.read_jsonl(out)]
    assert len(uids) == 20 and len(set(uids)) == 20     # replaced, not 40
