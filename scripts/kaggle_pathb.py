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
    # 1. vLLM first, on its own -- it pins an exact torch/CUDA build. Letting it
    #    drive avoids a mismatch with Kaggle's pre-installed torch.
    if sh(PY, "-m", "pip", "install", "-q", "-U", "vllm"):
        print("vllm install failed -- see log above. You can still run few-shot/CoT "
              "with the transformers fallback: set `provider: hf` in the model config.", flush=True)
        return 1
    # 2. the rest (skip deps -- vllm already resolved torch & transformers)
    sh(PY, "-m", "pip", "install", "-q", "huggingface-hub", "accelerate", "sentencepiece", "pyyaml", "tqdm")
    sh(PY, "-m", "pip", "install", "-q", "--no-deps", "-e", ".")
    # 3. GPU + vLLM sanity
    sh(PY, "-c", "import torch,vllm; print('torch', torch.__version__, '| CUDA', torch.cuda.is_available(),"
                 " '|', torch.cuda.device_count(), 'GPU |', 'vllm', vllm.__version__)")
    # 4. freeze what actually resolved
    with open(ROOT / "requirements-pathb.lock.txt", "w", encoding="utf-8") as fh:
        subprocess.run([PY, "-m", "pip", "freeze"], cwd=ROOT, stdout=fh)
    # 5. confirm the model revision is pinned (resolve it if still PIN_ME)
    cfg = (ROOT / "configs" / "model" / "qwen25-7b-local.yaml").read_text(encoding="utf-8")
    if "PIN_ME" in cfg:
        return sh(PY, "scripts/pin_model.py")
    print("model already pinned:", [l for l in cfg.splitlines() if l.startswith("revision:")][0], flush=True)
    return 0


def _run_tag() -> str:
    sys.path.insert(0, str(ROOT / "src"))
    from medalign_qa import config as c  # noqa
    return c.run_tag()


def _stage_data() -> list[Path]:
    """Copy processed_data jsonl from an attached Kaggle dataset into ./processed_data/.
    Looks under /kaggle/input/**  and  ./_data/**  for *.jsonl (or a processed_data/ dir)."""
    import shutil
    proc = ROOT / "processed_data"
    proc.mkdir(exist_ok=True)
    have = list(proc.glob("medqa_usmle_*.jsonl"))
    if have:
        return have
    roots = [Path("/kaggle/input"), ROOT / "_data"]
    for base in roots:
        if not base.exists():
            continue
        for src in list(base.glob("**/processed_data/*.jsonl")) or list(base.glob("**/*.jsonl")):
            if src.name.endswith(".jsonl"):
                shutil.copy2(src, proc / src.name)
    return list(proc.glob("medqa_usmle_*.jsonl"))


def run(full: bool) -> int:
    have = _stage_data()
    if not have:
        print("No MedQA files found. Attach a Kaggle Dataset containing "
              "medqa_usmle_4opt.jsonl + medqa_usmle_5opt.jsonl (this script scans "
              "/kaggle/input/**), or run `python run.py phase04` with raw_data/ present.",
              flush=True)
        return 2
    print("staged:", *(p.name for p in have), flush=True)
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
