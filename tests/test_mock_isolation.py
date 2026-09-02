"""A --mock run must never touch real outputs -- everything redirects to */mock/."""
from __future__ import annotations

import importlib
import json
import subprocess
import sys

from medalign_qa.utils import paths


def test_paths_redirect_under_mock_env(monkeypatch):
    monkeypatch.setenv("MEDALIGN_RUN_TAG", "mock")
    p = importlib.reload(paths)
    try:
        for root in (p.RESULTS, p.TABLES, p.FIGURES, p.DOCS):
            assert root.name == "mock" and root.parent == p.ROOT / root.parent.name
        assert p.LOGS == p.ROOT / "logs"          # logs are always real
        assert p.PROCESSED == p.ROOT / "processed_data"   # inputs never redirect
    finally:
        monkeypatch.delenv("MEDALIGN_RUN_TAG", raising=False)
        importlib.reload(paths)


def test_config_run_tag_env_overrides_yaml(monkeypatch):
    from medalign_qa import config
    monkeypatch.setenv("MEDALIGN_RUN_TAG", "mock")
    assert config.run_tag() == "mock" and config.is_mock()
    monkeypatch.setenv("MEDALIGN_RUN_TAG", "")
    assert config.run_tag() == ""                 # explicit empty wins over yaml


def test_mock_phase_writes_only_under_mock(tmp_path):
    """End-to-end: `run.py phase12 --mock` leaves the real results/ tables/ alone."""
    root = paths.ROOT
    before = {f: (root / f).stat().st_mtime
              for f in ("results/phase12_mc_results.json", "tables/table7.md",
                        "results/comparison.md")
              if (root / f).exists()}
    r = subprocess.run([sys.executable, "run.py", "phase12", "--mock", "--limit", "4"],
                       cwd=root, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    for f, mt in before.items():
        assert (root / f).stat().st_mtime == mt, f"{f} was modified by a --mock run"
    assert (root / "results" / "mock" / "phase12_mc_results.json").exists()
    d = json.loads((root / "results" / "mock" / "phase12_mc_results.json").read_text())
    assert d["mock"] is True
