#!/usr/bin/env python
"""Task runner (a small `make` replacement for Windows).

Usage:
    python run.py --list
    python run.py <task> [task args...]

Tasks map to scripts/phaseNN_*.py. Each phase script is independently runnable.
"""
from __future__ import annotations

import os
import runpy
import subprocess
import sys
from pathlib import Path

# Force UTF-8 everywhere: child processes (subprocess), file opens without an
# explicit encoding, and this console. Phase scripts/logs contain non-ASCII
# (arrows, +/-, degree) that cp1252 cannot encode.
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Windows consoles default to cp1252; phase scripts/log lines contain non-ASCII
# (arrows, +/-, degree). Force UTF-8 output so a phase can't die with UnicodeEncodeError.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except Exception:  # noqa: BLE001
        pass

ROOT = Path(__file__).resolve().parent
PY = sys.executable

# Phases that require model predictions (Path A/B/C decision -- see docs/STATUS.md).
# They hard-fail with "NO DATA" rather than emit placeholder results.
# Phase 18 (reproducibility validation) is model-independent for the Phase 1-8 pipeline.
_NEEDS_MODEL = {f"phase{n:02d}" for n in (9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20)}

TASKS: dict[str, str] = {
    "phase01": "scripts/phase01_environment.py",
    "phase02": "scripts/phase02_acquire.py",
    "phase03": "scripts/phase03_verify.py",
    "phase04": "scripts/phase04_integrate.py",
    "phase05": "scripts/phase05_cohort.py",
    "phase06": "scripts/phase06_preprocess.py",
    "phase07": "scripts/phase07_features.py",
    "phase08": "scripts/phase08_eda.py",
    "phase09": "scripts/phase09_model.py",
    "phase10": "scripts/phase10_fewshot.py",
    "phase11": "scripts/phase11_cot.py",
    "phase12": "scripts/phase12_self_consistency.py",
    "phase13": "scripts/phase13_scaling.py",
    "phase14": "scripts/phase14_selective_prediction.py",
    "phase15": "scripts/phase15_variance.py",
    "phase16": "scripts/phase16_stats.py",
    "phase17": "scripts/phase17_tables_figures.py",
    "phase18": "scripts/phase18_repro.py",
    "phase19": "scripts/phase19_comparison.py",
    "phase20": "scripts/phase20_docs.py",
    "test": None,  # special: run pytest
}


def _list() -> None:
    print("Available tasks:")
    for name, target in TASKS.items():
        if target is None:
            note = ""
        elif not (ROOT / target).exists():
            note = "  (not yet created)"
        elif name in _NEEDS_MODEL:
            note = "  [needs a FROZEN model — Path decision; NO DATA otherwise]"
        else:
            note = ""
        print(f"  {name:10s} -> {target or 'pytest'}{note}")
    print("\nPhases 01-08 are the model-independent data harness (Milestone 1).")
    print("Phases 09-20 need the Path A/B/C decision in docs/STATUS.md §4.")


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "--list", "list"):
        _list()
        return 0
    task, rest = argv[0], argv[1:]
    if task == "test":
        return subprocess.call([PY, "-m", "pytest", *rest])
    if task not in TASKS or TASKS[task] is None:
        print(f"Unknown task: {task}")
        _list()
        return 2
    script = ROOT / TASKS[task]
    if not script.exists():
        print(f"Task '{task}' script not created yet: {script}")
        return 2
    sys.argv = [str(script), *rest]
    runpy.run_path(str(script), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
