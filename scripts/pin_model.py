#!/usr/bin/env python
"""Freeze the Path B substitute model to an exact Hugging Face commit SHA (RA-16).

Resolves the current commit of the model's `main` branch (or --revision <ref>) and
writes it into the `revision:` line of configs/model/qwen25-7b-local.yaml, replacing
the `PIN_ME` placeholder. Run this once, on a machine with internet, then commit the
config. The SHA is the reproducibility anchor -- the paper's weights were never
released, so "same model" means "same revision".

    python scripts/pin_model.py                     # pin Qwen2.5-7B-Instruct @ main
    python scripts/pin_model.py --config configs/model/other.yaml --revision main
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CFG = ROOT / "configs" / "model" / "qwen25-7b-local.yaml"


def resolve_sha(model_id: str, revision: str) -> str:
    try:
        from huggingface_hub import HfApi
    except ImportError:
        sys.exit("huggingface_hub not installed. `pip install huggingface-hub` "
                 "(it is in requirements-pathb.txt).")
    info = HfApi().model_info(model_id, revision=revision)
    sha = getattr(info, "sha", None)
    if not sha:
        sys.exit(f"could not resolve a commit SHA for {model_id}@{revision}")
    return sha


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=DEFAULT_CFG)
    ap.add_argument("--revision", default="main", help="branch/tag/SHA to resolve (default: main)")
    args = ap.parse_args()

    text = args.config.read_text(encoding="utf-8")
    m_model = re.search(r"^model:\s*(\S+)\s*$", text, re.MULTILINE)
    if not m_model:
        sys.exit(f"no `model:` line in {args.config}")
    model_id = m_model.group(1)

    sha = resolve_sha(model_id, args.revision)
    new_text, n = re.subn(r"^(revision:\s*)(\S+)(.*)$",
                          rf"\g<1>{sha}\g<3>", text, count=1, flags=re.MULTILINE)
    if n != 1:
        sys.exit(f"no `revision:` line to update in {args.config}")
    args.config.write_text(new_text, encoding="utf-8")
    print(f"pinned {model_id} -> {sha}\nwrote {args.config.relative_to(ROOT)}")
    print("Now: git add the config and commit it before running any phase.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
