#!/usr/bin/env python
"""B1 -- minimal MedQA-only replication on Groq free tier (Qwen3.8-27B).

MedQA-4opt: few-shot (full 1273) + CoT (full 1273) + self-consistency (11x on a
fixed 200-question subsample, RA: cost control). Then partial tables + verdict.
~4,750 API calls, ~16 h at ~5 req/min. Resumable per phase.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
CFG = "configs/model/qwen3-27b-groq.yaml"

STEPS = [
    ["run.py", "phase10", "--config", CFG, "--workers", "3"],                       # MedQA-4opt few-shot
    ["run.py", "phase11", "--config", CFG, "--datasets", "medqa_usmle_4opt", "--workers", "3"],
    ["run.py", "phase12", "--config", CFG, "--datasets", "medqa_usmle_4opt", "--limit", "200", "--workers", "3"],
    ["run.py", "phase13"],
    ["run.py", "phase16"],
    ["run.py", "phase17"],
    ["run.py", "phase19"],
    ["run.py", "phase20"],
]


def main() -> int:
    for step in STEPS:
        name = step[1]
        print(f"\n{'='*66}\n>>> {name}  ({time.strftime('%H:%M:%S')})\n{'='*66}", flush=True)
        t0 = time.time()
        r = subprocess.run([PY, *step], cwd=ROOT)
        print(f"<<< {name} exit={r.returncode}  ({(time.time()-t0)/60:.1f} min)", flush=True)
        if r.returncode != 0 and name in ("phase10", "phase11", "phase12"):
            print(f"!!! {name} failed -- stopping", flush=True)
            return r.returncode
    print("\nB1 PIPELINE COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
