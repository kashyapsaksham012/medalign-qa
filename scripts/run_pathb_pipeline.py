#!/usr/bin/env python
"""Run Path B phases 10 -> 20 in sequence (real API). Resumable per phase."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

STEPS = [
    ["run.py", "phase10", "--all"],
    ["run.py", "phase11"],
    ["run.py", "phase12"],
    ["run.py", "phase13"],
    ["run.py", "phase14"],           # full 1273 (no --limit)
    ["run.py", "phase15"],
    ["run.py", "phase16"],
    ["run.py", "phase17"],
    ["run.py", "phase18"],
    ["run.py", "phase19"],
    ["run.py", "phase20"],
]


def main() -> int:
    for step in STEPS:
        name = step[1]
        print(f"\n{'='*70}\n>>> {name}  ({time.strftime('%H:%M:%S')})\n{'='*70}", flush=True)
        t0 = time.time()
        r = subprocess.run([PY, *step], cwd=ROOT)
        dt = time.time() - t0
        print(f"<<< {name} exit={r.returncode}  ({dt/60:.1f} min)", flush=True)
        if r.returncode != 0 and name in ("phase10", "phase12", "phase14"):
            # a hard failure in an inference phase -> stop so it can be inspected
            print(f"!!! {name} failed -- stopping pipeline", flush=True)
            return r.returncode
    print("\nPIPELINE COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
