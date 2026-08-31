#!/usr/bin/env python
"""Kaggle / Colab bootstrap for the Path B substitute-model run (RA-16).

Meant to be executed from a GPU notebook cell after the repo is present:

    !git clone <repo-url> medalign-qa && cd medalign-qa && \
        python scripts/kaggle_pathb.py --setup        # install deps + pin model
    # (attach processed_data as a Kaggle dataset, or run phase04 with raw_data)
    !cd medalign-qa && python scripts/kaggle_pathb.py --run   # phases 9-20 + package

Steps:
  --setup : pip install requirements-pathb.txt + `-e .`; pin the model revision
  --run   : verify processed_data, run scripts/run_pathb_pipeline.py, then zip
            results/ tables/ figures/ logs/ derived_data/predictions/<run_tag>/
            into ./pathb_artifacts.zip for download.

See docs/pathb_runbook.md for the full click-by-click.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def sh(*cmd: str) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=ROOT).returncode


def setup() -> int:
    if sh(PY, "-m", "pip", "install", "-q", "-r", "requirements-pathb.txt", "-e", "."):
        return 1
    # GPU sanity
    sh(PY, "-c", "import torch; print('CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')")
    # freeze what actually resolved
    with open(ROOT / "requirements-pathb.lock.txt", "w", encoding="utf-8") as fh:
        subprocess.run([PY, "-m", "pip", "freeze"], cwd=ROOT, stdout=fh)
    # pin the model revision (needs internet ON)
    return sh(PY, "scripts/pin_model.py")


def _run_tag() -> str:
    sys.path.insert(0, str(ROOT / "src"))
    from medalign_qa import config as c  # noqa
    return c.run_tag()


def run(full: bool) -> int:
    proc = ROOT / "processed_data"
    have = list(proc.glob("medqa_usmle_*.jsonl"))
    if not have:
        print("processed_data/ has no MedQA files. Either attach a Kaggle dataset "
              "with processed_data/, or run `python run.py phase04` with raw_data/ present.",
              flush=True)
        return 2
    cmd = [PY, "scripts/run_pathb_pipeline.py"] + (["--all"] if full else [])
    rc = subprocess.run(cmd, cwd=ROOT).returncode

    tag = _run_tag()
    out = ROOT / "pathb_artifacts.zip"
    globs = ["results/*", "tables/*", "figures/*", "logs/*",
             f"derived_data/predictions/{tag}/**/*", "docs/reproducibility.md",
             "configs/model/qwen25-7b-local.yaml", "requirements-pathb.lock.txt"]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for g in globs:
            for p in ROOT.glob(g):
                if p.is_file():
                    z.write(p, p.relative_to(ROOT))
    print(f"packaged -> {out}  (pipeline exit {rc})", flush=True)
    return rc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--setup", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--all", action="store_true", help="full MC sweep (default: MedQA-only)")
    args = ap.parse_args()
    if args.setup:
        return setup()
    if args.run:
        return run(args.all)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
