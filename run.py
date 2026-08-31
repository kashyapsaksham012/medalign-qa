#!/usr/bin/env python
"""Task runner (a small `make` replacement for Windows).

Usage:
    python run.py --list
    python run.py <task> [task args...]

Tasks map to scripts/phaseNN_*.py. Each phase script is independently runnable.
"""
from __future__ import annotations

import runpy
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable

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
        exists = "" if target is None else ("  " if (ROOT / target).exists() else "  (not yet created)")
        print(f"  {name:10s} -> {target or 'pytest'}{exists}")


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
