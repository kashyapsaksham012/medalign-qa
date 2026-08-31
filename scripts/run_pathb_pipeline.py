#!/usr/bin/env python
"""Path B pipeline -- substitute model (RA-16), MedQA-only first pass (RA-27).

Runs the local vLLM model (configs/model/qwen25-7b-local.yaml, frozen revision)
through phases 9 -> 20. Resumable per phase (prediction JSONLs are append/skip).
Second pass (MedMCQA / PubMedQA / MMLU) = re-run with --all once this is proven.

    python scripts/run_pathb_pipeline.py            # MedQA-only
    python scripts/run_pathb_pipeline.py --all      # full MC sweep
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

MEDQA = ["--datasets", "medqa_usmle_4opt"]


def steps(full: bool, mock: bool) -> list[list[str]]:
    ds = [] if full else MEDQA                       # phase 11/12 dataset filter
    m = ["--mock"] if mock else []
    lim = ["--limit", "24"] if mock else []          # keep the offline check quick
    sp_limit = ["--limit", "40" if mock else "500"]  # selective prediction subset (RA-26)
    return [
        ["run.py", "phase09"] + m,                                # smoke (5 MedQA Q)
        ["run.py", "phase10"] + (["--all"] if full else []) + m + lim,   # few-shot
        ["run.py", "phase11"] + ds + m + lim,                     # CoT
        ["run.py", "phase12"] + ds + m + lim,                     # self-consistency (n=11)
        ["run.py", "phase13"],                                    # scaling verdict (single model)
        ["run.py", "phase14"] + sp_limit + m,                     # selective prediction subset (RA-26)
        ["run.py", "phase15"] + m + lim,                          # repeated-eval variance (A.2)
        ["run.py", "phase16"],                                    # Wilson CIs / McNemar (beyond paper)
        ["run.py", "phase17"],                                    # tables + figures
        ["run.py", "phase18"],                                    # reproducibility checks
        ["run.py", "phase19"],                                    # paper-vs-ours comparison
        ["run.py", "phase20"],                                    # final docs
    ]


HARD = {"phase09", "phase10", "phase11", "phase12", "phase14"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="full MC sweep, not MedQA-only")
    ap.add_argument("--mock", action="store_true", help="offline plumbing check (no GPU)")
    args = ap.parse_args()
    for step in steps(args.all, args.mock):
        name = step[1]
        print(f"\n{'='*70}\n>>> {name}  ({time.strftime('%H:%M:%S')})\n{'='*70}", flush=True)
        t0 = time.time()
        r = subprocess.run([PY, *step], cwd=ROOT)
        print(f"<<< {name} exit={r.returncode}  ({(time.time()-t0)/60:.1f} min)", flush=True)
        if r.returncode != 0 and name in HARD:
            print(f"!!! {name} failed -- stopping pipeline for inspection", flush=True)
            return r.returncode
    print("\nPATH B PIPELINE COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
